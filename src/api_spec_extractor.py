from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# # tool to extract the API spec from the given text
# @tool("fetch_api_openapi_specification", args_schema=APIInput)
def fetch_api_openapi_specification(path: str, method: str) -> str:
    """Tool help to extract the API specification from the given API path. Use the path and method as parameters to extract the API spec."""
    return get_api_spec(path, method, "data/apis/openapi-specification.yaml")

# Actual API specification extraction logic below

import json
import yaml
from copy import deepcopy

def load_openapi_spec(file_path):
    """Load OpenAPI specification from a file."""
    with open(file_path, 'r') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)
        elif file_path.endswith('.json'):
            return json.load(file)
        else:
            raise ValueError("Unsupported file format. Only JSON and YAML are supported.")

def extract_specific_paths(openapi_spec, paths_to_extract, method='get'):
    """Extract specific paths from OpenAPI specification."""
    extracted_details = {'paths': {}}
    for path in paths_to_extract:
        if path in openapi_spec['paths']:
            if method in openapi_spec['paths'][path]:
                extracted_details['paths'][path] = {}
                extracted_details['paths'][path][method] = openapi_spec['paths'][path][method]
    return extracted_details


def extract_references(data, ref_list):
    """Recursively extract all references from the given data."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == '$ref':
                ref_list.append(value)
            else:
                extract_references(value, ref_list)
    elif isinstance(data, list):
        for item in data:
            extract_references(item, ref_list)

def copy_referenced_components(openapi_spec, ref_list):
    """Copy all referenced components from the original spec to the new spec."""
    components = deepcopy(openapi_spec.get('components', {}))
    new_components = {}
    for ref in ref_list:
        parts = ref.split('/')
        if len(parts) > 2 and parts[0] == '#' and parts[1] == 'components':
            component_type = parts[2]
            component_name = parts[3]
            if component_type not in new_components:
                new_components[component_type] = {}
            new_components[component_type][component_name] = components.get(component_type, {}).get(component_name, {})
    return new_components

def build_new_openapi_spec(extracted_details, openapi_spec, ref_list):
    """Build a new OpenAPI specification using extracted path details and referenced components."""
    new_spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Extracted API',
            'version': '1.0.0'
        },
        'paths': extracted_details['paths'],
        'components': copy_referenced_components(openapi_spec, ref_list)
    }
    return new_spec

def save_openapi_spec(openapi_spec, file_path):
    """Save OpenAPI specification to a file."""
    with open(file_path, 'w') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            yaml.dump(openapi_spec, file, default_flow_style=False)
        elif file_path.endswith('.json'):
            json.dump(openapi_spec, file, indent=2)
        else:
            raise ValueError("Unsupported file format. Only JSON and YAML are supported.")
        
def get_api_spec(path, method, openapi_spec_path):
    # Example usage
    input_file_path = openapi_spec_path  # Replace with your input file path
    paths_to_extract = [path]  # Replace with the paths you want to extract

    # Load the existing OpenAPI specification
    openapi_spec = load_openapi_spec(input_file_path)

    # Extract specified paths
    extracted_details = extract_specific_paths(openapi_spec, paths_to_extract, method)

    # Extract all $refs from the extracted paths
    ref_list = []
    for path, methods in extracted_details['paths'].items():
        for method, details in methods.items():
            if 'requestBody' in details:
                extract_references(details['requestBody'], ref_list)
            if 'responses' in details:
                extract_references(details['responses'], ref_list)

    # Build a new OpenAPI specification
    new_openapi_spec = build_new_openapi_spec(extracted_details, openapi_spec, ref_list)

    return yaml.dump(new_openapi_spec, default_flow_style=False)
