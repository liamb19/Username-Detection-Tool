import requests
from flask import Flask, render_template, request, send_from_directory
import csv
import os
import re
import time
import random
import logging
from werkzeug.utils import secure_filename


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("username_checker.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

def get_random_headers():
    """Generate headers with a random user agent to avoid detection."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",  
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def validate_username(username):
    """Validate that the username is safe to use."""
    # Typical username restrictions
    if not re.match(r'^[a-zA-Z0-9_\.-]{1,30}$', username):
        return False
    return True

def handle_rate_limiting(response):
    """Handle rate limiting responses."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logger.warning(f"Rate limited. Waiting for {retry_after} seconds")
        time.sleep(retry_after)
        return True
    return False

def make_request(url, username):
    """Make a request with proper error handling and rate limiting."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Random delay to avoid rate limiting
            time.sleep(random.uniform(1.0, 3.0))
            
            headers = get_random_headers()
            logger.info(f"Requesting {url} with User-Agent: {headers['User-Agent'][:30]}...")
            
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            
            if handle_rate_limiting(response):
                retry_count += 1
                continue
                
            return response
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {url}. Retrying... ({retry_count+1}/{max_retries})")
            retry_count += 1
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
    
    logger.error(f"Max retries reached for {url}")
    return None

def check_username_availability(username):
    """Check username availability across multiple platforms."""
    if not validate_username(username):
        logger.warning(f"Invalid username format: {username}")
        return [("All Platforms", username, "Invalid Format - Use only letters, numbers, underscores, dots and dashes (max 30 chars)", "#")]
    
    sites = [
        {"name": "GitHub", "url": f"https://github.com/{username}", "check_function": check_github},
        {"name": "Twitter", "url": f"https://x.com/{username}", "check_function": check_twitter},
        {"name": "Instagram", "url": f"https://www.instagram.com/{username}/", "check_function": check_instagram},
        {"name": "Facebook", "url": f"https://www.facebook.com/{username}", "check_function": check_facebook},
        {"name": "LinkedIn", "url": f"https://www.linkedin.com/in/{username}", "check_function": check_linkedin},
        {"name": "TikTok", "url": f"https://www.tiktok.com/@{username}", "check_function": check_tiktok},
        {"name": "Pinterest", "url": f"https://www.pinterest.com/{username}/", "check_function": check_pinterest},
        {"name": "Snapchat", "url": f"https://www.snapchat.com/add/{username}", "check_function": check_snapchat},
        {"name": "Threads", "url": f"https://www.threads.net/@{username}", "check_function": check_threads},
        {"name": "Telegram", "url": f"https://t.me/{username}", "check_function": check_telegram},
    ]
    
    results = []
    
    for site in sites:
        logger.info(f"Checking {site['name']} for {username}")
        
        response = make_request(site["url"], username)
        
        if response is None:
            results.append((site["name"], username, "Error - Connection Failed", site["url"]))
            continue
            
        content = response.text.lower()
        final_url = response.url.lower()

        logger.info(f"Final URL: {final_url}")
        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Content snippet: {content[:200]}")

        try:
            status = site["check_function"](response, content, final_url, username)
            results.append((site["name"], username, status, site["url"]))
        except Exception as e:
            logger.error(f"Error checking {site['name']}: {str(e)}")
            results.append((site["name"], username, f"Error - {str(e)[:50]}", site["url"]))

    return results

# Site-specific checkers (enhanced)

def check_github(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
    
    # Check for GitHub's specific not found indicators
    not_found_patterns = [
        r"not found",
        r"doesn't exist",
        r"this username is not available"
    ]
    
    if any(re.search(pattern, content) for pattern in not_found_patterns):
        return "Available"
    
    # Look for profile indicators
    profile_indicators = [
        r'class="p-name"',
        r'class="p-nickname"',
        r'class="avatar-user"',
        f'"/{username}"'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Unavailable"

def check_twitter(response, content, final_url, username):
    not_found_patterns = [
        r"this account doesn['']t exist",
        r"page does not exist",
        r"hmm... this page doesn['']t exist",
        r"this profile doesn't exist",
        r"account suspended",
        r"doesn['']t exist"
    ]
    
    if any(re.search(pattern, content) for pattern in not_found_patterns):
        return "Available"
        
    if "/home" in final_url or "/search?" in final_url:
        return "Available"
        
    profile_indicators = [
        r'"screen_name":"\s*' + re.escape(username) + r'\s*"',
        f'@{username.lower()}',
        f'/{username.lower()}/photo',
        f'/{username.lower()}/header_photo'
    ]
    
    if not any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Available"
        
    return "Unknown Status" if response.status_code != 200 else "Unavailable"

def check_instagram(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"sorry, this page isn't available",
        r"page not found",
        r"page could not be found",
        r"this page is not available"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    if response.status_code == 200 and f"instagram.com/{username.lower()}/" in final_url:
        profile_indicators = [
            r'profile picture',
            r'profile photo', 
            r'og:title" content="[^"]+ \(@' + re.escape(username) + r'\)',
            r'followers.*following',
            r'following.*followers'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
            return "Unavailable"
            
    if response.status_code == 302 or "/accounts/login/" in final_url:
        return "Login Required (Likely Unavailable)"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_facebook(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"page not found",
        r"content isn't available",
        r"this page isn't available",
        r"this content isn't available right now"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    if "/login/" in final_url or "facebook.com/login" in final_url:
        return "Login Required (Likely Unavailable)"
        
    profile_indicators = [
        f'facebook.com/{username.lower()}',
        r'entity_id',
        r'profile_id',
        r'profile picture'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_linkedin(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"page not found",
        r"this page doesn't exist",
        r"we can't find this page",
        r"this profile doesn't exist"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    if "/authwall" in final_url or "linkedin.com/login" in final_url:
        return "Login Required (Unable to Check)"
        
    profile_indicators = [
        f'linkedin.com/in/{username.lower()}',
        r'profile-id',
        r'member-name',
        r'profile picture'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_tiktok(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"couldn't find this account",
        r"page not found",
        r"user not found",
        r"this account does not exist"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    profile_indicators = [
        f'@{username.lower()}',
        r'user-unique-id',
        r'uniqueid',
        r'user-profile',
        r'follower-count',
        r'following-count'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_pinterest(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"something went wrong",
        r"page not found",
        r"user not found",
        r"sorry, we couldn't find that page"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    if "/login/" in final_url or "pinterest.com/login" in final_url:
        return "Login Required (Likely Unavailable)"
        
    profile_indicators = [
        f'pinterest.com/{username.lower()}/',
        r'data-test-id="user"',
        r'username="' + re.escape(username) + r'"',
        r'follower',
        r'following'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_snapchat(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"cannot find the user",
        r"user not found",
        r"this page doesn't exist",
        r"sorry, we couldn't find that page"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
    
    profile_indicators = [
        r'snapcode-img',
        r'username="' + re.escape(username) + r'"',
        r'add-friend-button',
        r'profile-card',
        r'snapcode'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_threads(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"sorry, this page isn't available",
        r"page not found",
        r"user not found",
        r"this page could not be found"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
        
    profile_indicators = [
        f'threads.net/@{username.lower()}',
        r'profile picture',
        r'followers',
        r'profile-header'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

def check_telegram(response, content, final_url, username):
    if response.status_code == 404:
        return "Available"
        
    not_available_patterns = [
        r"nobody is using this username",
        r"this channel is empty",
        r"this channel doesn't exist",
        r"sorry, this page doesn't exist"
    ]
    
    if any(re.search(pattern, content) for pattern in not_available_patterns):
        return "Available"
    
    profile_indicators = [
        r'tgme_page_title',
        r'tgme_username_link',
        r'members',
        r'subscribers',
        r'channel-info'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) for pattern in profile_indicators):
        return "Unavailable"
        
    return "Unknown Status" if response.status_code != 200 else "Likely Available"

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        
        if not username:
            error = "Please enter a username"
        else:
            try:
                results = check_username_availability(username)
                if results:
                    save_results_to_csv(results)
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                error = f"An error occurred: {str(e)}"
                
    return render_template("index.html", results=results, error=error)

def save_results_to_csv(results):
    """Save results to a CSV file with a timestamp to avoid overwriting."""
    os.makedirs('static/results', exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f'username_results_{timestamp}.csv'
    filepath = os.path.join('static/results', filename)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Website", "Username", "Status", "Link"])
        writer.writerows(results)
        
    # Save the most recent filename for download
    with open(os.path.join('static', 'latest_results.txt'), 'w') as f:
        f.write(filename)
        
    return filename

@app.route("/download")
def download_file():
    try:
        # Get the latest results filename
        with open(os.path.join('static', 'latest_results.txt'), 'r') as f:
            filename = f.read().strip()
            
        return send_from_directory(
            directory='static/results', 
            path=filename, 
            as_attachment=True,
            download_name='username_results.csv'
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return "No results available for download", 404

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.errorhandler(413)
def request_entity_too_large(error):
    return "File too large", 413

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return "An internal server error occurred. Please try again later.", 500

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/results', exist_ok=True)
    
    # Create the log directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    app.run(debug=True)