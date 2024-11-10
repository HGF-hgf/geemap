import ee
import geemap.foliumap as geemap
import streamlit as st

# Initialize the Earth Engine library
ee.Authenticate()
ee.Initialize(project='qualified-glow-437914-i0')

# DATASET
elevation_asl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ele_asl')
gti = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/gti_LTAy_AvgDailyTotals')
opta = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/opta_LTAy_AvgDailyTotals')
pvout_ltam = ee.ImageCollection('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAm_AvgDailyTotals')
pvout_ltay = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAy_AvgDailyTotals')
temp_agl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/temp_2m_agl')
dif = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dif_LTAy_AvgDailyTotals")
dni = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dni_LTAy_AvgDailyTotals")
ghi = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ghi_LTAy_AvgDailyTotals")
esri_lulc10 = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS")

# Create a map
Map = geemap.Map()
palette_niccoli_linearl = ['#2B4BA1', '#4C74D9', '#7CEBA5', '#FFFF00', '#FFA500', '#FF4500', '#8B0000']

Map.addLayer(pvout_ltam.first(), {'min': 0.55, 'max': 7, 'palette': palette_niccoli_linearl}, 'PVOUT_LTAm')

Map.add_basemap('SATELLITE')

# Add layers to the map

# Streamlit UI
st.title('Interactive Solar Data Explorer')
st.sidebar.header('Map Controls')

# Check if coordinates are saved in session state, if not, set default values
if 'lat' not in st.session_state:
    st.session_state.lat = 0
if 'lon' not in st.session_state:
    st.session_state.lon = 0

# Input fields for Latitude and Longitude
lat = st.sidebar.text_input("Latitude", str(st.session_state.lat))
lon = st.sidebar.text_input("Longitude", str(st.session_state.lon))
def get_solar_data(lat, lon):
    point = ee.Geometry.Point(lon, lat)


    # Get GHI and DNI values at the specified point
    ghi_value = ghi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    )
    ghi_value = ghi_value.get('b1')
    # st.write results
    ghi_value = ghi_value.getInfo() if ghi_value is not None else "No GHI data"
    st.write(f"GHI at ({lat}, {lon}): {ghi_value} kWh/m²/day")

    dni_value = dni.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dni_value = dni_value.getInfo() if dni_value is not None else "No DNI data"
    st.write(f"DNI at ({lat}, {lon}): {dni_value} kWh/m²/day")

    # GTI (Global Tilted Irradiation)
    gti_value = gti.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    gti_value = gti_value.getInfo() if gti_value is not None else "No GTI data"
    st.write(f"GTI at ({lat}, {lon}): {gti_value} kWh/m²/day")

    # Optimum Tilt Angle
    opta_value = opta.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    opta_value = opta_value.getInfo() if opta_value is not None else "No Optimum Tilt Angle data"
    st.write(f"Optimum Tilt Angle at ({lat}, {lon}): {opta_value} degrees")

    # PV Output (Long-Term Annual Average)
    pvout_ltay_value = pvout_ltay.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    pvout_ltay_value = pvout_ltay_value.getInfo() if pvout_ltay_value is not None else "No PV Output (Annual) data"
    st.write(f"PV Output (Annual) at ({lat}, {lon}): {pvout_ltay_value} kWh/kWp/day")

    # Temperature at 2m Above Ground Level
    temp_agl_value = temp_agl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    temp_agl_value = temp_agl_value.getInfo() if temp_agl_value is not None else "No Temperature data"
    st.write(f"Temperature at 2m AGL at ({lat}, {lon}): {temp_agl_value} °C")

    # Elevation (Above Sea Level)
    elevation_value = elevation_asl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    elevation_value = elevation_value.getInfo() if elevation_value is not None else "No Elevation data"
    st.write(f"Elevation at ({lat}, {lon}): {elevation_value} meters")

    # Diffuse Horizontal Irradiation
    dif_value = dif.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dif_value = dif_value.getInfo() if dif_value is not None else "No Diffuse Irradiation data"
    st.write(f"Diffuse Horizontal Irradiation at ({lat}, {lon}): {dif_value} kWh/m²/day")
# Only update the session state when the user clicks the button
if st.sidebar.button('Go to Coordinates'):
    try:
        # Update session state with new latitude and longitude
        st.session_state.lat = float(lat)
        st.session_state.lon = float(lon)
        
        # Set map center
        Map.set_center(st.session_state.lon, st.session_state.lat, zoom=8)
        st.write(f"Map centered at Latitude: {st.session_state.lat}, Longitude: {st.session_state.lon}")
        
        point = ee.Geometry.Point(st.session_state.lon, st.session_state.lat)

        get_solar_data(st.session_state.lat, st.session_state.lon)

    except ValueError:
        st.error("Invalid latitude or longitude. Please enter valid numbers.")

# Display the map in Streamlit
st.markdown("### Solar Data Map")

Map.to_streamlit(width=800, height=600)
