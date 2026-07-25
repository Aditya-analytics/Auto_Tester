import json

def normalize_json_keys(data, schema):
    if not isinstance(data, dict) or not isinstance(schema, dict):
        if isinstance(data, list) and isinstance(schema, dict) and "items" in schema:
            return [normalize_json_keys(item, schema["items"]) for item in data]
        return data
        
    properties = schema.get("properties", {})
    
    # Create a mapping of lowercased stripped keys to actual keys
    # e.g. "baseurl" -> "base_url"
    valid_key_map = {}
    for k in properties.keys():
        normalized_k = k.lower().replace("_", "").replace("-", "")
        valid_key_map[normalized_k] = k
        
    normalized_data = {}
    for k, v in data.items():
        search_k = k.lower().replace("_", "").replace("-", "")
        if search_k in valid_key_map:
            actual_k = valid_key_map[search_k]
            # recursively normalize if this property has a schema
            prop_schema = properties.get(actual_k, {})
            normalized_data[actual_k] = normalize_json_keys(v, prop_schema)
        else:
            # If we don't find a match, just keep the original key but still recurse if we somehow know the schema
            normalized_data[k] = v
            
    return normalized_data

ai_out = {"baseUrl": "http", "nestedObj": {"firstName": "suyash"}}
schema = {
    "type": "object", 
    "properties": {
        "base_url": {"type": "string"},
        "nested_obj": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"}
            }
        }
    }
}

print(normalize_json_keys(ai_out, schema))
