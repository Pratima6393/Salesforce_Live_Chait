
# import json
# import logging
# from config import logger
# from watsonx_utils import *
# import requests

# def call_watsonx_api(prompt, WATSONX_URL, WATSONX_PROJECT_ID, WATSONX_MODEL_ID, get_watsonx_token):
#     access_token = get_watsonx_token()
#     url = f"{WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "project_id": WATSONX_PROJECT_ID,
#         "model_id": WATSONX_MODEL_ID,
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
#     WATSONX_URL,
#     WATSONX_PROJECT_ID,
#     WATSONX_MODEL_ID,
#     get_watsonx_token,
#     max_chunk_size=3000
# ):
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
#             WATSONX_URL,
#             WATSONX_PROJECT_ID,
#             WATSONX_MODEL_ID,
#             get_watsonx_token
#         )
#     except Exception as e:
#         logger.error(f"Error calling WatsonX API: {e}")
#         return "Sorry, I couldn't generate a summary due to an error.", {}

#     try:
#         parsed_response = json.loads(response_text)
#         summary_text = parsed_response.get("summary", "No summary provided.")
#         data_obj = parsed_response.get("data", {})

#         # No reshaping here because app.py handles merged table conditionally
#         # Just return as-is
#     except Exception as e:
#         logger.error(f"Error parsing AI response JSON: {e}")
#         summary_text = response_text
#         data_obj = {}

#     return summary_text, data_obj


#====================================new update 3/7/25==============================
import json
import logging
from config import logger
from watsonx_utils import *
import requests

def call_watsonx_api(prompt, WATSONX_URL, WATSONX_PROJECT_ID, WATSONX_MODEL_ID, get_watsonx_token):
    access_token = get_watsonx_token()
    url = f"{WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "project_id": WATSONX_PROJECT_ID,
        "model_id": WATSONX_MODEL_ID,
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
    WATSONX_URL,
    WATSONX_PROJECT_ID,
    WATSONX_MODEL_ID,
    get_watsonx_token,
    max_chunk_size=3000
):
    try:
        backend_json_str = json.dumps(analysis_result, default=str)
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        backend_json_str = "{}"

    prompt = f"""
You are an AI assistant. Given the following backend analysis result and a user query, please provide:

1) A concise, clear, and user-friendly summary in text.
2) A JSON object containing two keys: 
   - "graph_data": an object with key-value pairs for fields and their counts (for plotting).
   - "details": a list of records or table rows with counts (for details tab).

Format your response EXACTLY as a JSON object with two keys "summary" and "data", for example:

{{
  "summary": "Your text summary here.",
  "data": {{
    "graph_data": {{
      "field1": {{"A": 10, "B": 5}},
      "field2": {{"X": 7, "Y": 8}}
    }},
    "details": [
      {{"field1": "A", "count": 10}},
      {{"field1": "B", "count": 5}}
    ]
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
            WATSONX_URL,
            WATSONX_PROJECT_ID,
            WATSONX_MODEL_ID,
            get_watsonx_token
        )
    except Exception as e:
        logger.error(f"Error calling WatsonX API: {e}")
        return "Sorry, I couldn't generate a summary due to an error.", {}

    try:
        parsed_response = json.loads(response_text)
        summary_text = parsed_response.get("summary", "No summary provided.")
        data_obj = parsed_response.get("data", {})

        # No reshaping here because app.py handles merged table conditionally
        # Just return as-is
    except Exception as e:
        logger.error(f"Error parsing AI response JSON: {e}")
        summary_text = response_text
        data_obj = {}

    return summary_text, data_obj
