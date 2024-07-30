import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Define the URLs and corresponding city names
urls = [
    # ('https://aqarmap.com.eg/en/for-sale/property-type/alexandria/', 'Alexandria'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/cairo/', 'Cairo'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/north-coast/', 'North Coast'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/ain-elsokhna/', 'Ain El Sokhna'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/sharqia/', 'Sharqia'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/dakahlia/', 'Dakahlia'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/red-sea/', 'Hurghada/Red Sea'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/damietta/', 'Damietta'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/gharbia/', 'Gharbia'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/port-said/', 'Port Said'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/ras-sidr/', 'Ras Sidr'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/monufia/', 'Monufia'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/marsa-matruh/', 'Marsa Matruh'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/ismailia/', 'Ismailia'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/suez/', 'Suez'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/beheira/', 'Beheira'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/asyut/', 'Asyut'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/el-fayoum/', 'El Fayoum'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/el-minia/', 'El Minya'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/sharm-el-sheikh/', 'Sharm El Sheikh'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/sohag/', 'Sohag'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/beni-suef/', 'Beni Seuf'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/kafr-el-sheikh/', 'Kafr El Sheikh'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/aswan/', 'Aswan'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/qina/', 'Qina'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/jnwb-syn/', 'South Sinai'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/north-sinai/', 'North Sinai'),
    # ('https://aqarmap.com.eg/en/for-sale/property-type/new-valley/', 'New Valley')
    # ('https://aqarmap.com.eg/en/for-sale/property-type/luxor/', 'Luxor')
]

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Load existing data if it exists
try:
    existing_df = pd.read_excel('egy_aqar.xlsx')
except FileNotFoundError:
    existing_df = pd.DataFrame(columns=['City', 'Price per m² for Apartments', 'Price per m² for Villas'])

# Container for new data
new_data = []

for url, city in urls:
    try:
        driver.get(url)
        
        # Adding delay to ensure page elements are loaded
        time.sleep(5)
        
        # Find the div containing the prices using XPath
        div_container = driver.find_element(By.XPATH, '//div[contains(@class, "legend-container")]')
        if div_container:
            # Find the ul element within this div
            ul_element = div_container.find_element(By.TAG_NAME, 'ul')
            if ul_element:
                # Find all li elements within this ul
                li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
                if len(li_elements) >= 2:
                    # Extract the strong elements from the first and second li
                    apartment_price_elem = li_elements[0].find_element(By.TAG_NAME, 'strong')
                    villa_price_elem = li_elements[1].find_element(By.TAG_NAME, 'strong')

                    # Extract and clean the prices
                    apartment_price = apartment_price_elem.text.strip().replace(' EGP', '') if apartment_price_elem else 'N/A'
                    villa_price = villa_price_elem.text.strip().replace(' EGP', '') if villa_price_elem else 'N/A'
                else:
                    apartment_price = 'N/A'
                    villa_price = 'N/A'
            else:
                apartment_price = 'N/A'
                villa_price = 'N/A'
        else:
            apartment_price = 'N/A'
            villa_price = 'N/A'

        # Append to new data list
        new_data.append({
            'City': city,
            'Price per m² for Apartments': apartment_price,
            'Price per m² for Villas': villa_price
        })

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# Close the WebDriver
driver.quit()

# Convert new data to DataFrame
new_df = pd.DataFrame(new_data)

# Combine existing and new data
combined_df = pd.concat([existing_df, new_df], ignore_index=True)

# Drop duplicates based on the 'City' column, keeping the last entry
combined_df.drop_duplicates(subset='City', keep='last', inplace=True)

# Save combined DataFrame to Excel file
combined_df.to_excel('egy_aqar.xlsx', index=False)
