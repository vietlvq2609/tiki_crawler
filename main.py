from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas
import re

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

driver.get("https://tiki.vn/")
driver.maximize_window()

searchInput = driver.find_element(By.XPATH, '//*[@id="main-header"]/div/div[1]/div[1]/div[2]/div/input') # find search element


searchInput.send_keys("giày đá bóng") # type product want to get data from


searchInput.send_keys(Keys.RETURN) # click ENTER 

sleep(5) # wait 5 second for filtering products


# get search-result products's link and store it into an array
productLinks = driver.find_elements(By.XPATH, '//a[contains(@class, "product-item")]')
productLinks = [link.get_attribute("href") for link in productLinks]


products_data = [] # initiate an empty array to store products data

amount_of_products = 10 # replace it with number of product you want to get data from


if productLinks:

    # loop for each link to get detail data of product
    for i in range(1, amount_of_products + 1):
        driver.get(productLinks[i]) # access to detail product link

        name = driver.find_element(By.XPATH, '//h1[@class="title"]').text # get product's name

        # get product's category
        category = re.search( r"<span>(.+?)</span>", driver.find_element( By.XPATH, '//*[@id="__next"]/div[1]/main/div[1]/div/div/a[2]').get_attribute("innerHTML")).group(1) 

        ###################### get product prices
        current_price = ""
        regular_price = ""

        left_html = driver.find_element(By.XPATH, '//div[contains(@class, "left")]').get_attribute("innerHTML")
        description = driver.find_element(By.XPATH,'//div[contains(@class, "ToggleContent__View-sc-1dbmfaw-0 wyACs")]').get_attribute("innerHTML")

        current_price_match_pattern1 = re.search(r'<div class="styles__Price-sc-6hj7z9-1 jgbWJA">(.+?) ₫</div>', left_html)
        current_price_match_pattern2 = re.search(r'<div class="product-price__current-price">(.+?) ₫</div>', left_html)
        
        if current_price_match_pattern1:
            current_price = current_price_match_pattern1.group(1)
            regular_price = current_price_match_pattern1.group(1)
        elif current_price_match_pattern2:
            current_price = current_price_match_pattern2.group(1)
            regular_price = current_price_match_pattern2.group(1)
        current_price = re.sub(r"\.", "", current_price)
        regular_price = re.sub(r"\.", "", regular_price)
        #####################################

        ################ get products image excluding video (dev is noob, so need time to complete this function)
        images = ""
        imagesEL = driver.find_elements(By.XPATH, '//a[contains(@data-view-id, "pdp_main_view_photo")]')

        for el in imagesEL:
            el.click()
            imageContainer = driver.find_element( By.XPATH, '//div[contains(@class, "thumbnail")]').get_attribute('innerHTML')
            if re.search(r'<picture class="webpimg-container">', imageContainer):
                images = images + re.search(r'src="([^"]+)"', imageContainer).group(1) + ", "

        products_data.append(
            {
                "ID": i,
                "Type": "simple",
                "SKU": "",
                "Name": name,
                "Published": 1,
                "Is featured?": 0,
                "Visibility in catalog": "visible",
                "Short description": "",
                "Description": description,
                "Date sale price start": "",
                "Date sale price ends": "",
                "Tax status": "taxable",
                "Tax class": "",
                "In stock?": 1,
                "Stock": "",
                "Low stock amount": "",
                "Backorders allowed?": 0,
                "Sold individually?": 0,
                "Weight (kg)": "",
                "Length (cm)": "",
                "Width (cm)": "",
                "Height (cm)": "",
                "Allow customer reviews?": 1,
                "Purchase note": "",
                "Sale price": current_price,
                "Regular price": regular_price,
                "Categories": category,
                "Tags": "",
                "Shipping class": "",
                "Images": images,
                "Download limit": "",
                "Download expiry days": "",
                "Parent": "",
                "Grouped products": "",
                "Upsells": "Cross-sells",
                "External URL": "",
                "Button text": "",
                "Position": 0,
                "Attribute 1 name": "",
                "Attribute 1 value(s)": "",
                "Attribute 1 visible": 0,
                "Attribute 1 global": 1,
                "Attribute 2 name": "",
                "Attribute 2 value(s)": "",
                "Attribute 2 visible": 0,
                "Attribute 2 global": 1,
            }
        )

        # ID	Type	SKU	Name	Published	Is featured?	Visibility in catalog	Short description	Description	Date sale price starts	Date sale price ends	Tax status	Tax class	In stock?	Stock	Low stock amount	Backorders allowed?	Sold individually?	Weight (kg)	Length (cm)	Width (cm)	Height (cm)	Allow customer reviews?	Purchase note	Sale price	Regular price	Categories	Tags	Shipping class	Images	Download limit	Download expiry days	Parent	Grouped products	Upsells	Cross-sells	External URL	Button text	Position	Attribute 1 name	Attribute 1 value(s)	Attribute 1 visible	Attribute 1 global	Attribute 2 name	Attribute 2 value(s)	Attribute 2 visible	Attribute 2 global	Attribute 3 name	Attribute 3 value(s)	Attribute 3 visible	Attribute 3 global	Attribute 4 name	Attribute 4 value(s)	Attribute 4 visible	Attribute 4 global
        sleep(2)
else:
    print("Please check your network availablity")
################
driver.close()

df = pandas.DataFrame(products_data)
df.to_csv("products_data.csv", index=True)
