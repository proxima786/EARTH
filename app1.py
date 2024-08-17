import streamlit as st
import pandas as pd
from astropy.io import fits
from astropy.table import Table
import numpy as np

def input_data():
    st.write("Please ensure your data follows this sequence of columns: ")
    st.write("Planet name, Host name, Orbital radius, Planet radius/diameter, Stellar radius, Diameter, Spectral type (optional), Effective temperature of star")

    # File uploader widget in Streamlit
    uploaded_file = st.file_uploader("Select your data file", type=["csv", "txt", "fits"])

    if not uploaded_file:
        st.warning("No file selected. Please try again.")
        return None

    # Determine the file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()

    # Load the data based on file type and convert to pandas DataFrame
    if file_extension == "csv":
        data = pd.read_csv(uploaded_file)
        st.success("CSV file loaded successfully.")
    elif file_extension == "txt":
        data_table = Table.read(uploaded_file, format="ascii")
        data = data_table.to_pandas()
        st.success("TXT file loaded and converted to pandas DataFrame successfully.")
    elif file_extension == "fits":
        hdul = fits.open(uploaded_file)
        data_table = hdul[1].data  # Assuming the data is in the second HDU
        data = pd.DataFrame(np.array(data_table).byteswap().newbyteorder())
        st.success("FITS file loaded and converted to pandas DataFrame successfully.")
    else:
        st.error("Unsupported file format. Please upload a .csv, .txt, or .fits file.")
        return None

    return data

def process_data(data, min_teff, max_teff):
    expected_columns = 7  # Minimum number of expected columns
    if data.shape[1] < expected_columns:
        st.error(f"Error: Expected at least {expected_columns} columns, but got {data.shape[1]}. Please check your data format.")
        return None

    # Convert columns to appropriate numeric types using column indices
    data.iloc[:, 2] = pd.to_numeric(data.iloc[:, 2], errors='coerce')  # Orbital radius
    data.iloc[:, 3] = pd.to_numeric(data.iloc[:, 3], errors='coerce')  # Planet radius/diameter
    data.iloc[:, 4] = pd.to_numeric(data.iloc[:, 4], errors='coerce')  # Stellar radius
    data.iloc[:, 6] = pd.to_numeric(data.iloc[:, 6], errors='coerce')  # Effective temperature of star

    data.replace("--", np.nan, inplace=True)
    data.fillna(0, inplace=True)

    filtered_data = data[(data.iloc[:, 6] >= min_teff) & (data.iloc[:, 6] <= max_teff)].copy()

    filtered_data['st_rad/pl_rade'] = filtered_data.iloc[:, 4] / filtered_data.iloc[:, 3] * 109.7522  # Stellar radius / Planet radius
    filtered_data['pl_orbsmax/st_rad'] = filtered_data.iloc[:, 2] / filtered_data.iloc[:, 4] * 107.1428  # Orbital radius / Stellar radius

    filtered_data = filtered_data[(filtered_data.iloc[:, 3] != 0) & (filtered_data.iloc[:, 4] != 0) & (filtered_data.iloc[:, 2] != 0)]

    if st.checkbox("Would you like to see the processed data?"):
        st.dataframe(filtered_data)

    if st.checkbox("Would you like to check for a specific planet?"):
        planet_name = st.text_input("Please enter the planet name:")
        if planet_name:
            planet_data = filtered_data[filtered_data.iloc[:, 0] == planet_name]
            if not planet_data.empty:
                st.write("Details for the specified planet:")
                st.dataframe(planet_data)
            else:
                st.warning(f"No data found for planet '{planet_name}'.")

    if st.checkbox("Would you like to add additional planets?"):
        exoplanets = []
        while True:
            pl_name = st.text_input("Enter planet name:").strip()
            host_name = st.text_input("Enter host name:").strip()
            pl_orb_max = st.number_input("Enter orbital radius (in days):", value=0.0)
            D_p = st.number_input("Enter planet radius/diameter:", value=0.0)
            D_s = st.number_input("Enter stellar radius:", value=0.0)
            star_type = st.text_input("Enter spectral type (optional):").strip()
            T_eff = st.number_input("Enter effective temperature of star (in Kelvin):", value=0.0)

            exoplanets.append([pl_name, host_name, pl_orb_max, D_p, D_s, star_type, T_eff])

            if not st.checkbox("Add another planet?"):
                break

        exoplanet_columns = ["pl_name", "host_name", "pl_orbsmax", "pl_rade", "st_rad", "st_spectype", "st_teff"]
        new_planets_df = pd.DataFrame(exoplanets, columns=exoplanet_columns)

        new_planets_df['st_rad/pl_rade'] = new_planets_df['st_rad'] / new_planets_df['pl_rade'] * 109.7522
        new_planets_df['pl_orbsmax/st_rad'] = new_planets_df['pl_orbsmax'] / new_planets_df['st_rad'] * 107.1428

        new_planets_df['st_teff'] = pd.to_numeric(new_planets_df['st_teff'], errors='coerce')

        valid_new_planets = new_planets_df[(new_planets_df['st_teff'] >= min_teff) & (new_planets_df['st_teff'] <= max_teff)]
        if not valid_new_planets.empty:
            filtered_data = pd.concat([filtered_data, valid_new_planets], ignore_index=True)
            st.success("New planets added and processed.")
            if st.checkbox("Would you like to see the newly added planets?"):
                st.dataframe(valid_new_planets)
        else:
            st.warning("No new planets met the temperature criteria.")
            
    return filtered_data

# Streamlit app
st.title("EARTH - Exoplanet Assessment for Relative Terrestrial Habitability")

data = input_data()
if data is not None:
    min_value = st.number_input("Enter minimum stellar temperature (in Kelvin):", value=4000)
    max_value = st.number_input("Enter maximum stellar temperature (in Kelvin):", value=6000)
    
    processed_data = process_data(data, min_value, max_value)
