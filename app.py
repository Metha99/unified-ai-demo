import streamlit as st
import openai
import requests
from requests.auth import HTTPBasicAuth

# 🔐 API KEYS AND SECRETS (for demo only)
OPENAI_API_KEY = "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"
GITLAB_TOKEN = "glpat-Zg4U5fietyzw2_Y27xtu"
SNOW_INSTANCE = "https://dev203611.service-now.com"
SNOW_USER = "admin"
SNOW_PASSWORD = "Nachet@123$$$$$$"  # DEMO ONLY

openai.api_key = OPENAI_API_KEY

# Streamlit App
st.set_page_config(page_title="Unified AI", page_icon="🤖")
st.title("🤖 Unified AI - SRE Assistant")
st.markdown("Enter a customer-related query to fetch and analyze live system status, incidents, and pipelines.")

query = st.text_input("Enter Customer Query:")

def get_azure_data(customer):
    # Simulated Azure response based on customer name
    if "gava" in customer.lower():
        return "VMs:\n• gava-linux-db1 – Status: Running\n• gava-win-app01 – Status: Degraded (memory leak)"
    elif "tetra" in customer.lower():
        return "VMs:\n• tetra-db01 – Status: Critical (Disk Latency High)\n• tetra-frontend – Status: Running"
    else:
        return "No Azure VMs found for this customer."

def get_gitlab_data(customer):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    if "gava" in customer.lower():
        try:
            url = "https://gitlab.com/api/v4/projects/67127345/pipelines"
            res = requests.get(url, headers=headers)
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                latest = data[0]
                return f"Latest Pipeline for Gava:\n• Pipeline ID: {latest['id']} – Status: {latest['status']}"
            return "No GitLab pipelines found."
        except Exception as e:
            return f"GitLab API Error: {e}"
    return "No relevant GitLab pipelines found."

def get_snow_data(customer):
    try:
        table = "incident"
        query_url = f"{SNOW_INSTANCE}/api/now/table/{table}?sysparm_query=short_descriptionLIKE{customer}"
        headers = {"Accept": "application/json"}
        res = requests.get(query_url, headers=headers, auth=HTTPBasicAuth(SNOW_USER, SNOW_PASSWORD))
        data = res.json()

        if "result" in data and data["result"]:
            inc = data["result"][0]
            return f"ServiceNow Incident:\n• ID: {inc['number']}\n• Short Description: {inc['short_description']}"
        return "No ServiceNow incidents found for this customer."
    except Exception as e:
        return f"ServiceNow API Error: {e}"

if query:
    with st.spinner("Gathering system data..."):
        azure_info = get_azure_data(query)
        gitlab_info = get_gitlab_data(query)
        snow_info = get_snow_data(query)

        full_context = f"""
        🔍 Customer Query: {query}

        --- Azure Resources ---
        {azure_info}

        --- GitLab Pipelines ---
        {gitlab_info}

        --- ServiceNow Tickets ---
        {snow_info}
        """

        st.markdown("### 🔧 Retrieved Data")
        st.code(full_context.strip())

        st.markdown("### 🤖 Unified AI Analysis")
        with st.spinner("AI thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You're an SRE assistant that analyzes technical data to help engineers troubleshoot quickly."},
                        {"role": "user", "content": full_context}
                    ]
                )
                result = response['choices'][0]['message']['content']
                st.success(result)
            except Exception as e:
                st.error(f"OpenAI Error: {e}")
