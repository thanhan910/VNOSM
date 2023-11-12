import os
import json

def create_polygons(borders):
    lines = [[]]
    if len(borders) == 0:
        # print("Warning: Found no borders")
        return lines
    if len(borders) == 1:
        lines[-1].extend(borders[0])
        return lines

    elif len(borders) == 1:
        lines[-1].extend(borders[0])
    if borders[0][-1] == borders[1][0]:
        lines[-1].extend(borders[0])
        lines[-1].extend(borders[1][1:])
    elif borders[0][0] == borders[1][0]:
        lines[-1].extend(borders[0][::-1])
        lines[-1].extend(borders[1][1:])
    elif borders[0][-1] == borders[1][-1]:
        lines[-1].extend(borders[0])
        lines[-1].extend(borders[1][::-1][1:])
    elif borders[0][0] == borders[1][-1]:
        lines[-1].extend(borders[0][::-1])
        lines[-1].extend(borders[1][::-1][1:])
    else:
        # print("Warning: Found non connected borders")
        lines[-1].extend(borders[0])
        lines.append([])
        lines[-1].extend(borders[1][1:])

    for border in borders[2:]:
        if lines[-1][-1] == border[-1]:
            lines[-1].extend(border[::-1][1:])
        elif lines[-1][-1] == border[0]:
            lines[-1].extend(border[1:])
        else:
            # print("Warning: Found non connected borders")
            lines.append([])
            lines[-1].extend(border[1:])
    return lines

def create_geojson_object(element):

    labels = [m for m in element['members'] if m['role'] == 'label']
    subareas = [int(m['ref']) for m in element['members'] if m['role'] == 'subarea']
    borders = [[(point['lon'], point['lat']) for point in m['geometry']] for m in element['members'] if m['role'] == 'outer' and m['type'] == 'way']

    for m in element['members']:
        if m['role'] == 'outer':
            if 'geometry' not in m:
                print(f"[{element['id']}] Warning: Found no geometry")

    geojson_object = {}

    geojson_object['type'] = 'Feature'
    geojson_object['properties'] = {
        'id': element['id'],
        'type': element['type'],
        'tags': element['tags'],
        'bounds': element['bounds'],
        'label': labels,
        'subareas': subareas
    }

    lines = create_polygons(borders)
    
    if len(lines) == 1:
        geojson_object['geometry'] = {
            'type': 'Polygon',
            'coordinates': lines
        }
    else:
        geojson_object['geometry'] = {
            'type': 'MultiPolygon',
            'coordinates': lines
        }

    return geojson_object

def main():
    INPUT_DIR = "output"
    data = {int(f.removesuffix('.json')): json.load(open(os.path.join(INPUT_DIR, f), "r")) for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f)) and f.endswith(".json")}
    data = { k : create_geojson_object(v) for k, v in data.items() }
    OUTPUT_DIR = "subareas"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for k, v in data.items():
        v['properties']['parent'] = []
    for k, v in data.items():
        for osm_id in v['properties']['subareas']:
            if osm_id in data:
                data[osm_id]['properties']['parent'].append(k)
            else:
                print(f"Warning: Cannot find {osm_id}")
    for k, v in data.items():
        polygons = []
        for osm_id in v['properties']['subareas']:
            if osm_id in data:
                polygons.append(data[osm_id])
            else:
                print(f"Warning [{k}]: Cannot find {osm_id}")
        if len(polygons) > 0:    
            with open(os.path.join(OUTPUT_DIR, f"{k}.geojson"), "w") as f:
                json.dump(polygons, f)
        print(k)

if __name__ == "__main__":
    main()


