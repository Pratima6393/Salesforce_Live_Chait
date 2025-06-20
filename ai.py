
# import json
# import logging
# from config import logger
# # from watsonx_utils import get_watsonx_token, watsonx_url, watsonx_project_id, watsonx_model_id
# import requests

# def call_watsonx_api(prompt, watsonx_url, watsonx_project_id, watsonx_model_id, get_watsonx_token):
#     access_token = get_watsonx_token()
#     url = f"{watsonx_url}/ml/v1/text/chat?version=2023-05-29"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "project_id": watsonx_project_id,
#         "model_id": watsonx_model_id,
#         "messages": [
#             {"role": "system", "content": "You are a helpful, concise, conversational analytics assistant."},
#             {"role": "user", "content": prompt}
#         ],
#         "parameters": {"decoding_method": "greedy"}
#     }
#     response = requests.post(url, headers=headers, json=data, timeout=120)
#     response.raise_for_status()
#     resp_json = response.json()

#     if isinstance(resp_json, dict) and 'results' in resp_json and resp_json['results']:
#         return resp_json['results'][0].get('generated_text', str(resp_json['results'][0]))
#     elif isinstance(resp_json, dict) and 'choices' in resp_json and resp_json['choices']:
#         return resp_json['choices'][0]['message'].get('content', str(resp_json['choices'][0]['message']))
#     elif isinstance(resp_json, dict) and 'error' in resp_json:
#         logger.error(f"WatsonX API Error: {resp_json}")
#         return f"Sorry, there was an AI error: {resp_json['error']}"
#     else:
#         logger.error(f"WatsonX API unexpected response: {resp_json}")
#         return "Sorry, I couldn't generate a summary for this result."

# def summarize_analysis_result_with_ai(
#     analysis_result,
#     user_question,
#     watsonx_url,
#     watsonx_project_id,
#     watsonx_model_id,
#     get_watsonx_token,
#     max_chunk_size=3000
# ):
#     """
#     Summarize backend result and also return structured graph and detail data as JSON.
#     """

#     # Serialize analysis_result to JSON string safely
#     try:
#         backend_json_str = json.dumps(analysis_result, default=str)
#     except Exception as e:
#         logger.error(f"Serialization error: {e}")
#         backend_json_str = "{}"

#     prompt = f"""
# You are an AI assistant. Given the following backend analysis result and a user query, please provide:

# 1) A concise, clear, and user-friendly summary in text.
# 2) A JSON object containing two keys: 
#    - "graph_data": an object with key-value pairs for fields and their counts (for plotting).
#    - "details": a list of records or table rows with counts (for details tab).

# Format your response EXACTLY as a JSON object with two keys "summary" and "data", for example:

# {{
#   "summary": "Your text summary here.",
#   "data": {{
#     "graph_data": {{
#       "field1": {{"A": 10, "B": 5}},
#       "field2": {{"X": 7, "Y": 8}}
#     }},
#     "details": [
#       {{"field1": "A", "count": 10}},
#       {{"field1": "B", "count": 5}}
#     ]
#   }}
# }}

# Backend analysis result (in JSON):
# {backend_json_str}

# User question:
# {user_question}

# Please ONLY output the JSON object described above.
# """

#     try:
#         response_text = call_watsonx_api(
#             prompt,
#             watsonx_url,
#             watsonx_project_id,
#             watsonx_model_id,
#             get_watsonx_token
#         )
#     except Exception as e:
#         logger.error(f"Error calling WatsonX API: {e}")
#         return "Sorry, I couldn't generate a summary due to an error.", {}

#     # Parse JSON from AI response
#     try:
#         parsed_response = json.loads(response_text)
#         summary_text = parsed_response.get("summary", "No summary provided.")
#         data_obj = parsed_response.get("data", {})
#     except Exception as e:
#         logger.error(f"Error parsing AI response JSON: {e}")
#         # fallback: just return full text as summary and empty data
#         summary_text = response_text
#         data_obj = {}

#     return summary_text, data_obj

#==========================================new code today=====================


import json
import logging
from config import logger
#from watsonx_utils import get_watsonx_token, watsonx_url, watsonx_project_id, watsonx_model_id
import requests

def call_watsonx_api(prompt, watsonx_url, watsonx_project_id, watsonx_model_id, get_watsonx_token):
    access_token = get_watsonx_token()
    url = f"{watsonx_url}/ml/v1/text/chat?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "project_id": watsonx_project_id,
        "model_id": watsonx_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful, concise, conversational analytics assistant."},
            {"role": "user", "content": prompt}
        ],
        "parameters": {"decoding_method": "greedy"}
    }
    response = requests.post(url, headers=headers, json=data, timeout=120)
    response.raise_for_status()
    resp_json = response.json()

    if isinstance(resp_json, dict) and 'results' in resp_json and resp_json['results']:
        return resp_json['results'][0].get('generated_text', str(resp_json['results'][0]))
    elif isinstance(resp_json, dict) and 'choices' in resp_json and resp_json['choices']:
        return resp_json['choices'][0]['message'].get('content', str(resp_json['choices'][0]['message']))
    elif isinstance(resp_json, dict) and 'error' in resp_json:
        logger.error(f"WatsonX API Error: {resp_json}")
        return f"Sorry, there was an AI error: {resp_json['error']}"
    else:
        logger.error(f"WatsonX API unexpected response: {resp_json}")
        return "Sorry, I couldn't generate a summary for this result."


def summarize_analysis_result_with_ai(
    analysis_result,
    user_question,
    watsonx_url,
    watsonx_project_id,
    watsonx_model_id,
    get_watsonx_token,
    max_chunk_size=3000
):
    """
    Summarize backend result and also return structured graph and detail data as JSON.
    Supports multiple tables in the 'details' key.
    """

    try:
        backend_json_str = json.dumps(analysis_result, default=str)
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        backend_json_str = "{}"

    prompt = f"""
You are an AI assistant. Given the following backend analysis result and a user query, please provide:

1) A concise, clear, and user-friendly summary in text.
2) A JSON object with two keys: 
   - "graph_data": an object with key-value pairs for fields and their counts (for plotting).
   - "details": either a single table (list of rows) or an object containing multiple named tables. Each table is a list of records (dicts).

Format your response EXACTLY as a JSON object with keys "summary" and "data". For example:

{{
  "summary": "Your summary here.",
  "data": {{
    "graph_data": {{
      "field1": {{"A": 10, "B": 5}},
      "field2": {{"X": 7, "Y": 8}}
    }},
    "details": {{
      "Count Table": [
        {{"field1": "A", "count": 10}},
        {{"field1": "B", "count": 5}}
      ],
      "Funnel Ratio Table": [
        {{"stage": "Lead", "ratio": 0.5}},
        {{"stage": "Converted", "ratio": 0.3}}
      ]
    }}
  }}
}}

Backend analysis result (in JSON):
{backend_json_str}

User question:
{user_question}

Please ONLY output the JSON object described above.
"""

    try:
        response_text = call_watsonx_api(
            prompt,
            watsonx_url,
            watsonx_project_id,
            watsonx_model_id,
            get_watsonx_token
        )
    except Exception as e:
        logger.error(f"Error calling WatsonX API: {e}")
        return "Sorry, I couldn't generate a summary due to an error.", {}

    try:
        parsed_response = json.loads(response_text)
        summary_text = parsed_response.get("summary", "No summary provided.")
        data_obj = parsed_response.get("data", {})
    except Exception as e:
        logger.error(f"Error parsing AI response JSON: {e}")
        summary_text = response_text
        data_obj = {}

    return summary_text, data_obj

