import streamlit as st
import pandas as pd
from astropy.io import fits
import io

def load_data(uploaded_file):
    try:
        # Check file type by extension and read accordingly
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'txt':
            try:
                # Try reading the .txt file assuming it's delimited by tabs or spaces
                df = pd.read_csv(uploaded_file, delimiter='\t')
            except Exception:
                # Fallback: treat it as a simple text file
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                df = pd.DataFrame([line.split() for line in content.splitlines()])
        elif file_type == 'fits':
            hdul = fits.open(uploaded_file)
            data = hdul[1].data
            df = pd.DataFrame(data)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
        return df

    except PermissionError:
        st.error("Permission denied. Please check the file's read permissions.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")
        return None

def display_data(df):
    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df)

def main():
    st.title("Exoplanet Data Upload and Processing")

    # File uploader widget with a broader list of file types
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt", "fits", "xlsx", "json", "xml", "pdf", "docx", "md"])

    if uploaded_file is not None:
        # Load data, attempting to read the file, handling permissions
        df = load_data(uploaded_file)

        if df is not None:
            display_data(df)

            # Optional: Check for a specific planet
            if st.checkbox("Check specific planet details"):
                planet_name = st.text_input("Enter the planet name:")
                if st.button("Search"):
                    if planet_name:
                        # Handle case where the uploaded file might not have 'Planet name' column
                        if 'Planet name' in df.columns:
                            result = df[df['Planet name'].str.contains(planet_name, case=False, na=False)]
                            if not result.empty:
                                st.write(result)
                            else:
                                st.write("Planet not found.")
                        else:
                            st.error("The file does not contain a 'Planet name' column.")
                    else:
                        st.write("Please enter a planet name.")

if __name__ == "__main__":
    main()
