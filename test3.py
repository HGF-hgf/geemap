# app.py
from flask import Flask, render_template, jsonify, request
import ee
import geemap
import random
import string
app = Flask(__name__)

# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='qualified-glow-437914-i0')

# DATASET definitions
elevation_asl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ele_asl')
gti = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/gti_LTAy_AvgDailyTotals')
opta = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/opta_LTAy_AvgDailyTotals')
pvout_ltay = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAy_AvgDailyTotals')
pvout_ltam = ee.ImageCollection('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/pvout_LTAm_AvgDailyTotals');
temp_agl = ee.Image('projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/temp_2m_agl')
dif = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dif_LTAy_AvgDailyTotals")
dni = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/dni_LTAy_AvgDailyTotals")
ghi = ee.Image("projects/earthengine-legacy/assets/projects/sat-io/open-datasets/global_solar_atlas/ghi_LTAy_AvgDailyTotals")

roi_layer_pairs = []

def get_solar_data(lat, lon):
    point = ee.Geometry.Point(lon, lat)
    
    # Collect all data points
    data = {}
    
    # PV Output (Long-Term Annual Average)
    pvout_ltay_value = pvout_ltay.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    pvout_ltay_value = pvout_ltay_value.getInfo() if pvout_ltay_value is not None else "No PV Output (Annual) data"
    data['pvout_ltay'] = pvout_ltay_value if pvout_ltay_value is not None else "No data"
    
    # GHI (Global Horizontal Irradiation)
    ghi_value = ghi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=8,
            bestEffort=True
        )
    ghi_value = ghi_value.get('b1')
    ghi_value = ghi_value.getInfo() if ghi_value is not None else "No GHI data"
    data['ghi'] = round(ghi_value, 2) if ghi_value is not None else "No data"
    
    # DNI (Direct Normal Irradiation)
    dni_value = dni.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dni_value = dni_value.getInfo() if dni_value is not None else "No DNI data"
    data['dni'] = round(dni_value, 2) if dni_value is not None else "No data"
    
    # Diffuse Horizontal Irradiation
    dif_value = dif.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    dif_value = dif_value.getInfo() if dif_value is not None else "No Diffuse Irradiation data"
    data['dif'] = round(dif_value, 2) if dif_value is not None else "No data"
    
    # GTI (Global Tilted Irradiation)
    gti_value = gti.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    gti_value = gti_value.getInfo() if gti_value is not None else "No GTI data"
    data['gti'] = round(gti_value, 2) if gti_value is not None else "No data"
    
    # Optimum Tilt Angle
    opta_value = opta.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    opta_value = opta_value.getInfo() if opta_value is not None else "No Optimum Tilt Angle data"
    data['opta'] = round(opta_value, 2) if opta_value is not None else "No data"

    
    # Temperature at 2m Above Ground Level
    temp_agl_value = temp_agl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    temp_agl_value = temp_agl_value.getInfo() if temp_agl_value is not None else "No Temperature data"
    data['temp_agl'] = round(temp_agl_value, 2) if temp_agl_value is not None else "No data"
    
    # Elevation (Above Sea Level)
    elevation_value = elevation_asl.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=8,
        bestEffort=True
    ).get('b1')
    elevation_value = elevation_value.getInfo() if elevation_value is not None else "No Elevation data"
    data['elevation_asl'] = round(elevation_value, 2) if elevation_value is not None else "No data"

    # Get other values similarly...
    # Add more data collection as needed
    
    return data

def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))  # Generate random ID

def handle_draw(geo_json):
    roi_data = {}
    global roi_layer_pairs
    roi = None
    if geo_json['geometry']['type'] in ['Polygon', 'LineString']:
        roi_id = generate_id()
        print(f"New ROI ID: {roi_id}")

        # Add ID to properties of geo_json
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
        roi_data['area'] = round(area_km2.getInfo(),2)

        mean_image = pvout_ltay.focal_mean(radius=600, units='meters')

        # Tính trung bình của hình ảnh đã làm mịn trong vùng roi
        mean_ghi = mean_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            maxPixels=1e9
        ).get('b1')
        print('Mean GHI:', mean_ghi.getInfo())
        roi_data['mean_pvOut'] = mean_ghi.getInfo()
        mean_ghi_image = ee.Image.constant(mean_ghi.getInfo())
        # Create an image where pixels have 1 if they exceed meanGhi, otherwise 0
        ghi_high = pvout_ltay.gt(mean_ghi_image).selfMask().clip(roi)

        # Add layer for high GHI areas and save the layer
        layer_name = f'High GHI Areas - {roi_id}'
        layer_params = {'color': 'yellow', 'width': 23}

        # Store the ROI and its layer information in roi_layer_pairs
        roi_layer_pairs.append({
            'id': roi_id,
            'roi': roi,
            'name': layer_name,
            'params': layer_params,
            'geo_json': geo_json  # Store geo_json as is for deletion handling
        })

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
            roi_data['high_pv_area'] = round(area_sq_km, 2)

        except Exception as e:
            print(f"Error getting high GHI area info: {e}")
            
        ghi_high_viz = {'min': 0, 'max': 1, 'palette': ['black', 'yellow']}
        

        return {
            'roi_id': roi_id,
            'layer_name': layer_name,
            'layer_params': ghi_high_viz,
            'geo_json': geo_json,
            'tile_url': geemap.ee_tile_layer(ghi_high, layer_params, layer_name).url            
        }, roi_data
        
def remove_layer_for_roi(roi_id):
    global roi_layer_pairs
    for i in range(len(roi_layer_pairs)):
        # Compare the ID of the deleted ROI with the ID in the array
        if roi_layer_pairs[i]['id'] == roi_id:
            # Remove the corresponding layer for that ROI
            # Remove the roi and layer pair from the array
            roi_layer_pairs.pop(i)
            return True
        return False

def handle_deleted(geo_json):
    global roi_layer_pairs
    print(f"Deleting ROI with geo_json: {geo_json}")
    for entry in roi_layer_pairs:
        print(f"Checking entry: {entry['geo_json']}")
        if entry['geo_json']['geometry'] == geo_json['geometry']:
            roi_id = entry['id']
            if remove_layer_for_roi(roi_id):
                # Only remove from list if the layer was found and removed
                roi_layer_pairs.remove(entry)
                print(f"ROI with ID {roi_id} has been removed")
            break
    else:
        print("Matching ROI not found for deletion.")

    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.get_json()
    lat = float(data['lat'])
    lon = float(data['lon'])
    
    solar_data = get_solar_data(lat, lon)
    return jsonify(solar_data)

@app.route('/handle_draw', methods=['POST'])
def handle_draw_endpoint():
    data = request.get_json()
    geo_json = data['geo_json']
    result, roi_data = handle_draw(geo_json)
    return jsonify({'result': result, 'roi_data': roi_data})

@app.route('/handle_deleted', methods=['POST'])
def handle_deleted_endpoint():
    data = request.get_json()
    geo_json = data['geo_json']
    handle_deleted(geo_json)
    return jsonify({'status': 'success'})

@app.route('/get_tile_url', methods=['GET'])
def get_tile_url():
    vis_params = {
        'min': 0.55,
        'max': 7,
        'palette': ['#2B4BA1', '#4C74D9', '#7CEBA5', '#FFFF00', '#FFA500', '#FF4500', '#8B0000']
    }
    map_id_dict = geemap.ee_tile_layer(pvout_ltam, vis_params, 'PVOUT_LTAm')
    tile_url = map_id_dict.url
    return jsonify({'tile_url': tile_url})

if __name__ == '__main__':
    app.run(debug=True)