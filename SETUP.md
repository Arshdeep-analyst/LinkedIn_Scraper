LinkedIn Lead Automation — Setup Guide

1. Prerequisites

Install:

Python 3.11+

Git

UV

Google Chrome

Verify:

python --version
git --version
uv --version

2. Clone the Repository

git clone https://github.com/Arshdeep-analyst/LinkedIn_Scraper.git
cd LinkedIn_Scraper

3. Create the Virtual Environment

uv venv

Activate it on Windows PowerShell:

.venv\Scripts\activate

4. Install Dependencies

Recommended: UV

Because this project contains pyproject.toml and uv.lock:

uv sync

Alternative: requirements.txt

If you want to use pip instead:

pip install -r requirements.txt

For this project, uv sync is the preferred approach.

5. Configure the Scraper

Open:

linkedin_leads.py

Edit the configuration:

JOB_KEYWORD = "virtual assistant jobs in usa remote"

COUNTRIES = [
    "Usa",
    "India",
]

DATE_POSTED = "24h"
EXPERIENCE_LEVELS = ["2"]
WORKPLACE_TYPES = ["2", "3"]

Date filters

"any"   = Any time
"24h"   = Past 24 hours
"week"  = Past week
"month" = Past month

Experience filters

[]      = All levels
["1"]   = Internship
["2"]   = Entry level
["3"]   = Associate
["4"]   = Mid-Senior level
["5"]   = Director
["6"]   = Executive

Workplace filters

[]      = All types
["1"]   = On-site
["2"]   = Remote
["3"]   = Hybrid

6. Run the Scraper

Recommended:

uv run linkedin_leads.py

If the virtual environment is activated, you can also use:

python linkedin_leads.py

Selenium will open Chrome and perform the scraping workflow.

7. LinkedIn Authentication

If LinkedIn requires authentication, complete the required authentication in the browser.

Do not save LinkedIn credentials, cookies, or session data inside the repository.

8. Scraping Workflow

Configuration
      ↓
Build LinkedIn Search URL
      ↓
Open Search Page
      ↓
Scroll / Load More Jobs
      ↓
Extract Job Cards
      ↓
Deduplicate Job URLs
      ↓
Open Individual Job
      ↓
Extract Additional Details
      ↓
Classify / Derive Lead Fields
      ↓
Save CSV

9. Output

A CSV file is generated in the project directory after a successful run.

The output contains:

Job Title
Company Name
Source ID
Source Name
Job URL
Location
Work Arrangement
Salary Mentioned
Role Category
Date Posted
Date Found
Job Status
Hiring Signal

Date Posted is designed to capture LinkedIn's relative values such as:

19 hours ago
17 hours ago
2 days ago
8 hours ago

10. Troubleshooting

No pyproject.toml found

Make sure you are inside the repository:

cd LinkedIn_Scraper
uv sync

Selenium cannot start Chrome

Make sure Google Chrome is installed and working.

Verify Selenium:

uv run python -c "import selenium; print(selenium.__version__)"

BeautifulSoup import error

Run:

uv sync

or:

pip install -r requirements.txt

No jobs are found

Check:

LinkedIn is accessible in Chrome

The keyword is valid

The location is correct

Filters are not overly restrictive

LinkedIn returned job cards

LinkedIn has not changed the relevant page structure

11. Development

After changing dependencies:

uv sync

Run:

uv run linkedin_leads.py

Check changes:

git status

Commit:

git add .
git commit -m "Update LinkedIn lead scraper"

Push:

git push

12. Files That Must Not Be Committed

Never commit:

.venv/
.env
*.csv
cookies
session data
credentials
private client data

Your .gitignore should exclude these files.

13. Project Status

The core LinkedIn lead-generation workflow is functional and under development.

Planned improvements include better reliability, retries, error handling, classification accuracy, and production deployment.