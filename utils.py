from goodreads_scraper.utils import setup_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.goodreads.com/author/show/13199.Alain_de_Botton"
browser = setup_browser()

browser.get(url)


body = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

born_label = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='dataTitle' and text()='Born']"))
)

birthplace = browser.execute_script(
    "return arguments[0].nextSibling.textContent.trim();", 
    born_label
)

print(birthplace)

#TODO: Encapsular, testar, lidar gracefully com caso em que o elemento não existe.
