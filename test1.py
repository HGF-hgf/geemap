import ee
import geemap
import ipywidgets as widgets
import random
import string
import streamlit as st
from IPython.display import display
from ipyleaflet import Marker
from ipyleaflet import AwesomeIcon
from palettable.cmocean.sequential import Dense_7
from palettable.matplotlib import Plasma_7
from palettable.colorbrewer.diverging import Spectral_9
from palettable.cmocean.sequential import Solar_7

# Initialize the Earth Engine library
ee.Authenticate()
ee.Initialize(project='qualified-glow-437914-i0')

#DATASET
elevation_asl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ele_asl');
gti = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/gti_LTAy_AvgDailyTotals');
opta = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/opta_LTAy_AvgDailyTotals');
pvout_ltam = ee.ImageCollection('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAm_AvgDailyTotals');
pvout_ltay = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAy_AvgDailyTotals');
temp_agl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/temp_2m_agl');
dif = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dif_LTAy_AvgDailyTotals")
dni = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dni_LTAy_AvgDailyTotals")
ghi = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ghi_LTAy_AvgDailyTotals")
esri_lulc10 = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS")
countries = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0")

# Define visualization parameters
dif_viz = {'min': 0.95, 'max': 3, 'palette': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac']}
dni_viz = {'min': 0.8, 'max': 10, 'palette': ['#0d0887', '#5c01a6', '#9c179e', '#ed7953', '#f0f921']}
ghi_viz = {'min': 2, 'max': 7, 'palette': ['#09ded0', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027', '#a50026']}
lulc_viz = {'min': 1, 'max': 9, 'palette': ['#1A5BAB', '#358221', '#87D19E', '#FFDB5C', '#ED022A', '#EDE9E4', '#F2FAFF', '#C8C8C8', '#C6AD8D']}

# Create a map
Map = geemap.Map(min_zoom=3, max_zoom=18)

lulc_image = esri_lulc10.filterDate('2023-01-01', '2023-12-31').mosaic()
palette_niccoli_linearl = ['#2B4BA1', '#4C74D9', '#7CEBA5', '#FFFF00', '#FFA500', '#FF4500', '#8B0000']


Map.addLayer(pvout_ltam.first(), {'min': 0.55, 'max': 7, 'palette': palette_niccoli_linearl}, 'PVOUT_LTAm')

Map.add_basemap('Esri.WorldImagery')


def center_map_on_input(sender):
    try:
        lat = float(lat_text.value)
        Map.set_center(float(lon_text.value), lat, zoom=8)  # Center map and set zoom
        point = ee.Geometry.Point(float(lon_text.value), lat)

        # Create a feature for the marker
        point_feature = ee.Feature(point)
        latlng = lat, float(lon_text.value)
        # Add the point as a layer on the map
        marker = Marker(location=latlng)
        Map.add_layer(marker)
        print(f"Map centered at latitude: {lat}, longitude: {float(lon_text.value)}")
        get_solar_data(lat, float(lon_text.value))

    except ValueError:
        print("Invalid latitude or longitude. Please enter valid numbers.")

# Create text input fields for latitude and longitude
lat_text = widgets.Text(
    value='0',
    description='Latitude:',
    disabled=False
)
lon_text = widgets.Text(
    value='0',
    description='Longitude:',
    disabled=False
)

# Create a button to trigger the map movement
submit_button = widgets.Button(
    description='Go to Coordinates',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click to center map at specified coordinates',
)

# Assign the function to be called when the button is clicked
submit_button.on_click(center_map_on_input)

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
    # Print results
    ghi_value = ghi_value.getInfo() if ghi_value is not None else "No GHI data"
    print(f"GHI at ({lat}, {lon}): {ghi_value} kWh/m²/day")

    dni_value = dni.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dni_value = dni_value.getInfo() if dni_value is not None else "No DNI data"
    print(f"DNI at ({lat}, {lon}): {dni_value} kWh/m²/day")

    # GTI (Global Tilted Irradiation)
    gti_value = gti.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    gti_value = gti_value.getInfo() if gti_value is not None else "No GTI data"
    print(f"GTI at ({lat}, {lon}): {gti_value} kWh/m²/day")

    # Optimum Tilt Angle
    opta_value = opta.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    opta_value = opta_value.getInfo() if opta_value is not None else "No Optimum Tilt Angle data"
    print(f"Optimum Tilt Angle at ({lat}, {lon}): {opta_value} degrees")

    # PV Output (Long-Term Annual Average)
    pvout_ltay_value = pvout_ltay.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    pvout_ltay_value = pvout_ltay_value.getInfo() if pvout_ltay_value is not None else "No PV Output (Annual) data"
    print(f"PV Output (Annual) at ({lat}, {lon}): {pvout_ltay_value} kWh/kWp/day")

    # Temperature at 2m Above Ground Level
    temp_agl_value = temp_agl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    temp_agl_value = temp_agl_value.getInfo() if temp_agl_value is not None else "No Temperature data"
    print(f"Temperature at 2m AGL at ({lat}, {lon}): {temp_agl_value} °C")

    # Elevation (Above Sea Level)
    elevation_value = elevation_asl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    elevation_value = elevation_value.getInfo() if elevation_value is not None else "No Elevation data"
    print(f"Elevation at ({lat}, {lon}): {elevation_value} meters")

    # Diffuse Horizontal Irradiation
    dif_value = dif.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dif_value = dif_value.getInfo() if dif_value is not None else "No Diffuse Irradiation data"
    print(f"Diffuse Horizontal Irradiation at ({lat}, {lon}): {dif_value} kWh/m²/day")


def add_legend(layer_name, legend_dict, title):
    Map.add_legend(legend_title=title, legend_dict=legend_dict)

markers_geojson = []
def handle_map_click(target, action, geo_json):
    if action == 'created' and geo_json['geometry']['type'] == 'Point':
        # Retrieve coordinates from geo_json
        coordinates = geo_json['geometry']['coordinates']
        latitude, longitude = coordinates[1], coordinates[0]

        # Create a marker at the location
        marker = Marker(location=(latitude, longitude))
        Map.add_layer(marker)

        # Save the marker's geojson representation
        markers_geojson.append(marker)

        # Print coordinates and geojson data
        print(f"Tọa độ: {latitude}, {longitude}")
        get_solar_data(latitude, longitude)

# Gọi hàm này khi bạn nhấn vào biểu tượng thùng rác
Map.draw_control.polyline = {}
Map.draw_control.circlemarker = {}
Map.draw_control.polygon = {'shapeOptions': {'color': '#0000FF'}}  # Set polygon color to blue
Map.draw_control.rectangle = {'shapeOptions': {'color': '#0000FF'}}  # Set rectangle color to blue
roi_layer_pairs = []

# Hàm tạo ID ngẫu nhiên
def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))  # Generate random ID

# Function to find and remove the layer corresponding to the deleted ROI by ID
def remove_layer_for_roi(roi_id):
    global roi_layer_pairs
    for i in range(len(roi_layer_pairs)):
        # Compare the ID of the deleted ROI with the ID in the array
        if roi_layer_pairs[i]['id'] == roi_id:
            # Remove the corresponding layer for that ROI
            Map.remove(roi_layer_pairs[i]['name'])

            return True
        return False

def handle_draw(target, action, geo_json):
    global roi_layer_pairs
    global roi
    if action == 'created' and geo_json['geometry']['type'] in ['Polygon', 'LineString']:
        roi_id = generate_id()
        print(f"New ROI ID: {roi_id}")

        # Thêm ID vào properties của geo_json
        if 'properties' not in geo_json:
            geo_json['properties'] = {}
        geo_json['properties']['id'] = roi_id
        print("GeoJSON after ID assignment:", geo_json)

        # Extract geometry from geo_json, handle potential errors
        try:
            # Assume geo_json is a dictionary and has a 'geometry' key
            geometry = geo_json.get('geometry')

            # Check if geometry is valid before creating ee.Geometry
            if geometry:
                roi = ee.Geometry(geometry)
            else:
                print("Invalid geometry data in geo_json")
                return
        except Exception as e:
            print(f"Error creating ee.Geometry: {e}")
            return

        # Print roi for verification
        print('ROI updated:', roi.getInfo())
        area_km2 = roi.area(maxError=1).divide(1e6)
        print('Area in square kilometers:', area_km2.getInfo())

        # Center the map on roi
        # Map.centerObject(roi, 6)

        # Calculate mean GHI
        mean_ghi = pvout_ltam.mean().reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            maxPixels=1e9
        ).get('b1')  # Adjust 'b1' if necessary for the correct band
        print('Mean GHI:', mean_ghi.getInfo())
        mean_ghi_image = ee.Image.constant(mean_ghi.getInfo())
        # Create an image where pixels have 1 if they exceed meanGhi, otherwise 0
        ghi_high = pvout_ltam.mean().gt(mean_ghi_image.multiply(1.005)).clip(roi)

        # Add layer for high GHI areas and save the layer
        layer_name = f'High GHI Areas - {roi_id}'
        layer_params = {'color': 'yellow', 'width': 23}

        # Add the layer for high GHI areas without expecting a return
        Map.addLayer(ghi_high.updateMask(ghi_high), layer_params, layer_name)

        # Store the ROI and its layer information in roi_layer_pairs
        roi_layer_pairs.append({
            'id': roi_id,
            'roi': roi,
            'name': layer_name,
            'params': layer_params,
            'geo_json': geo_json  # Store geo_json as is for deletion handling
        })
        # print("Current ROI Layer Pairs:", roi_layer_pairs)
        # print(roi_layer_pairs)
        # Center the map on the ROI

        # Calculate area of High GHI areas in square kilometers
        high_ghi_area = ghi_high.multiply(ee.Image.pixelArea()).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=roi,
            maxPixels=1e9
        )

        try:
            result = high_ghi_area.getInfo()  # This retrieves the result as a Python dictionary
            area_sq_km = result['b1'] / 1e6 if result and 'b1' in result else 0  # Convert to sq km if result exists
            print('High GHI Area (sq km):', area_sq_km)
        except Exception as e:
            print(f"Error getting high GHI area info: {e}")

def handle_deleted(target, action, geo_json):
    global roi_layer_pairs
    if action == 'deleted':
        # Compare geo_json geometries with those in roi_layer_pairs
        for entry in roi_layer_pairs:
            if entry['geo_json']['geometry'] == geo_json['geometry']:
                roi_id = entry['id']
                if remove_layer_for_roi(roi_id):
                    # Only remove from list if the layer was found and removed
                    roi_layer_pairs.remove(entry)
                    print(f"ROI with ID {roi_id} has been removed")
                break
        else:
            print("Matching ROI not found for deletion.")



Map.draw_control.on_draw(handle_map_click)
Map.draw_control.on_draw(handle_draw)
Map.draw_control.on_draw(handle_deleted)
widget_box = widgets.VBox([lat_text, lon_text, submit_button])
display(widget_box)
Map.addLayerControl()

Map.to_streamlit(height=500)