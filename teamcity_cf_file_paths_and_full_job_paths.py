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
PROJECT_API = f"{TEAMCITY_SERVER}/app/rest/projects/{{projectId}}"

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

# Function to get the full folder structure (project path) for a build configuration
def get_project_path(project_id):
    headers = {"Accept": "application/json"}  # Request JSON response
    response = requests.get(PROJECT_API.format(projectId=project_id), auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for projectId {project_id}")
        print("Response content:", response.text)
        return None

    # Try parsing JSON, if it fails, print the raw content
    try:
        project_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for projectId {project_id}. Response content:")
        print(response.text)
        return None

    # Recursively build the project path by traversing parent projects
    project_path = [project_data['name']]
    parent_project = project_data.get('parentProjectId')

    while parent_project:
        response = requests.get(PROJECT_API.format(projectId=parent_project), auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)
        if response.status_code != 200:
            break
        try:
            parent_data = response.json()
            project_path.insert(0, parent_data['name'])
            parent_project = parent_data.get('parentProjectId')
        except requests.exceptions.JSONDecodeError:
            break

    return " / ".join(project_path)

# Main function to collect unique values of the 'system.cloudformation-template.file-path' parameter along with build paths
def collect_file_paths_with_jobs():
    build_types = get_all_build_types()
    file_path_to_jobs = {}  # Dictionary to map file paths to the jobs that use them

    for build_type in build_types:
        build_type_id = build_type['id']
        build_type_name = build_type['name']
        project_id = build_type['projectId']

        # Get the full project path (folder structure)
        project_path = get_project_path(project_id)

        # Get parameters for the build configuration
        parameters = get_build_parameters(build_type_id)

        for param in parameters.get('property', []):
            if param['name'] == 'system.cloudformation-template.file-path':
                file_path = param['value']
                
                # Add the job (build configuration) with the full path to the list for this file path
                if file_path not in file_path_to_jobs:
                    file_path_to_jobs[file_path] = []

                full_job_path = f"{project_path} / {build_type_name}"
                file_path_to_jobs[file_path].append(full_job_path)

    return file_path_to_jobs

if __name__ == '__main__':
    file_path_to_jobs = collect_file_paths_with_jobs()

    # Print the mapping of file paths to jobs with full paths
    print("Mapping of 'system.cloudformation-template.file-path' to jobs:")
    for file_path, jobs in file_path_to_jobs.items():
        print(f"\nCloudFormation file path: {file_path}")
        print("Used in jobs:")
        for job in jobs:
            print(f"  - {job}")
