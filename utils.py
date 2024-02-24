from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from goodreads_scraper.utils import setup_browser
import re


def scrape_gr_author(url: str):
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


def cleanup_birthplace(birthplace: str):
    if birthplace:
        raw_country = birthplace.split(",")[-1].lstrip()
        if raw_country.startswith("The "):
            return raw_country[4:]
        return raw_country
