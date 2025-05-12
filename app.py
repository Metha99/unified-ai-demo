import streamlit as st
import requests
import openai

# Hardcoded API Keys and Credentials (For testing purposes)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Azure credentials
AZURE_ACCESS_TOKEN = "QxN8Q~y.PalckYVbS5evoch2u3HiPfmhT1LmfbqX"
AZURE_SUBSCRIPTION_ID = "unified-ai-demo"  # Your Azure Subscription ID
AZURE_RESOURCE_GROUP = "unified-ai-prototype"  # Resource group name

# ServiceNow credentials
SNOW_INSTANCE = "https://dev203611.service-now.com"
SNOW_USER = "admin"
SNOW_PASSWORD = "Nachet@123$$$$$$"

# GitLab credentials
GITLAB_TOKEN = "glpat-Zg4U5fietyzw2_Y27xtu"
GITLAB_PROJECT_ID = "12345678"  # Replace with your GitLab project ID

# Set up the Streamlit page config
st.set_page_config(page_title="Unified AI", layout="centered")
st.title("🤖 Unified AI: Infra Assistant")

# Function to fetch Azure VM status
def get_azure_logs(query):
    # Fetch all VMs in the resource group
    vm_url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.Compute/virtualMachines?api-version=2021-07-01"
    headers = {
        'Authorization': f"Bearer {AZURE_ACCESS_TOKEN}"
    }

    response = requests.get(vm_url, headers=headers)
    if response.status_code == 200:
        vm_data = response.json()
        vm_statuses = []
        for vm in vm_data['value']:
            vm_name = vm['name']
            status_url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.Compute/virtualMachines/{vm_name}/instanceView?api-version=2021-07-01"
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code == 200:
                vm_status = status_response.json()
                status = vm_status['status']['displayStatus']
                vm_statuses.append(f"VM Name: {vm_name}, Status: {status}")
        return "\n".join(vm_statuses)
    else:
        return f"Error fetching Azure VMs. Status code: {response.status_code}"

# Function to fetch GitLab pipeline status
def get_pipeline_info(query):
    gitlab_url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/pipelines"
    headers = {'Private-Token': GITLAB_TOKEN}

    response = requests.get(gitlab_url, headers=headers)
    if response.status_code == 200:
        pipelines = response.json()
        if pipelines:
            last_pipeline = pipelines[0]  # Get the most recent pipeline
            status = last_pipeline['status']
            return f"GitLab Pipeline Status: {status}"
        else:
            return "No pipelines found."
    else:
        return f"Error fetching GitLab data. Status code: {response.status_code}"

# Function to fetch ServiceNow incidents
def get_incidents(query):
    url = f"{SNOW_INSTANCE}/api/now/table/incident?sysparm_query=short_description={query}&sysparm_limit=5"
    auth = (SNOW_USER, SNOW_PASSWORD)

    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        incidents = response.json()['result']
        if incidents:
            incident_details = []
            for incident in incidents:
                short_description = incident.get('short_description', 'N/A')
                status = incident.get('state', 'N/A')
                incident_details.append(f"Incident: {short_description}, Status: {status}")
            return "\n".join(incident_details)
        else:
            return "No incidents found for this query."
    else:
        return f"Error fetching ServiceNow data. Status code: {response.status_code}"

# Function to create prompt for OpenAI and ask for a response
def create_prompt(query, azure_data, servicenow_data, gitlab_data):
    prompt = f"""
    You are an intelligent assistant analyzing customer infrastructure.

    Customer Query: {query}

    --- Azure Resources ---
    {azure_data}

    --- ServiceNow Tickets ---
    {servicenow_data}

    --- GitLab Pipelines ---
    {gitlab_data}

    Provide a summary and any actionable insights.
    """
    return prompt

# Function to send request to OpenAI API and get the response
def ask_gpt(prompt):
    try:
        # Correct OpenAI API call using openai.chat.completions.create
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the latest available model
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with OpenAI: {e}"

# Get the user query
query = st.text_input("Enter your customer issue/query:")

if query:
    with st.spinner("Analyzing data sources..."):
        # Fetch data from Azure, GitLab, and ServiceNow
        azure = get_azure_logs(query)
        snow = get_incidents(query)
        gitlab = get_pipeline_info(query)

        # Create the prompt for OpenAI
        final_prompt = create_prompt(query, azure, snow, gitlab)

        # Send the prompt to OpenAI and get the response
        response = ask_gpt(final_prompt)

    # Display the result from OpenAI
    st.success("Unified AI Response:")
    st.markdown(response)
