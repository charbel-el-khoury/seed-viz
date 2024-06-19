import folium
from streamlit_folium import st_folium
import ee
import geemap.foliumap as geemap
import streamlit as st
import plotly.graph_objects as go
from google.oauth2 import service_account


# initialize the Earth Engine
# service_account_info = st.secrets["gee"]
# st.write(service_account_info)
# credentials = service_account.Credentials.from_service_account_info(service_account_info)
# ee.Initialize(credentials)


service_account_email = "seed-viz-runner-streamlit@ee-seed-zh.iam.gserviceaccount.com"
json = st.secrets["gee"]
email = json["client_email"]
key = json["private_key"]
credentials = ee.ServiceAccountCredentials(email=email, key_data=key)
ee.Initialize(credentials)
st.set_page_config(
    page_title="SEED Index Visualizer 3000",
    page_icon="✅",
    layout="wide",
)
image = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/ecosystem_connectivity_kernel").rename("Ecosystem Connectivity")
image2 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/ecosystem_function_kernel").rename("Ecosystem Function")
image3 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/ecosystem_structure_kernel").rename("Ecosystem Structure")
image4 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/genetic_animals_kernel").rename("Genetic Animals")
image5 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/genetic_microbes_kernel").rename("Genetic Microbes")
image6 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/genetic_plants_kernel").rename("Genetic Plants")
image8 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/species_animals_kernel").rename("Species Animals")
image9 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/species_microbes_kernel").rename("Species Microbes")
image10 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/species_plants_kernel").rename("Species Plants")
image7 = ee.Image("projects/ee-speckerfelix/assets/seed_pipeline_temporary/PIPELINE_RUNS/v1_2_0/FelixMacStudio/2024-05-29/18-10-00/output/seed_index_kernel").rename("Seed Index")

im_with_all_bands = ee.ImageCollection.toBands([image, image2, image3, image4, image5, image6, image7, image8, image9, image10])
bands = im_with_all_bands.bandNames().getInfo()

Map = geemap.Map()

Map.add_basemap('ROADMAP')
palette= ['red', 'yellow', 'green']
vis_params = {'min': 0, 'max': 1, 'palette': palette, "name": 'Seed Index'}
for band in bands:
    if band != '6_Seed Index':
        Map.addLayer(im_with_all_bands.select(band), vis_params, name=band)

Map.addLayer(im_with_all_bands.select('6_Seed Index'), vis_params, name='Seed Index')

# Display elements on the Streamlit app

st.title('SEED Index Visualizer')
col1, col2 = st.columns([4, 2])
with col1:
    with st.form(key='aa'):
        st.form_submit_button(label='Submit')
        map_data = st_folium(Map, width=1200, height=700)

    st.markdown("for complaints please contact: [Robert McElderry](https://picsum.photos/2000)")
    st.image('figs/ETH+CL Logo_white+yellow.png', width= 300)

    st.image("figs/AQJU2073.JPG", width=70)
    st.image('figs/restor.png', width=70)

with col2:

    def handle_click(lat, lon):
        point = ee.Geometry.Point([lon, lat])
        dataset = im_with_all_bands
        value = dataset.reduceRegion(ee.Reducer.mean(), point, 500).getInfo()
        return value

    
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.write(f"Latitude: {lat}, Longitude: {lon}")
        axes_values = handle_click(lat, lon)
        seed_index = axes_values["6_Seed Index"]

        axes_values = {k: v for k, v in axes_values.items() if k != "6_Seed Index"}
        k = list(axes_values.keys())
        k = [i.split('_')[1] for i in k]
        v = list(axes_values.values())
        # create a spyder chart

        # MAKE A FIGURE WITH DARK BACKGROUND


        fig = go.Figure() 

        for i in 0.25, 0.5, 0.75, 1:
            fig.add_trace(go.Scatterpolar(
                r=[i]*(len(k)+1),
                theta=k + [k[0]],
                name = None,
                marker=dict(color='black', opacity=0, size=0),
                line=dict(color='#606060', width=0.6),
            ))
        fig.add_trace(go.Scatterpolar(
            r=v + [v[0]],
            theta=k + [k[0]],
            fill='toself',
        ))
        # fig = px.line_polar(r=v, theta=k, line_close=True)
        # fig.update_traces(fill='toself')
        # fig.update_yaxes(visible=False)
        fig.update_layout(polar = dict(radialaxis = dict(showticklabels = False, visible=False)), template="plotly_dark", showlegend=False, autosize=True, width=1200, height=700,)



        # # add to the streamlit app
        st.plotly_chart(fig)
        col1, col2, col3 = st.columns([3,2, 3])

        # Place content in the center column
        with col1:
            st.write("")

        with col2:
            if seed_index != None:
                seed_index_str = f"{seed_index:.2f}/{1:.2f}"
                st.metric(label="Seed Index", value=seed_index_str, delta=f"{seed_index-1:.2f}", delta_color="off")

        with col3:
            st.write("")
