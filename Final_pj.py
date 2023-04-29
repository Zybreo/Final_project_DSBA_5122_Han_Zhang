import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.express as px
import base64
from PIL import Image

st.set_page_config(layout="wide")

data = pd.read_csv('new_data2.csv')
df = pd.DataFrame(data)

df['State'] = df['State'].astype(str)
df['City'] = df['City'].astype(str)

# Create a header
st.title("🚗 EV Station Data Visualization")

# Initialize the session state
if "show_data" not in st.session_state:
    st.session_state.show_data = False

# Add this code to display an image
image_path = "ev_01.jpeg"
st.image(image_path, use_column_width=True)

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Replace these with your local image paths
image_path1 = "ev_021.jpeg"
image_path2 = "ev_022.jpeg"
image_path3 = "ev_023.jpeg"

image_base64_1 = image_to_base64(image_path1)
image_base64_2 = image_to_base64(image_path2)
image_base64_3 = image_to_base64(image_path3)

# Add this code to display three images side by side with hover effect
st.markdown(f"""
<style>
    .image-container {{
        display: flex;
        justify-content: center;
    }}
    .image-box {{
        margin: 0 10px;
        transition: 0.3s;
    }}
    .image-container:hover .image-box {{
        opacity: 0.5;
    }}
    .image-box:hover {{
        opacity: 1 !important;
    }}
    .image-box img {{
        width: 100%;
        height: auto;
    }}
    .button-container {{
        padding-top: 10px;
    }}
</style>
<div class="image-container">
    <div class="image-box">
        <img src="data:image/jpeg;base64,{image_base64_1}" alt="Image 1" />
    </div>
    <div class="image-box">
        <img src="data:image/jpeg;base64,{image_base64_2}" alt="Image 2" />
    </div>
    <div class="image-box">
        <img src="data:image/jpeg;base64,{image_base64_3}" alt="Image 3" />
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="button-container">', unsafe_allow_html=True)
if st.button("Click to see the Dataset", key="dataset_button"):
    st.session_state.show_data = not st.session_state.show_data
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_data:
    st.write("Below is the dataset of electric vehicle charging stations in the US.")
    st.write(df)

# Add a filter for power type
power_type_options = ['Select', 'Both', 'Level 2 EVSE', 'DC Fast']
power_type = st.sidebar.selectbox("Levels of EV Charging", power_type_options)


# Sidebar
st.sidebar.header("Filters")

# Sort states and cities alphabetically
sorted_states = ['Select'] + sorted(df["State"].unique())
selected_state = st.sidebar.selectbox("Choose a State", sorted_states)

if selected_state != 'Select':
    sorted_cities = ['Select'] + sorted(df[df["State"] == selected_state]["City"].unique())
    selected_city = st.sidebar.selectbox("Choose City", sorted_cities)
else:
    selected_city = 'Select'


# Filter the DataFrame based on the selected state and city
if selected_state != 'Select' and selected_city != 'Select':
    filtered_df = df[(df["State"] == selected_state) & (df["City"] == selected_city)]
else:
    filtered_df = pd.DataFrame()


# Simplify EV Pricing to 'free' or 'other'
df['EV Pricing'] = df['EV Pricing'].apply(lambda x: 'free' if x == 'free' else 'other')


# Add more filters in the sidebar
min_access_days_time = int(df['Access Days Time2'].min())
max_access_days_time = int(df['Access Days Time2'].max())
min_time, max_time = st.sidebar.slider("Access Days Time Range", min_access_days_time, max_access_days_time, (min_access_days_time, max_access_days_time))
unique_pricing = sorted(df['EV Pricing'].unique())
selected_pricing = st.sidebar.multiselect("EV Pricing", unique_pricing, unique_pricing)

# Apply new filters
filtered_df2 = df[(df['State'] == selected_state) &
                 (df['City'] == selected_city) &
                 (df['Access Days Time2'] >= min_time) &
                 (df['Access Days Time2'] <= max_time) &
                 (df['EV Pricing'].isin(selected_pricing))]

# Create a bar plot for access days time and EV pricing for different places
fig2 = px.bar(filtered_df2, x='Station Name', y='Access Days Time2', color='EV Pricing',
              title='Access Days Time and EV Pricing for Distribution Comparison',
              hover_data=['City', 'Facility Type'])
fig2.update_layout(
    autosize=True,
    width=800,  
    height=550,  
)


# Apply filters common to both figures
common_filtered_df = df[(df['State'] == selected_state) &
                        (df['City'] == selected_city) &
                        (df['Access Days Time2'] >= min_time) &
                        (df['Access Days Time2'] <= max_time) &
                        (df['EV Pricing'].isin(selected_pricing))]

# Apply power type filter only for fig1
if power_type == "Level 2 EVSE":
    fig1_filtered_df = common_filtered_df[common_filtered_df['EV Level2 EVSE Num'] > 0]
elif power_type == "DC Fast":
    fig1_filtered_df = common_filtered_df[common_filtered_df['EV DC Fast Count'] > 0]
elif power_type == "Both":
    fig1_filtered_df = common_filtered_df
else:
    fig1_filtered_df = pd.DataFrame()

# Create the scatter plot (fig1) using fig1_filtered_df
if not fig1_filtered_df.empty:
    fig1_filtered_df['EV Level2 EVSE Num'] = fig1_filtered_df['EV Level2 EVSE Num'].fillna(0)

    fig1 = px.scatter_mapbox(fig1_filtered_df,
                             title='Map of EV stations in the US',
                             lat="Latitude",
                             lon="Longitude",
                             color="Facility Type",
                             size="EV Level2 EVSE Num",
                             hover_name="Station Name",
                             hover_data=["City", "State"],
                             zoom=8.5,
                             color_continuous_scale=px.colors.cyclical.IceFire,
                             mapbox_style="carto-positron")
    fig1.update_layout(
        autosize=True,
        width=900,  
        height=600,  
    )

    st.plotly_chart(fig1)


else:
    st.write("Please select charging type and state to display the map.")

# Use the common_filtered_df DataFrame for fig2
filtered_df2 = common_filtered_df

st.plotly_chart(fig2)

st.markdown(
    '<p style="text-align: center; font-size: 12px;"><a href="https://www.lifewire.com/ev-charging-levels-explained-5201716" target="_blank">Source: lifewire.com</a></p>',
    unsafe_allow_html=True,
)