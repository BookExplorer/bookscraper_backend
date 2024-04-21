from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from goodreads_scraper.utils import setup_browser
import re


def scrape_gr_author(url: str) -> str | None:
    """
    Scrapes the author's Goodreads page and extracts the author's birthplace.
    Args:
        url (str): The author's Goodreads URL, brought from the scraping of the user's page.

    Returns:
        str | None: Birthplace of the author or None if we can't find it in the authors page.
    """

    browser = setup_browser()

    browser.get(url)

    body = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    try:
        born_label = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='dataTitle' and text()='Born']")
            )
        )

        raw_birthplace = browser.execute_script(
            "return arguments[0].nextSibling.textContent.trim();", born_label
        )

        birthplace = re.sub(r"^in\s+", "", raw_birthplace)
    except TimeoutException:
        birthplace = None
    return birthplace


def cleanup_birthplace(birthplace: str | None) -> str | None:
    """Cleans up the birthplace string that comes from Goodreads.

    Args:
        birthplace (str | None): Birthplace scraped from Goodreads.

    Returns:
        str | None: Cleaned up birthplace if applicable, None if birthplace is None.
    """
    if birthplace:
        raw_country = birthplace.split(",")[-1].lstrip()
        if raw_country.startswith("The "):
            return raw_country[4:]
        return raw_country
