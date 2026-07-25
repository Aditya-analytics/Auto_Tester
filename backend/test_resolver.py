def resolve_schema(schema, full_swagger):
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        ref_path = schema["$ref"]
        # e.g. #/components/schemas/BaseConfig
        parts = ref_path.replace("#/", "").split("/")
        curr = full_swagger
        for p in parts:
            if p in curr:
                curr = curr[p]
            else:
                return schema
        return resolve_schema(curr, full_swagger)
    
    # Recursively resolve dicts
    resolved = {}
    for k, v in schema.items():
        if isinstance(v, dict):
            resolved[k] = resolve_schema(v, full_swagger)
        elif isinstance(v, list):
            resolved[k] = [resolve_schema(i, full_swagger) if isinstance(i, dict) else i for i in v]
        else:
            resolved[k] = v
    return resolved

from services.discovery import discover_openapi
swagger = discover_openapi('http://127.0.0.1:8000')
schema = {'$ref': '#/components/schemas/BaseConfig'}
print(resolve_schema(schema, swagger))
