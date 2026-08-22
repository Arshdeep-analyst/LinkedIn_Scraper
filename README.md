LinkedIn Lead Automation

A Selenium + BeautifulSoup based LinkedIn job scraper built to automate a manual sales lead-generation workflow.

Overview

This project automates a sales-operations workflow where relevant LinkedIn job postings were manually searched, collected in batches, opened individually, and organized into a lead-tracking dataset.

The scraper can:

Build LinkedIn job searches dynamically

Search across multiple locations

Filter by date posted, experience level, and workplace type

Automatically scroll and load more jobs

Extract job and company information

Open individual job pages for additional details

Extract work arrangement and salary information when available

Categorize roles

Generate a hiring signal

Deduplicate jobs by Job URL

Export structured lead data to CSV

Output

The CSV follows the client's lead-data structure:

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

Tech Stack

Python

Selenium

BeautifulSoup4

UV

CSV

Project Structure

LinkedIn_Scraper/
├── linkedin_leads.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── requirements.txt
├── README.md
├── SETUP.md
└── .gitignore

Status

🚧 The project is currently functional and under development. Further improvements will focus on reliability, error handling, classification accuracy, and production readiness.

See SETUP.md for installation and execution instructions.

Responsible Use

Use the scraper responsibly and in accordance with LinkedIn's terms, applicable laws, and the permissions or requirements applicable to your use of the data.