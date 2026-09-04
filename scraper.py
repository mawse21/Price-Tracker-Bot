from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from datetime import datetime

options = Options()

# Options to make the search faster and less consuming
options.add_argument("--disable-images")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.page_load_strategy = 'eager'


def get_noon_info(url):
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 5)
    driver.get(url)

    info = {}
    try:
        info["price"] = wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, '[data-qa="div-price-now"]')
    )
).text.strip()
        info["name"] = wait.until(
    EC.visibility_of_element_located(
        (By.TAG_NAME, "h1")
    )
).text.strip()
    except:
        info["price"] = None
        info["name"] = None
    info["store"] = "Noon"
    info["time"] = datetime.now()

    driver.quit()

    return info  

def get_jumia_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try: 
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"request failed{e}")
    
    info ={}
    try:
        info["price"] = soup.find(class_ = "-b -ubpt -tal -fs24 -prxs").text.strip()  # depends on site
        info["name"] = soup.find(class_ = "-fs20 -ptm -pbxs").text.strip() # depends on site
    except:
        info["price"] = None
        info["name"] = None
    info["store"] = "Jumia"
    info["time"] = datetime.now()
    return info
    
def get_info(url):
    if "jumia.com" in url:
        return get_jumia_info(url)
    elif "noon.com" in url:
        return get_noon_info(url)
    else:
        info = {"price": None}
        return info

def clean_price(price):
    updated_price = ""
    for c in price:
        if c.isnumeric() or c == ".":
            updated_price += c
    try: 
        updated_price = float(updated_price.strip())
    except:
        updated_price = None
    return updated_price