from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from datetime import datetime
import time
import csv
import re


# ============================================================
# CONFIG
# ============================================================

JOB_KEYWORD = "virtual assistant jobs in usa remote"

COUNTRIES = [
    "Usa",
    
]

DATE_POSTED = "24h"
EXPERIENCE_LEVELS = ["2"]
WORKPLACE_TYPES = ["2", "3"]


# DATE_POSTED codes:
# "any"   = Any time
# "24h"   = Past 24 hours
# "week"  = Past week
# "month" = Past month

# EXPERIENCE_LEVELS codes:
# []   = All levels
# ["1"] = Internship
# ["2"] = Entry level
# ["3"] = Associate
# ["4"] = Mid-Senior level
# ["5"] = Director
# ["6"] = Executive

# WORKPLACE_TYPES codes:
# []   = All types
# ["1"] = On-site
# ["2"] = Remote
# ["3"] = Hybrid


# ============================================================
# LEAD SHEET CONSTANTS
# ============================================================

SOURCE_ID = "SRC-LD001"
SOURCE_NAME = "LinkedIn Jobs"
JOB_STATUS = "Active"

# Date Found is the date your scraper collected the record.
DATE_FOUND = datetime.now().strftime("%Y-%m-%d")


# ============================================================
# SCRAPING CONFIG
# ============================================================

MAX_SCROLL_ATTEMPTS = 200
SCROLL_PAUSE = 5
DETAIL_PAUSE = 2


# ============================================================
# ROLE CATEGORY RULES
# ============================================================

ROLE_CATEGORY_RULES = [
    (
        "Virtual Assistant",
        [
            "virtual assistant",
            "executive assistant",
            "personal assistant",
            "administrative assistant",
            "admin assistant",
        ],
    ),
    (
        "Data Entry",
        [
            "data entry",
            "data entry clerk",
            "data entry specialist",
            "data entry associate",
            "data entry operator",
        ],
    ),
    (
        "Scheduling & Coordination",
        [
            "scheduling",
            "scheduler",
            "coordinator",
            "coordination",
            "booking support",
            "travel coordinator",
        ],
    ),
    (
        "Sales Support",
        [
            "sales support",
            "sales admin",
            "sales assistant",
            "sales coordinator",
            "sales operations",
        ],
    ),
    (
        "Customer Support",
        [
            "customer support",
            "customer service",
            "support representative",
            "client support",
        ],
    ),
    (
        "Operations",
        [
            "operations",
            "operations assistant",
            "operations associate",
            "operations specialist",
            "office operations",
        ],
    ),
    (
        "Administrative Support",
        [
            "administrative",
            "office assistant",
            "office administrator",
            "executive assistant",
        ],
    ),
]


# ============================================================
# SAFE FILENAMES
# ============================================================

safe_keyword = JOB_KEYWORD.replace(" ", "_")

safe_exp = (
    ",".join(EXPERIENCE_LEVELS).replace(",", "_")
    if EXPERIENCE_LEVELS
    else "all"
)

safe_workplace = (
    ",".join(WORKPLACE_TYPES).replace(",", "_")
    if WORKPLACE_TYPES
    else "all"
)

safe_date = DATE_POSTED


# ============================================================
# SETUP CHROME
# ============================================================

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)


# ============================================================
# BUILD LINKEDIN JOB SEARCH URL
# ============================================================

def build_linkedin_url(
    keyword,
    location,
    exp_levels,
    workplace_types,
    date_posted
):
    exp_param = ",".join(exp_levels) if exp_levels else ""

    workplace_param = (
        ",".join(workplace_types)
        if workplace_types
        else ""
    )

    date_param = ""

    if date_posted == "24h":
        date_param = "r86400"

    elif date_posted == "week":
        date_param = "r604800"

    elif date_posted == "month":
        date_param = "r2592000"

    url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote_plus(keyword)}"
        f"&location={quote_plus(location)}"
    )

    if exp_param:
        url += f"&f_E={exp_param}"

    if workplace_param:
        url += f"&f_WT={workplace_param}"

    if date_param:
        url += f"&f_TPR={date_param}"

    url += "&position=1&pageNum=0"

    return url


# ============================================================
# SCROLL PAGE
# ============================================================

def scroll_page(driver):
    attempt = 0

    last_height = driver.execute_script(
        "return document.body.scrollHeight"
    )

    while attempt < MAX_SCROLL_ATTEMPTS:

        print(f"Scrolling... attempt {attempt + 1}")

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(SCROLL_PAUSE)

        try:
            show_more_btn = WebDriverWait(
                driver,
                5
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        "infinite-scroller__show-more-button"
                    )
                )
            )

            print("Clicking 'Show more jobs'...")
            driver.execute_script(
                "arguments[0].click();",
                show_more_btn
            )

            time.sleep(SCROLL_PAUSE)

        except Exception:
            pass

        new_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        if new_height == last_height:
            print("No more content loaded.")
            break

        last_height = new_height
        attempt += 1


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def first_non_empty(*values):
    for value in values:
        value = clean_text(value)
        if value:
            return value
    return ""


def extract_posted_time(card):
    """
    Robust LinkedIn job-card posting-time extraction.

    Handles visible values such as:
      19 hours ago
      17 hours ago
      2 days ago
      8 hours ago
      Just now
    """
    posted_tag = card.find("time")

    if posted_tag:
        visible_text = clean_text(
            posted_tag.get_text(" ", strip=True)
        )
        if visible_text:
            return visible_text

        datetime_value = clean_text(
            posted_tag.get("datetime", "")
        )
        if datetime_value:
            return datetime_value

    card_text = clean_text(
        card.get_text(" ", strip=True)
    )

    match = re.search(
        r"\b(?:just now|\d+\s+(?:minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)\s+ago)\b",
        card_text,
        flags=re.I,
    )

    if match:
        return match.group(0)

    return "Not mentioned"


def detect_work_arrangement(text):
    """
    Attempts to map the job into:
    Remote / Hybrid / On-site / Not mentioned
    """
    text = clean_text(text).lower()

    if "hybrid" in text:
        return "Hybrid"

    if "remote" in text:
        return "Remote"

    if "on-site" in text or "onsite" in text or "on site" in text:
        return "On-site"

    return "Not mentioned"


def extract_salary(card, detail_soup=None):
    """
    Tries several salary selectors and text patterns.
    Falls back to 'Not mentioned' exactly as used in the target sheet.
    """
    selectors = [
        "span.job-search-card__salary-info",
        "div.job-search-card__salary-info",
        ".job-search-card__salary-info",
        ".salary",
    ]

    for selector in selectors:
        element = card.select_one(selector)
        if element:
            salary = clean_text(element.get_text(" ", strip=True))
            if salary:
                return salary

    if detail_soup:
        detail_selectors = [
            ".salary",
            ".job-details-jobs-unified-top-card__job-insight",
            ".job-details-jobs-unified-top-card__job-insight-item",
        ]

        for selector in detail_selectors:
            for element in detail_soup.select(selector):
                text = clean_text(element.get_text(" ", strip=True))
                if "$" in text or "£" in text or "€" in text:
                    return text

        detail_text = clean_text(detail_soup.get_text(" ", strip=True))
        salary_match = re.search(
            r"(\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?"
            r"(?:\s*/\s*(?:hr|hour|month|yr|year))?)",
            detail_text,
            flags=re.I,
        )

        if salary_match:
            return salary_match.group(1)

    return "Not mentioned"


def detect_role_category(job_title, job_description=""):
    """
    Maps the job title/description into the target sheet's Role Category.
    Uses title first, then description.
    """
    title = clean_text(job_title).lower()
    description = clean_text(job_description).lower()

    for category, keywords in ROLE_CATEGORY_RULES:
        if any(keyword in title for keyword in keywords):
            return category

    for category, keywords in ROLE_CATEGORY_RULES:
        if any(keyword in description for keyword in keywords):
            return category

    return "Other"


def detect_hiring_signal(
    job_title,
    company_name,
    posted,
    job_description="",
):
    """
    Heuristic classification for the target sheet.

    This is not a LinkedIn-native field. It is intentionally derived
    from observable job data so you can tune it later to match the
    client's exact sales logic.
    """
    text = " ".join(
        [
            clean_text(job_title),
            clean_text(company_name),
            clean_text(posted),
            clean_text(job_description),
        ]
    ).lower()

    if any(
        phrase in text
        for phrase in [
            "actively hiring",
            "we are hiring",
            "urgent hire",
            "immediate start",
            "hiring now",
        ]
    ):
        return "Actively hiring"

    if any(
        phrase in text
        for phrase in [
            "multiple openings",
            "multiple positions",
            "several openings",
            "rapidly growing",
            "growing team",
            "repeat hiring",
        ]
    ):
        return "Repeat hiring"

    return "New hiring signal"


# ============================================================
# FETCH JOB DETAILS
# ============================================================

def fetch_job_details(job_url):
    job_desc = ""
    company_desc = ""
    work_arrangement = "Not mentioned"
    salary = "Not mentioned"

    if not job_url:
        return (
            job_desc,
            company_desc,
            work_arrangement,
            salary,
        )

    try:
        driver.get(job_url)

        time.sleep(DETAIL_PAUSE)

        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "body"
                )
            )
        )

        job_soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        # Job description
        job_div = job_soup.find(
            "div",
            class_="description__text"
        )

        if job_div:
            job_desc = job_div.get_text(
                separator="\n",
                strip=True
            )

        # Company description
        company_div = job_soup.find(
            "div",
            class_="show-more-less-html__markup"
        )

        if company_div:
            company_desc = company_div.get_text(
                separator="\n",
                strip=True
            )

        # Work arrangement from the entire visible job page.
        detail_text = clean_text(
            job_soup.get_text(" ", strip=True)
        )
        work_arrangement = detect_work_arrangement(
            detail_text
        )

        # Salary from detail page when available.
        salary = extract_salary(
            BeautifulSoup("", "html.parser"),
            detail_soup=job_soup,
        )

    except Exception as e:
        print(
            f"⚠️ Failed to fetch job detail: {e}"
        )

    return (
        job_desc,
        company_desc,
        work_arrangement,
        salary,
    )


# ============================================================
# MAIN SCRAPING LOOP
# ============================================================

all_jobs = []
seen_job_urls = set()

try:

    for country in COUNTRIES:

        print()
        print("=" * 60)
        print(f"Scraping LinkedIn Jobs for: {country}")
        print("=" * 60)

        url = build_linkedin_url(
            JOB_KEYWORD,
            country,
            EXPERIENCE_LEVELS,
            WORKPLACE_TYPES,
            DATE_POSTED
        )

        print(f"🔗 URL: {url}")

        driver.get(url)

        time.sleep(3)

        # Scroll/load jobs
        scroll_page(driver)

        # Get final HTML
        html = driver.page_source

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Find job cards
        job_cards = soup.find_all(
            "div",
            class_="base-card"
        )

        print(
            f"📊 Found {len(job_cards)} job cards "
            f"for {country}"
        )

        # Process jobs
        for idx, card in enumerate(job_cards):

            a_tag = card.find(
                "a",
                class_="base-card__full-link"
            )

            job_url = (
                a_tag["href"].strip()
                if a_tag and a_tag.get("href")
                else ""
            )

            # Normalize LinkedIn tracking/query parameters.
            if job_url:
                job_url = job_url.split("?")[0].strip()

            # Deduplicate across countries/searches.
            if job_url and job_url in seen_job_urls:
                print(
                    f"⏭️ Duplicate skipped: {job_url}"
                )
                continue

            if job_url:
                seen_job_urls.add(job_url)

            # Job title
            job_title = ""

            if a_tag:
                title_span = a_tag.find(
                    "span",
                    class_="sr-only"
                )

                if title_span:
                    job_title = title_span.get_text(
                        strip=True
                    )

            # Company
            company_tag = card.find(
                "h4",
                class_="base-search-card__subtitle"
            )

            company_a = (
                company_tag.find("a")
                if company_tag
                else None
            )

            company_name = (
                company_a.get_text(strip=True)
                if company_a
                else ""
            )

            # Location
            location_tag = card.find(
                "span",
                class_="job-search-card__location"
            )

            location = (
                location_tag.get_text(strip=True)
                if location_tag
                else ""
            )

            # Posted date
            posted = extract_posted_time(card)

            # Work arrangement from card first.
            card_text = clean_text(
                card.get_text(" ", strip=True)
            )
            work_arrangement = detect_work_arrangement(
                card_text
            )

            # Salary from card first.
            salary = extract_salary(card)

            print(
                f"🔍 ({idx + 1}/{len(job_cards)}) "
                f"Fetching: {job_title}"
            )

            # Fetch detail page
            (
                job_description,
                company_description,
                detail_work_arrangement,
                detail_salary,
            ) = fetch_job_details(job_url)

            # Prefer detail-page values when present.
            if detail_work_arrangement != "Not mentioned":
                work_arrangement = detail_work_arrangement

            if detail_salary != "Not mentioned":
                salary = detail_salary

            # Role category
            role_category = detect_role_category(
                job_title,
                job_description
            )

            # Hiring signal
            hiring_signal = detect_hiring_signal(
                job_title,
                company_name,
                posted,
                job_description
            )

            # Store in EXACT target-sheet column order.
            all_jobs.append(
                {
                    "Job Title": job_title,
                    "Company Name": company_name,
                    "Source ID": SOURCE_ID,
                    "Source Name": SOURCE_NAME,
                    "Job URL": job_url,
                    "Location": location,
                    "Work Arrangement": work_arrangement,
                    "Salary Mentioned": salary,
                    "Role Category": role_category,
                    "Date Posted": posted,
                    "Date Found": DATE_FOUND,
                    "Job Status": JOB_STATUS,
                    "Hiring Signal": hiring_signal,
                }
            )


    # ========================================================
    # SAVE TO CSV
    # ========================================================

    if all_jobs:

        fieldnames = [
            "Job Title",
            "Company Name",
            "Source ID",
            "Source Name",
            "Job URL",
            "Location",
            "Work Arrangement",
            "Salary Mentioned",
            "Role Category",
            "Date Posted",
            "Date Found",
            "Job Status",
            "Hiring Signal",
        ]

        csv_file = (
            f"linkedin_leads_"
            f"{safe_keyword}_"
            f"{'_'.join(c.replace(' ', '') for c in COUNTRIES)}_"
            f"{safe_exp}_"
            f"{safe_workplace}_"
            f"{safe_date}.csv"
        )

        with open(
            csv_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(all_jobs)

        print()
        print("=" * 60)
        print("✅ SCRAPING COMPLETED")
        print("=" * 60)

        print(f"📁 Saved {len(all_jobs)} leads")
        print(f"📄 CSV: {csv_file}")

    else:

        print()
        print("⚠️ No jobs extracted.")

finally:

    driver.quit()
    print("🔒 Browser closed.")