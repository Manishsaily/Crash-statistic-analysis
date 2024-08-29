import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

#title of the Streamlit app
st.title('Accident Analysis App')

# Define the CSV file path within the git repo
CSV_FILE = "Crash Statistics Victoria.csv"

# Function to read and process the CSV file
def read_csv(csv: str) -> pd.DataFrame:
    """Reads the CSV file and converts the ACCIDENT_DATE to datetime format."""
    try:
        data = pd.read_csv(csv)
        date_format = '%d/%m/%Y'
        data['ACCIDENT_DATE'] = pd.to_datetime(data['ACCIDENT_DATE'], format=date_format, errors='coerce')
        st.write('CSV file uploaded successfully!')
        return data
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

# Function to filter data based on user selections
def filter_data(data: pd.DataFrame) -> pd.DataFrame:
    """Filters the data based on user-selected year and accident type."""
    st.title("Crash Statistics Data Filtering")

    # Create a dropdown to select the year
    selected_year = st.selectbox("Select a Year", list(range(2013, 2020)))
    filtered_data = data[data['ACCIDENT_DATE'].dt.year == selected_year].copy()

    # Create a dropdown to select accident type
    accident_type = st.selectbox("Choose Accident Type", ("Collision", "Animal", "Pedestrian", "No Collision"))

    # Display filtered data based on the selected year
    if st.button(f"Show Data for {selected_year}"):
        selected_columns = ['OBJECTID', 'ACCIDENT_NO', 'ACCIDENT_STATUS', 'ACCIDENT_DATE', 'ACCIDENT_TIME', 'SEVERITY']
        st.dataframe(filtered_data[selected_columns])

    # Display data for the selected accident type
    display_data_for_accident_type(filtered_data, selected_year, accident_type)
    # Display accidents per hour
    display_accidents_per_hour(filtered_data, selected_year)
    # Display alcohol impacts
    display_alcohol_impacts(filtered_data, selected_year)
    # Display data per speed zone
    display_speed_zones(filtered_data, selected_year)

# Function to display data for a specific accident type
def display_data_for_accident_type(filtered_data: pd.DataFrame, selected_year: int, accident_type: str) -> None:
    """Displays data filtered by accident type."""
    if st.button(f"Show Data for Accident Type in {selected_year}"):
        filtered_data_type = filtered_data[filtered_data['ACCIDENT_TYPE'].str.contains(accident_type, case=False, na=False)]
        filtered_data_type['ACCIDENT_DATE'] = filtered_data_type['ACCIDENT_DATE'].dt.date
        selected_columns = ['OBJECTID', 'ACCIDENT_NO', 'ACCIDENT_TYPE', 'ACCIDENT_DATE', 'ACCIDENT_TIME', 'SEVERITY']
        st.dataframe(filtered_data_type[selected_columns])

# Function to display accidents per hour
def display_accidents_per_hour(filtered_data: pd.DataFrame, selected_year: int) -> None:
    """Displays a bar chart of accidents per hour."""
    if st.button("Accidents per Hour"):
        time_format = '%H.%M.%S'
        filtered_data['ACCIDENT_TIME'] = pd.to_datetime(filtered_data['ACCIDENT_TIME'], format=time_format, errors='coerce')
        filtered_data['hour'] = filtered_data['ACCIDENT_TIME'].dt.hour

        # Group data by hour and count accidents
        hourly_counts = filtered_data.groupby('hour')['ACCIDENT_TIME'].count()
        chart_data = pd.DataFrame({'Hour': hourly_counts.index, 'Accidents': hourly_counts.values})

        fig, ax = plt.subplots()
        ax.bar(chart_data['Hour'], chart_data['Accidents'], color='skyblue')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Accidents')
        ax.set_title(f'Hourly Accident Counts (24h) for {selected_year}')
        ax.set_xticks(range(24))
        st.pyplot(fig)

# Function to display the impact of alcohol on accidents
def display_alcohol_impacts(filtered_data: pd.DataFrame, selected_year: int) -> None:
    """Displays data and a pie chart for accidents involving alcohol."""
    if st.button("Alcohol Impacts"):
        alcohol_impact_data = filtered_data[filtered_data['ALCOHOLTIME'].str.lower() == 'yes'].copy()
        alcohol_impact_data['ACCIDENT_DATE'] = alcohol_impact_data['ACCIDENT_DATE'].dt.date

        selected_columns = ['OBJECTID', 'ACCIDENT_NO', 'ACCIDENT_TYPE', 'ACCIDENT_DATE', 'SEVERITY']
        st.dataframe(alcohol_impact_data[selected_columns])

        # Count accidents with and without alcohol impact
        alcohol_impact_count = alcohol_impact_data.shape[0]
        non_alcohol_impact_count = filtered_data[filtered_data['ALCOHOLTIME'].str.lower() == 'no'].shape[0]

        # Create a pie chart
        labels = ['Accidents with Alcohol Impact', 'Accidents without Alcohol Impact']
        sizes = [alcohol_impact_count, non_alcohol_impact_count]
        colors = ['lightcoral', 'lightblue']
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        plt.title(f'Alcohol Impacts in {selected_year}')
        st.pyplot(fig)

# Function to display accident data per speed zone
def display_speed_zones(filtered_data: pd.DataFrame, selected_year: int) -> None:
    """Displays data on total accidents per speed zone for the selected year."""
    if st.button("Show Data per Speed Zone"):
        # Filter data by the selected year
        filtered_data = data[data['ACCIDENT_DATE'].dt.year == selected_year].copy()
        
        # Extract numeric values from SPEED_ZONE
        filtered_data['SPEED_ZONE'] = filtered_data['SPEED_ZONE'].str.extract('(\d+)').astype(float)

        # Count accidents per speed zone
        accident_counts = filtered_data['SPEED_ZONE'].value_counts().reset_index()
        accident_counts.columns = ['Speed Zone (Km/h)', 'Total Accidents']

        # Display the total accidents per speed zone
        st.write(f'Total Accidents per Speed Zone in {selected_year}:')
        st.dataframe(accident_counts)

        # Create a bar chart of total accidents per speed zone
        fig, ax = plt.subplots()
        ax.bar(accident_counts['Speed Zone (Km/h)'], accident_counts['Total Accidents'], color='orange')
        ax.set_xlabel('Speed Zone (Km/h)')
        ax.set_ylabel('Total Accidents')
        ax.set_title(f'Total Accidents per Speed Zone in {selected_year}')
        st.pyplot(fig)

# Main execution to read and process data
data = read_csv(CSV_FILE)
if not data.empty:
    filter_data(data)
else:
    st.error("No data available to display.")
