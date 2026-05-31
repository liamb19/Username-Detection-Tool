# Username Detection Web Scraping Tool

A high-performance Open-Source Intelligence (OSINT) reconnaissance solution that automates target footprint analysis across the digital landscape. Developed as an academic capstone, this tool leverages a multi-library pipeline to cross-reference targets across 10+ major social media platforms, providing instantaneous intelligence gathering while strictly adhering to regulatory privacy constraints.

---

## Tech Stack & Hardware

**Backend Architecture:** Python (Advanced Automation Core)  
**Network & Scraping Engines:** requests (Synchronous HTTP Triage), BeautifulSoup4 (DOM Parsing), and Selenium WebDriver (Dynamic Javascript Rendering)  
**Web Interface Framework:** Flask (Micro-framework) utilizing native HTML5/CSS3 UI styling  
**Data Persistence Layer:** Secure CSV Export Engine mapped for penetration testing deliverables  

---

## System Architecture & Anti-Scraping Challenge

Standard web scrapers rely strictly on basic HTTP request pools to check endpoint existence. However, modern social media platforms implement diverse, complex anti-reconnaissance barriers. Modern endpoints often mask account statuses behind custom HTTP server redirects or dynamically generate account profile elements via client-side JavaScript execution.  

To circumvent these operational hurdles, this tool applies a platform-specific triage engine. The software executes custom regular expression (re) pattern matching against the raw page content rather than relying on status codes alone, safely identifying explicit indicators of existence (e.g., matching Snapchat profile indicators like snapcode-img) or lack thereof (e.g., catching text strings like "sorry, we couldn't find that page").


---

## Installation & Deployment Guide

Because this application relies on automated browser testing modules, deployment requires linking local runtime system variables to an active browser driver environment. Follow this verified terminal deployment pipeline instead.

### Environment & Driver Configuration
Before booting the local server, your operating system must have a compatible web browser driver to parse dynamic targets.  

- Ensure Google Chrome or Mozilla Firefox is installed on your local host system.
- Download the matching version of WebDriver (e.g., ChromeDriver for Chrome) and place it in an environment path directory.  
- Ensure your local machine runs Python 3.10 or higher.

### 2. Prepare the Workspace Environment
Clone this repository or download the source code release binaries.  

1. Open your system's Terminal or Windows PowerShell.  
2. Change directories into the root folder containing the application workspace:  

```powershell 
cd username_tool_project_folder
```

### 3. Clear Network Socket Locks
To prevent a local networking port binding crash (`OSError: [Errno 98] Address already in use`), ensure all development servers or micro-services running on local port `5000` (such as dangling Flask apps or local Docker processes) are terminated before executing.

### 4. Execute the Application Pipeline
Rather than dealing with complicated container configurations, install dependencies and launch the Flask server wrapper natively. Copy and paste the following automated sequence commands:

```bash
pip install -r requirements.txt
python app.py
```

### 5. Post-Launch Sequence & Kickstarting Runtime
1. Wait for the terminal to print Running on [http://127.0.0.1:5000](http://127.0.0.1:5000) followed by Debugger is active!.  
2. Open a modern web browser window and navigate directly to your local development server gateway at [http://127.0.0.1:5000](http://127.0.0.1:5000).  
3. Enter your target username into the centralized search interface query block and execute.  

### Rate Limiting & Optimisation
- The tracking reliability of this OSINT system depends completely on its operational stealth footprint.  
- Aggressive Scanning: Sending concurrent, unfiltered target inquiries causes target web servers to trigger rate limits, leading to temporary IP bans or forced 403 Forbidden states.  
- Ethical Adaptation: Incorporates automated rate-limiting mechanisms and customized User-Agent rotation parameters to match normal human web browser signatures, staying completely compliant with remote platforms' robots.txt specifications.  

### Challenges and Debugging Logs
1. Dynamic Component Failures (404 Content Masking)
Symptom: Sub-routines incorrectly flagged active usernames as available because platforms served a standard 200 OK wrapper page masking an internal error block.  
Resolution: Upgraded parsing logic to move past mere status code checks, introducing Python Regex (re.search) to inspect DOM elements for explicit profile indicators.  
2. Thread Contention & IP Rate Blocking
Symptom: Scanning 10+ platforms simultaneously triggered automatic bot countermeasures on high-security networks like LinkedIn and Instagram.  
Resolution: Implemented randomized request delay logic directly into the scraping loops, mimicking natural browser behaviors to maintain data integrity and compliance. 
3. Data Portability Faults
Symptom: Extracted data strings containing unexpected non-ASCII symbols corrupted final parsing arrays when writing output metrics.  
Resolution: Structured a robust CSV export handler utilizing UTF-8 character encoding and Privacy by Design controls, ensuring all saved target records avoid storage of unapproved personal data.  

