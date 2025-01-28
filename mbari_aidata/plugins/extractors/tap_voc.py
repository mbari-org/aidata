# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_voc.py
# Description: Extracts data from a VOC generated xml files and prepares it for loading into Tator

from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

from tqdm import tqdm


def extract_voc(xml_path: Path) -> pd.DataFrame:
    """Extracts data from a VOC generated xml files."""
    dfs = []

    if xml_path.is_dir():
        for det_xml_file in tqdm(list(xml_path.rglob("*.xml")), desc="Reading XML"):
            try:
                df = parse_voc(det_xml_file.as_posix())
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {det_xml_file}: {e}")
                continue
        if len(dfs) == 0:
            return pd.DataFrame()
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df = combined_df.sort_values(by="image_path")
    else:
        combined_df = parse_voc(xml_path)

    return combined_df


#  Convert the xml data to a localization object formatted for the database
def parse_voc(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get the image width and height
    image_width = 0
    image_height = 0
    for size in root.findall('size'):
        image_width = int(size.find('width').text)
        image_height = int(size.find('height').text)

    # Get the image path
    image_path = root.find('path').text

    objs = []
    for obj in root.findall('object'):
        obj_info = {'name': obj.find('name').text}
        bbox = obj.find('bndbox')
        obj_info['xmin'] = float(bbox.find('xmin').text)
        obj_info['ymin'] = float(bbox.find('ymin').text)
        obj_info['xmax'] = float(bbox.find('xmax').text)
        obj_info['ymax'] = float(bbox.find('ymax').text)

        # Normalize the bounding box to the image size
        obj_info['xmin'] = obj_info['xmin'] / image_width
        obj_info['ymin'] = obj_info['ymin'] / image_height
        obj_info['xmax'] = obj_info['xmax'] / image_width
        obj_info['ymax'] = obj_info['ymax'] / image_height

        x = obj_info['xmin']
        y = obj_info['ymin']
        w = obj_info['xmax'] - obj_info['xmin']
        h = obj_info['ymax'] - obj_info['ymin']

        # if the height or width is < 0 skip this object
        if w < 0 or h < 0:
            continue

        obj = {
            'image_path': image_path,
            'label': obj_info['name'],
            'score': 1.0,
            'saliency': -1,
            'cluster': -1,
            'concept': obj_info['name'],
            'x': x,
            'y': y,
            'xx': x + w,
            'xy': y + h,
            'image_width': image_width,
            'image_height': image_height,
        }
        objs.append(obj)

    return pd.DataFrame(objs, columns=['image_path', 'label', 'score', 'saliency', 'concept', 'cluster',
                                       'x', 'y', 'xx', 'xy', 'image_width', 'image_height'])
