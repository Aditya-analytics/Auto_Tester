from pydantic import ValidationError
from models import ApiConfig

def load_configuration(raw_data: dict) -> ApiConfig:
    """
    Parses and validates a raw dictionary into a structured ApiConfig object.
    Throws a ValidationError if the data is malformed.
    """
    try:
        config = ApiConfig(**raw_data)
        return config
    except ValidationError as e:
        print("❌ Configuration Error: Invalid Data Provided!")
        print(e.json(indent=2))
        raise

# ==========================================
# MANUAL TESTING & ERROR SIMULATION
# ==========================================
# from models import BaseConfig
# config = BaseConfig(base_url="https://petstore.swagger.io/v2")
# print(config.base_url)

# # Now try to break it with a bad URL:
# bad_config = BaseConfig(base_url="petstore") 
