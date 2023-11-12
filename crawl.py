import requests
import json
import os
import time
SESSION = requests.Session()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def get_subareas(relation_id, api_endpoint="https://overpass-api.de/api/interpreter"):
    # Query to get all members (subareas) of the relation
    query_meta = f"""
    [out:json];
    relation({relation_id});
    (._;>;);
    out meta;
    """
    query_geom = f"""
    [out:json];
    rel({relation_id});
    (._;>;);
    out geom;
    """

    filepath = os.path.join(OUTPUT_DIR, f'{relation_id}.json')

    if os.path.exists(filepath):
        print(f"[{relation_id}] Already downloaded.")
        with open(filepath, 'r') as f:
            element = json.load(f)

    else:
        while True:
            response = SESSION.get(api_endpoint, params={'data': query_geom})

            if response.status_code != 200:
                print(f"[{relation_id}] Error: {response.status_code}")
                continue
            else:
                print(f"[{relation_id}] Success : {response.status_code}")
                break

        result = response.json()

        if 'elements' not in result:
            print(f"[{relation_id}] Warning: No elements found.")
            return []
        
        # find element whose type is relation
        elements = [e for e in result['elements'] if e['type'] == 'relation']
        if not elements or len(elements) == 0:
            print(f"[{relation_id}] Warning: No relations found.")
            return []
        
        if len(elements) > 1:
            print(f"[{relation_id}] Warning: No relations found.")
            return []
        
        element = elements[0]
        name_keys = [k for k in element['tags'] if 'name' in k]
        if not name_keys or len(name_keys) == 0:
            print(f"[{relation_id}] Warning: No name found.")
            element_name = f"relation_{relation_id}"
        if 'name' in name_keys:
            element_name = element['tags']['name']
        if 'name:en' in name_keys:
            element_name = element['tags']['name:en']
        if 'name:vi' in name_keys:
            element_name = element['tags']['name:vi']  
        else:
            element_name = element['tags'][name_keys[0]]
        
        print(f"[{relation_id}] Name: {element_name}")

        with open(filepath, 'w') as f:
            json.dump(element, f)
    
    if 'members' not in element:
        print(f"[{relation_id}] Warning: No members found.")
        return []

    subarea_ids = [m['ref'] for m in element['members'] if m['role'] == 'subarea']

    print(f"[{relation_id}]: Found {len(subarea_ids)} subareas.")

    all_subareas = []
    for subarea_id in subarea_ids:
        subarea_data = get_subareas(subarea_id)
        all_subareas.extend(subarea_data)

    return all_subareas

def main():
    relation_id = 49915

    all_subareas = get_subareas(relation_id)

    if not all_subareas:
        print("No subareas found.")
        return

if __name__ == "__main__":
    current_time = time.perf_counter()
    main()
    print(f"Time elapsed: {time.perf_counter() - current_time}")
