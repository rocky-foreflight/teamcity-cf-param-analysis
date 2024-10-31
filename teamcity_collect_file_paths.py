import os

import requests
from requests.auth import HTTPBasicAuth

# TeamCity server details
TEAMCITY_SERVER = os.getenv("TEAMCITY_SERVER")
USERNAME = os.getenv("TEAMCITY_USERNAME")
PASSWORD = os.getenv("TEAMCITY_PASSWORD")

# API endpoints
BUILD_TYPES_API = f"{TEAMCITY_SERVER}/app/rest/buildTypes"
PARAMETERS_API = f"{TEAMCITY_SERVER}/app/rest/buildTypes/{{buildTypeId}}/parameters"

# Function to get all build configurations
def get_all_build_types():
    headers = {"Accept": "application/json"}  # Request JSON response
    response = requests.get(BUILD_TYPES_API, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print("Response content:", response.text)
        return []

    # Try parsing JSON, if it fails, print the raw content
    try:
        build_types = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON. Response content:")
        print(response.text)
        return []

    return [build_type['id'] for build_type in build_types.get('buildType', [])]

# Function to get parameters for a specific build configuration
def get_build_parameters(build_type_id):
    headers = {"Accept": "application/json"}  # Request JSON response
    response = requests.get(PARAMETERS_API.format(buildTypeId=build_type_id), auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for buildTypeId {build_type_id}")
        print("Response content:", response.text)
        return {}

    # Try parsing JSON, if it fails, print the raw content
    try:
        parameters = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for buildTypeId {build_type_id}. Response content:")
        print(response.text)
        return {}

    return parameters

# Main function to collect unique values of the 'system.cloudformation-template.file-path' parameter
def collect_unique_file_paths():
    build_type_ids = get_all_build_types()
    print(len(build_type_ids))
    # file_paths = set()  # Using a set to store unique values

    # for build_type_id in build_type_ids:
    #     parameters = get_build_parameters(build_type_id)
    #     for param in parameters.get('property', []):
    #         if param['name'] == 'system.cloudformation-template.file-path':
    #             file_paths.add(param['value'])  # Add the value to the set for uniqueness
    #             print(file_paths)

    return file_paths

if __name__ == '__main__':
    unique_file_paths = collect_unique_file_paths()

    # Print the unique values
    print("Unique 'system.cloudformation-template.file-path' values across all builds:")
    for file_path in unique_file_paths:
        print(file_path)
