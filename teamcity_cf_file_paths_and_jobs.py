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

    return build_types.get('buildType', [])

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
def collect_file_paths_with_jobs():
    build_types = get_all_build_types()
    file_path_to_jobs = {}  # Dictionary to map file paths to the jobs that use them

    for build_type in build_types:
        build_type_id = build_type['id']
        build_type_name = build_type['name']  # Optional: can also use 'buildType' field if needed
        
        parameters = get_build_parameters(build_type_id)
        
        for param in parameters.get('property', []):
            if param['name'] == 'system.cloudformation-template.file-path':
                file_path = param['value']
                
                # Add the job (build configuration) to the list for this file path
                if file_path not in file_path_to_jobs:
                    file_path_to_jobs[file_path] = []
                
                file_path_to_jobs[file_path].append(build_type_name)

    return file_path_to_jobs

if __name__ == '__main__':
    file_path_to_jobs = collect_file_paths_with_jobs()

    # Print the mapping of file paths to jobs
    print("Mapping of 'system.cloudformation-template.file-path' to jobs:")
    for file_path, jobs in file_path_to_jobs.items():
        print(f"\nCloudFormation file path: {file_path}")
        print("Used in jobs:")
        for job in jobs:
            print(f"  - {job}")
