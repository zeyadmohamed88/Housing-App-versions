from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in your PATH

# Function to scrape data from a URL
def scrape_data(url, city_name):
    driver.get(url)
    time.sleep(5)  # Adjust the sleep time as needed

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all the listing-card elements
    listings = soup.find_all('div', class_='listing-card clearfix')

    # Prepare lists to store the extracted data
    districts = []
    prices = []
    cities = []

    # Extract district names and prices
    for listing in listings:
        district_tag = listing.find('p', class_='titleTag')
        price_tag = listing.find('span', class_='integer')

        if district_tag and price_tag:
            district = district_tag.text.strip()
            price = price_tag.text.strip()
            districts.append(district)
            prices.append(price)
            cities.append(city_name)

    return districts, prices, cities

# URLs and city names
urls = [
    {"url": "https://aqarmap.com.eg/en/neighborhood/cairo/", "city": "Cairo"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/alexandria/", "city": "Alexandria"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/north-coast/", "city": "North Coast"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/dakahlia/", "city": "Dakahlia"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/gharbia/", "city": "Gharbia"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/qalyubia/", "city": "Qalyubia"},
    {"url": "https://aqarmap.com.eg/en/neighborhood/ain-elsokhna/", "city": "Ain Elsokhna"},
    
]

# Collect data from all URLs
all_districts = []
all_prices = []
all_cities = []

for entry in urls:
    districts, prices, cities = scrape_data(entry["url"], entry["city"])
    all_districts.extend(districts)
    all_prices.extend(prices)
    all_cities.extend(cities)

# Create a DataFrame and remove duplicates
df = pd.DataFrame({
    'City': all_cities,
    'District': all_districts,
    'Price per meter': all_prices
})

# Remove duplicate rows based on City, District, and Price per meter
df = df.drop_duplicates()

# Save the DataFrame to an Excel file
df.to_excel('district_prices.xlsx', index=False)

# Close the WebDriver
driver.quit()
