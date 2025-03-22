import openslide
import boto3
import json
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw
from shapely.geometry import shape, box, Polygon, MultiPolygon
from shapely.affinity import translate
from tqdm import tqdm
import tempfile
import os



def extract_grids_from_svs_bucket(bucket_name, output_bucket, grid_size, palet, threshold=200):
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    svs_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.svs')]
    geojson_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.geojson')]
    
    file_pairs = {}
    for svs_key in svs_files:
        base_name = svs_key.rsplit('.', 1)[0]
        for geojson_key in geojson_files:
            if geojson_key.startswith(base_name):
                file_pairs[svs_key] = geojson_key
                break
    
    
        
    
    file_processed = 0

    for svs_key, geojson_key in file_pairs.items():
        
        print(f"Processing {svs_key} and {geojson_key}")

        # Download SVS file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as svs_temp_file:
            s3.download_fileobj(bucket_name, svs_key, svs_temp_file)
            svs_temp_file.seek(0)  # Go back to the start of the file
            slide = openslide.OpenSlide(svs_temp_file.name)
            width, height = slide.dimensions

        # Download GeoJSON file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as geojson_temp_file:
            s3.download_fileobj(bucket_name, geojson_key, geojson_temp_file)
            geojson_temp_file.seek(0)  # Go back to the start of the file
            geojson_data = json.load(geojson_temp_file)


        
        num_grids_x = width // grid_size
        num_grids_y = height // grid_size
        print(f"Total number of grids: {num_grids_x} x {num_grids_y}")
        
        total_skipped_patch = 0
        
        for i in tqdm(range(num_grids_x), desc=f"Extracting grids for {svs_key} (X-axis)"):
            for j in tqdm(range(num_grids_y), desc="Y-axis", leave=False):
                try:
                    x = i * grid_size
                    y = j * grid_size


                    output_prefix = f"{svs_key.rsplit('.', 1)[0]}"

                    grid_path = f"{output_prefix}/grid_{i}_{j}.jp2"
                    seg_path = f"{output_prefix}/segmentation_{i}_{j}.png"

                    if file_processed < 100:
                        skip = True
                        try:
                            s3.head_object(Bucket=bucket_name, Key=grid_path)
                        except Exception as e:
                            # means this file could not be found
                            skip = False
                        if skip:
                            continue
                        file_processed+=1
                        

                    region = slide.read_region((x, y), 0, (grid_size, grid_size)).convert('RGB')
                    region_np = np.array(region)
                    
                    bg_mask = (region_np[:, :, 0] > threshold) & (region_np[:, :, 1] > threshold) & (region_np[:, :, 2] > threshold)
                    foreground_mask = ~bg_mask
                    
                    if np.mean(foreground_mask) <= 0.3:  # Skips mostly background patches
                        total_skipped_patch += 1
                        continue
                    
                    segmentation_map = Image.new('RGB', (grid_size, grid_size), (255, 255, 255))
                    draw = ImageDraw.Draw(segmentation_map)
                    patch_boundary = box(0, 0, grid_size, grid_size)
                    
                    for feature in geojson_data['features']:
                        polygon = shape(feature['geometry'])
                        class_ = feature["properties"]["classification"]["name"]
                        if class_ not in palet:
                            class_ = "Others"
                        
                        translated_polygon = translate(polygon, -x, -y)
                        clipped_polygon = translated_polygon.intersection(patch_boundary)

                        if not clipped_polygon.is_empty and clipped_polygon.is_valid:
                            # Get the coordinates to draw

                            if isinstance(clipped_polygon, Polygon):
                                coords = [(px, py) for px, py in clipped_polygon.exterior.coords]
                            # Check if geometry is a MultiPolygon
                            elif isinstance(clipped_polygon, MultiPolygon):
                                coords = []
                                for polygon in clipped_polygon.geoms:  # Iterate through each polygon in the MultiPolygon
                                    coords.extend([(px, py) for px, py in polygon.exterior.coords])
                            
                            # Draw and fill the polygon on the segmentation map
                            try:
                                draw.polygon(coords, fill=palet[class_])  # Adjust colors as needed
                            except Exception as e:
                                pass
                    
                    region_buffer = BytesIO()
                    region.save(region_buffer, 'JPEG2000', quality_mode='lossless')
                    region_buffer.seek(0)
                    
                    seg_map_buffer = BytesIO()
                    segmentation_map.save(seg_map_buffer, 'PNG')
                    seg_map_buffer.seek(0)
                    
                    
                    s3.upload_fileobj(region_buffer, output_bucket, grid_path)
                    s3.upload_fileobj(seg_map_buffer, output_bucket, seg_path)
                    
                except Exception as e:
                    print(f"Error processing grid {i},{j} for {svs_key}: {e}")
        
        slide.close()

        os.remove(svs_temp_file.name)
        os.remove(geojson_temp_file.name)

        print(f"Total skipped patches for {svs_key}: {total_skipped_patch}")


palet = {
    "Others": (0, 0, 0),
    "T-G1": (0, 192, 0),
    "T-G2": (255, 224, 32),
    "T-G3": (255, 0, 0),
    "Normal mucosa":(0, 32, 255),
    "Others_": (255, 255, 255)
}


extract_grids_from_svs_bucket(
    bucket_name='coad-data',
    output_bucket='256-1x-fg-patches',
    grid_size=256,
    palet=palet
)