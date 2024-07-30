import pandas as pd

# Load the Excel file
rent_file_path = 'rent_bayut.xlsx'
df_rent = pd.read_excel(rent_file_path)

# Function to clean, shift data, and recalculate price per metre in district
def clean_data_and_recalculate(df):
    # Shift the fields where 'City' is 'N/A' and 'District' is 'Cairo'
    for index, row in df.iterrows():
        if pd.isna(row['City']) and row['District'] == 'Cairo':
            df.at[index, 'City'] = 'Cairo'
            df.at[index, 'District'] = row['Neighborhood']
            df.at[index, 'Neighborhood'] = None

    # Drop duplicates based on relevant columns
    df.drop_duplicates(subset=['City', 'District', 'Neighborhood', 'Price in EGP'], keep='first', inplace=True)

    # Recalculate the "Price per metre on property"
    df['Price per metre on property'] = df['Price in EGP'] / df['Area in ㎡']

    # Calculate average price per meter for each district
    district_avg_price = df.groupby('District')['Price per metre on property'].mean().reset_index()
    district_avg_price.columns = ['District', 'Price per metre in District']

    # Remove existing 'Price per metre in District' column to avoid conflicts
    if 'Price per metre in District' in df.columns:
        df = df.drop(columns=['Price per metre in District'])

    # Merge the recalculated prices back to the main dataframe
    df = df.merge(district_avg_price, on='District', how='left')

    # Reorder columns to place 'Price per metre in District' beside 'Price per metre on property'
    cols = df.columns.tolist()
    price_idx = cols.index('Price per metre on property')
    district_price_idx = cols.index('Price per metre in District')
    cols.insert(price_idx + 1, cols.pop(district_price_idx))
    df = df[cols]

    return df

# Apply the cleaning and recalculating function to the rent dataframe
df_rent_cleaned = clean_data_and_recalculate(df_rent)

# Save the cleaned dataframe to a new Excel file
cleaned_rent_file_path = 'rent_bayut.xlsx'
df_rent_cleaned.to_excel(cleaned_rent_file_path, index=False)

cleaned_rent_file_path
