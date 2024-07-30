import streamlit as st
import pandas as pd
import openpyxl
import re
import plotly.graph_objects as go
import math

# Load the Excel files once at the start
EXCEL_FILE_PATH_CITY = 'egy_aqar.xlsx'
EXCEL_FILE_PATH_DISTRICT = 'district_prices.xlsx'
EXCEL_FILE_PATH_SALE = 'sale_bayut.xlsx'
EXCEL_FILE_PATH_RENT = 'rent_bayut.xlsx'

class App:
    def __init__(self):
        self.df_city = self.load_excel_data(EXCEL_FILE_PATH_CITY)
        self.df_district = self.load_excel_data(EXCEL_FILE_PATH_DISTRICT)
        self.df_sale = self.load_excel_data(EXCEL_FILE_PATH_SALE)
        self.df_rent = self.load_excel_data(EXCEL_FILE_PATH_RENT)
        self.run()

    def load_excel_data(self, file_path):
        return pd.read_excel(file_path)

    def run(self):
        st.title("Price per m² Selector")
        self.create_dropdown_menu()

    def create_dropdown_menu(self):
        options = ["Aqar Map", "Bayut"]
        selection = st.selectbox("Select a platform:", ["Choose a platform..."] + options)
        if selection == "Aqar Map":
            self.aqar_map()
        elif selection == "Bayut":
            self.bayut()

    def aqar_map(self):
        # Get unique cities from the city Excel data
        cities = self.df_city['City'].unique().tolist()
        
        # Select city
        city = st.selectbox("Select a city", ["Choose a city..."] + cities, index=0 if "Cairo" not in cities else cities.index("Cairo") + 1)
        
        if city and city != "Choose a city...":
            # Filter data for the selected city in the district Excel data
            city_district_data = self.df_district[self.df_district['City'] == city]
            districts = city_district_data['District'].unique().tolist() if not city_district_data.empty else []

            # If there are districts, allow selection of district
            if len(districts) > 0:
                district = st.selectbox("Select a district", ["Choose a district..."] + districts)
                
                if district and district != "Choose a district...":
                    # Generate button for city and district
                    if st.button("Generate"):
                        # Filter data for the selected district
                        district_data = city_district_data[city_district_data['District'] == district]
                        price_district = district_data['Price per meter'].values[0] if not district_data.empty else 'N/A'
                        st.write(f"Price per meter in {district}, {city}: {price_district}")

                        # Generate prices for city
                        city_data = self.df_city[self.df_city['City'] == city]
                        price_apartment = city_data['Price per m² for Apartments'].values[0] if not city_data.empty else 'N/A'
                        price_villa = city_data['Price per m² for Villas'].values[0] if not city_data.empty else 'N/A'
                        st.write(f"Price per meter for apartments in {city}: {price_apartment}")
                        st.write(f"Price per meter for villas in {city}: {price_villa}")

                        # Display Excel sheet
                        self.display_excel(EXCEL_FILE_PATH_DISTRICT, city, district)

                        # Display bar chart
                        self.plot_aqar_chart(city, price_apartment, price_villa, price_district, district)

            else:
                # Generate button for city only
                if st.button("Generate"):
                    city_data = self.df_city[self.df_city['City'] == city]
                    price_apartment = city_data['Price per m² for Apartments'].values[0] if not city_data.empty else 'N/A'
                    price_villa = city_data['Price per m² for Villas'].values[0] if not city_data.empty else 'N/A'
                    st.write(f"Price per meter for apartments in {city}: {price_apartment}")
                    st.write(f"Price per meter for villas in {city}: {price_villa}")

                    # Display Excel sheet
                    self.display_excel(EXCEL_FILE_PATH_CITY, city)

                    # Display bar chart
                    self.plot_aqar_chart(city, price_apartment, price_villa)

    def bayut(self):
        # Rent or Sale selection
        rent_or_sale = st.selectbox("Select Rent or Sale:", ["Choose an option..."] + ["Rent", "Sale"])
        
        if rent_or_sale and rent_or_sale != "Choose an option...":
            # Select city
            city = "Cairo"
            st.write(f"City: {city}")
            
            if rent_or_sale == "Sale":
                city_data = self.df_sale[self.df_sale['City'] == city]
            else:
                city_data = self.df_rent[self.df_rent['City'] == city]
            
            districts = city_data['District'].unique().tolist() if not city_data.empty else []
            
            if len(districts) > 0:
                district = st.selectbox("Select a district", ["Choose a district..."] + districts)
                
                if district and district != "Choose a district...":
                    # Generate button
                    if st.button("Generate"):
                        district_data = city_data[city_data['District'] == district]
                        price = district_data['Price per metre in District'].values[0] if not district_data.empty else 'N/A'
                        price = self.round_up(price) if price != 'N/A' else 'N/A'
                        st.write(f"Price per meter for {rent_or_sale.lower()} in {district}, {city}: {price}")

                        # Get the other type of price
                        if rent_or_sale == "Rent":
                            sale_data = self.df_sale[(self.df_sale['City'] == city) & (self.df_sale['District'] == district)]
                            sale_price = sale_data['Price per metre in District'].values[0] if not sale_data.empty else 'N/A'
                            sale_price = self.round_up(sale_price) if sale_price != 'N/A' else 'N/A'
                            # Display Excel sheet
                            self.display_excel(EXCEL_FILE_PATH_RENT, city, district)
                            # Display bar chart
                            self.plot_bayut_chart(sale_price, price, district, city)
                        else:
                            rent_data = self.df_rent[(self.df_rent['City'] == city) & (self.df_rent['District'] == district)]
                            rent_price = rent_data['Price per metre in District'].values[0] if not rent_data.empty else 'N/A'
                            rent_price = self.round_up(rent_price) if rent_price != 'N/A' else 'N/A'
                            # Display Excel sheet
                            self.display_excel(EXCEL_FILE_PATH_SALE, city, district)
                            # Display bar chart
                            self.plot_bayut_chart(price, rent_price, district, city)

    def display_excel(self, file_path, city, district=None):
        # Load the excel file
        df = pd.read_excel(file_path)
        st.write(df)

    def clean_price(self, price):
        # Remove any non-numeric characters except for the decimal point
        if price is None:
            return 0
        if isinstance(price, str):
            return float(re.sub(r'[^\d.]', '', price))
        return float(price)
    
    def round_up(self, price):
        # Round up to the nearest whole number
        return math.ceil(self.clean_price(price))

    def plot_aqar_chart(self, city, price_apartment, price_villa, price_district=None, district=None):
        # Prepare data for Plotly
        categories = ['Apartments', 'Villas']
        prices = [price_apartment, price_villa]
        if price_district:
            categories.append(district)
            prices.append(price_district)

        # Convert 'N/A' values to 0 for plotting and clean prices
        prices = [self.round_up(price) if price != 'N/A' else 0 for price in prices]
        
        # Create Plotly bar chart
        fig = go.Figure(data=[
            go.Bar(name='Prices', x=categories, y=prices, text=prices, textposition='auto')
        ])

        # Set y-axis ticks to fixed range
        max_price = max(prices)
        step = 5000
        rounded_max = (int(max_price) + step - 1) // step * step
        fig.update_layout(
            yaxis=dict(tickmode='linear', tick0=0, dtick=step, range=[0, rounded_max + step]),
            title=f'Price per meter in {city}' if not price_district else f'Price per meter in {city}',
            xaxis_title='Category',
            yaxis_title='Price per meter'
        )
        
        st.plotly_chart(fig)

    def plot_bayut_chart(self, sale_price, rent_price, district, city):
        # Prepare data for Plotly
        categories = [f'{district} - Sale', f'{district} - Rent'] if rent_price else [f'{district} - Sale']
        prices = [sale_price, rent_price] if rent_price else [sale_price]

        # Convert 'N/A' values to 0 for plotting and clean prices
        prices = [self.round_up(price) if price != 'N/A' else 0 for price in prices]
        
        # Create Plotly bar chart
        fig = go.Figure(data=[
            go.Bar(name='Prices', x=categories, y=prices, text=prices, textposition='auto')
        ])

        # Set y-axis ticks to fixed range
        max_price = max(prices)
        step = 10000
        rounded_max = (int(max_price) + step - 1) // step * step
        fig.update_layout(
            yaxis=dict(tickmode='linear', tick0=0, dtick=step, range=[0, rounded_max + step]),
            title=f'Price per meter in {district}, {city}',
            xaxis_title='Category',
            yaxis_title='Price per meter'
        )
        
        st.plotly_chart(fig)

if __name__ == "__main__":
    app = App()
