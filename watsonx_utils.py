
import requests
import json
import re
import pandas as pd
from config import watsonx_api_key, watsonx_project_id, watsonx_url, watsonx_model_id, IBM_CLOUD_IAM_URL, logger

def validate_watsonx_config():
    missing_configs = []
    if not watsonx_api_key:
        missing_configs.append("WATSONX_API_KEY")
    if not watsonx_project_id:
        missing_configs.append("WATSONX_PROJECT_ID")
    if missing_configs:
        error_msg = f"Missing WatsonX configuration: {', '.join(missing_configs)}"
        logger.error(error_msg)
        return False, error_msg
    if len(watsonx_api_key.strip()) < 10:
        return False, "WATSONX_API_KEY appears to be invalid (too short)"
    if len(watsonx_project_id.strip()) < 10:
        return False, "WATSONX_PROJECT_ID appears to be invalid (too short)"
    return True, "Configuration valid"

def get_watsonx_token():
    is_valid, validation_msg = validate_watsonx_config()
    if not is_valid:
        raise ValueError(f"Configuration error: {validation_msg}")
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": watsonx_api_key.strip()}
    logger.info("Requesting IBM Cloud IAM token...")
    try:
        response = requests.post(IBM_CLOUD_IAM_URL, headers=headers, data=data, timeout=90)
        logger.info(f"IAM Token Response Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("No access_token in response")
            logger.info("Successfully obtained IAM token")
            return access_token
        else:
            error_details = {
                "status_code": response.status_code,
                "response_text": response.text[:1000],
                "headers": dict(response.headers),
                "request_body": data
            }
            logger.error(f"IAM Token request failed: {error_details}")
            raise requests.exceptions.HTTPError(f"IAM API Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"IAM Token request exception: {str(e)}")
        raise

def create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df):
    context = {
        "data_summary": {
            "total_leads": len(leads_df),
            "total_users": len(users_df),
            "total_cases": len(cases_df),
            "total_events": len(events_df),
            "total_opportunities": len(opportunities_df),
            "total_tasks": len(task_df),
            "available_lead_fields": list(leads_df.columns) if not leads_df.empty else [],
            "available_user_fields": list(users_df.columns) if not users_df.empty else [],
            "available_case_fields": list(cases_df.columns) if not cases_df.empty else [],
            "available_event_fields": list(events_df.columns) if not events_df.empty else [],
            "available_opportunity_fields": list(opportunities_df.columns) if not opportunities_df.empty else [],
            "available_task_fields": list(task_df.columns) if not task_df.empty else []
        }
    }
    if not leads_df.empty:
        context["lead_field_info"] = {}
        for col in leads_df.columns:
            sample_values = leads_df[col].dropna().unique()[:5].tolist()
            context["lead_field_info"][col] = {
                "sample_values": [str(v) for v in sample_values],
                "null_count": leads_df[col].isnull().sum(),
                "data_type": str(leads_df[col].dtype)
            }
    if not cases_df.empty:
        context["case_field_info"] = {}
        for col in cases_df.columns:
            sample_values = cases_df[col].dropna().unique()[:5].tolist()
            context["case_field_info"][col] = {
                "sample_values": [str(v) for v in sample_values],
                "null_count": cases_df[col].isnull().sum(),
                "data_type": str(cases_df[col].dtype)
            }
    if not events_df.empty:
        context["event_field_info"] = {}
        for col in events_df.columns:
            sample_values = events_df[col].dropna().unique()[:5].tolist()
            context["event_field_info"][col] = {
                "sample_values": [str(v) for v in sample_values],
                "null_count": events_df[col].isnull().sum(),
                "data_type": str(events_df[col].dtype)
            }
    if not opportunities_df.empty:
        context["opportunity_field_info"] = {}
        for col in opportunities_df.columns:
            sample_values = opportunities_df[col].dropna().unique()[:5].tolist()
            context["opportunity_field_info"][col] = {
                "sample_values": [str(v) for v in sample_values],
                "null_count": opportunities_df[col].isnull().sum(),
                "data_type": str(opportunities_df[col].dtype)
            }
    if not task_df.empty:
        context["task_field_info"] = {}
        for col in task_df.columns:
            sample_values = task_df[col].dropna().unique()[:5].tolist()
            context["task_field_info"][col] = {
                "sample_values": [str(v) for v in sample_values],
                "null_count": task_df[col].isnull().sum(),
                "data_type": str(task_df[col].dtype)
            }
    return context

def query_watsonx_ai(user_question, data_context, leads_df=None, cases_df=None, events_df=None, users_df=None, opportunities_df=None, task_df=None):
    #=======================================lead versus opportunity==============
    # Add detection for opportunity vs lead queries
    question_lower = user_question.lower()
    if any(keyword in question_lower for keyword in [
        "opportunity versus lead", "lead versus opportunity", 
        "% of opportunity versus lead", "% of lead versus opportunity",
        "breakdown opportunity versus lead", "show me opportunity versus lead",
        "breakdown lead versus opportunity", "show me lead versus opportunity"
    ]):
        analysis_type = "opportunity_vs_lead"
        fields = ["Lead_Converted__c", "Id"]
        explanation = "Compare the count of leads (based on Id) with opportunities (where Lead_Converted__c is True)"
        # Only set quarter if explicitly mentioned in the query
        if selected_quarter:
            explanation += f" (Filtered for {selected_quarter})"
        else:
            explanation += " (No quarter filter applied)"
    # Updated to handle both singular and plural forms
    if "disqualification reason" in user_question.lower() or "disqualification reasons" in user_question.lower():
        return {
            "analysis_type": "disqualification_summary",
            "object_type": "lead",
            "field": "Disqualification_Reason__c",
            "filters": {},
            "explanation": "Show disqualification reasons with count and percentage"
        }
        
        # Simulated logic for understanding the query (replace with actual watsonx.ai API call)
    if "percentage" in user_question.lower() and "disqualification" in user_question.lower():
    # Identify the field and filter for percentage calculation
        field = "Customer_Feedback__c"  # Since the query involves disqualification leads based on Customer_Feedback__c
        filters = {"Customer_Feedback__c": "Not Interested"}
        analysis_type = "percentage"
        
        return {
            "analysis_type": analysis_type,
            "object_type": "lead",  # Added object_type to specify the dataset
            "fields": [field],
            "filters": filters,
            "explanation": f"Calculate percentage of disqualified leads where {field} is 'Not Interested'"
        }
        
    if "percentage" in user_question.lower() and "disqualified" in user_question.lower():
        # Identify the field and filter for percentage calculation
        field = "Status"  # Since the query involves disqualified leads based on Customer_Feedback__c
        filters = {"Status": "Unqualified"}
        analysis_type = "percentage"
        
        return {
            "analysis_type": analysis_type,
            "fields": [field],  # Add the fields key with the relevant field
            "filters": filters,
            "explanation": f"Calculate percentage of Unqualified leads where {field} is 'Unqualified'"
        }
        
    if "percentage" in user_question.lower() and "unqualified" in user_question.lower():
        # Identify the field and filter for percentage calculation
        field = "Status"  # Since the query involves unqualified leads based on Customer_Feedback__c
        filters = {"Status": "Unqualified"}
        analysis_type = "percentage"
        
        return {
            "analysis_type": analysis_type,
            "fields": [field],  # Add the fields key with the relevant field
            "filters": filters,
            "explanation": f"Calculate percentage of Unqualified leads where {field} is 'Unqualified'"
        }
    
   
    
        
    
    if any(keyword in user_question.lower() for keyword in ["disqualification"]) and any(pct in user_question.lower() for pct in ["%", "percent", "percentage"]):
        return {
            "analysis_type": "percentage",
            "object_type": "lead",
            "fields": ["Customer_Feedback__c"],  # Add the field being filtered
            "filters": {"Customer_Feedback__c": "Not Interested"},
            "explanation": "Calculate percentage of disqualification leads where Customer_Feedback__c is 'Not Interested'"
        }

    
    if "junk reason" in user_question.lower():
        return {
            "analysis_type": "junk_reason_summary",
            "object_type": "lead",
            "field": "Junk_Reason__c",
            "filters": {},
            "explanation": "Show junk reasons with count and percentage"
        }
        
    # # Handle "open lead" queries
    if "open lead" in user_question.lower():
        return {
            "analysis_type": "count" if "how many" in user_question.lower() else "filter",
            "object_type": "lead",
            "filters": {"Customer_Feedback__c": {"$in": ["Discussion Pending", None]}},
            "explanation": "Count or filter leads where Customer_Feedback__c is 'Discussion Pending' or None for open lead queries"
        }

    try:
        is_valid, validation_msg = validate_watsonx_config()
        if not is_valid:
            return {"analysis_type": "error", "explanation": f"Configuration error: {validation_msg}"}

        logger.info("Getting WatsonX access token...")
        token = get_watsonx_token()

        sample_lead_fields = ', '.join(data_context['data_summary']['available_lead_fields'])
        sample_case_fields = ', '.join(data_context['data_summary']['available_case_fields'])
        sample_event_fields = ', '.join(data_context['data_summary']['available_event_fields'])
        sample_opportunity_fields = ', '.join(data_context['data_summary']['available_opportunity_fields'])
        sample_task_fields = ', '.join(data_context['data_summary']['available_task_fields'])

        # Define keyword-to-column mappings
        lead_keyword_mappings = {
            "current lead funnel": "Status",
            "disqualification reasons": "Disqualification_Reason__c",
            "conversion rates": "Status",
            "lead source subcategory": "Lead_Source_Sub_Category__c",
            "(Facebook, Google, Website)": "Lead_Source_Sub_Category__c",
            "customer feedback": "Customer_Feedback__c",
            "interested": "Customer_Feedback__c",
            "not interested": "Customer_Feedback__c",
            "property size": "Property_Size__c",
            "property type": "Property_Type__c",
            "bhk": "Property_Size__c",
            "2bhk": "Property_Size__c",
            "3bhk": "Property_Size__c",
            "residential": "Property_Type__c",
            "commercial": "Property_Type__c",
            "rating": "Property_Type__c",
            "budget range": "Budget_Range__c",
            "frequently requested product": "Project_Category__c",
            "time frame": "Preferred_Date_of_Visit__c",
            "follow up": "Follow_Up_Date_Time__c",
            "location": "Preferred_Location__c",
            "crm team member": "OwnerId",
            "lead to sale ratio": "Status",
            "time between contact and conversion": "CreatedDate",
            "follow-up consistency": "Follow_UP_Remarks__c",
            "junk lead": "Customer_Feedback__c",
            "idle lead": "Follow_Up_Date_Time__c",
            "seasonality pattern": "CreatedDate",
            "quality lead": "Rating",
            "time gap": "CreatedDate",
            "missing location": "Preferred_Location__c",
            "product preference": "Project_Category__c",
            "project": "Project__c",
            "project name": "Project__c",
            "budget preference": "Budget_Range__c",
            "campaign": "Campaign_Name__c",
            #"disqualification": "Disqualification_Reason__c",
            "open lead": "Customer_Feedback__c",
            "hot lead": "Rating",
            "cold lead": "Rating",
            "warm lead": "Rating",
            "sale": "Lead_Converted__c",
            "product sale": "Lead_Converted__c",
            "product": "Project_Category__c",
            "product name": "Project_Category__c",
            "disqualified": "Status",
            "disqualification": "Customer_Feedback__c",
            "unqualified": "Status",
            "qualified": "Status",
            "lead conversion funnel": "Status",
            "funnel analysis": "Status",
            "Junk": "Customer_Feedback__c",
            # Project categories
            "aranyam valley": "Project_Category__c",
            "armonia villa": "Project_Category__c",
            "comm booth": "Project_Category__c",
            "commercial plots": "Project_Category__c",
            "dream bazaar": "Project_Category__c",
            "dream homes": "Project_Category__c",
            "eden": "Project_Category__c",
            "eligo": "Project_Category__c",
            "ews": "Project_Category__c",
            "ews_001_(410)": "Project_Category__c",
            "executive floors": "Project_Category__c",
            "fsi": "Project_Category__c",
            "generic": "Project_Category__c",
            "golf range": "Project_Category__c",
            "harmony greens": "Project_Category__c",
            "hssc": "Project_Category__c",
            "hubb": "Project_Category__c",
            "institutional": "Project_Category__c",
            "institutional_we": "Project_Category__c",
            "lig": "Project_Category__c",
            "lig_001_(310)": "Project_Category__c",
            "livork": "Project_Category__c",
            "mayfair park": "Project_Category__c",
            "new plots": "Project_Category__c",
            "none": "Project_Category__c",
            "old plots": "Project_Category__c",
            "plot-res-if": "Project_Category__c",
            "plots-comm": "Project_Category__c",
            "plots-res": "Project_Category__c",
            "prime floors": "Project_Category__c",
            "sco": "Project_Category__c",
            "sco.": "Project_Category__c",
            "swamanorath": "Project_Category__c",
            "trucia": "Project_Category__c",
            "veridia": "Project_Category__c",
            "veridia-3": "Project_Category__c",
            "veridia-4": "Project_Category__c",
            "veridia-5": "Project_Category__c",
            "veridia-6": "Project_Category__c",
            "veridia-7": "Project_Category__c",
            "villas": "Project_Category__c",
            "wave floor": "Project_Category__c",
            "wave floor 85": "Project_Category__c",
            "wave floor 99": "Project_Category__c",
            "wave galleria": "Project_Category__c",
            "wave garden": "Project_Category__c",
            "wave garden gh2-ph-2": "Project_Category__c"
        }

        case_keyword_mappings = {
            "case type": "Type",
            "feedback": "Feedback__c",
            "service request": "Service_Request_Number__c",
            "origin": "Origin",
            "closure remark": "Corporate_Closure_Remark__c"
        }

        event_keyword_mappings = {
            "event status": "Appointment_Status__c",
            "scheduled event": "Appointment_Status__c",
            "cancelled event": "Appointment_Status__c",
            "total appointments":"Appointment_status__c",
        }

        opportunity_keyword_mappings = {
            "opportunity stage": "StageName",
            "closed won": "StageName",
            "closed lost": "StageName",
            "negotiation": "StageName",
            "amount": "Amount",
            "close date": "CloseDate",
            "opportunity type": "Opportunity_Type__c",
            "new business": "Opportunity_Type__c",
            "renewal": "Opportunity_Type__c",
            "upsell": "Opportunity_Type__c",
            "cross-sell": "Opportunity_Type__c"
        }

        task_keyword_mappings = {
            "task status": "Status",
            "follow up status": "Follow_Up_Status__c",
            "task feedback": "Customer_Feedback__c",
            "sales feedback": "Sales_Team_Feedback__c",
            "transfer status": "Transfer_Status__c",
            "task subject": "Subject",
            "completed task": "Status",
            "open task": "Status",
            "pending follow-up": "Follow_Up_Status__c",
            "no follow-up": "Follow_Up_Status__c"
            
        }

        # Detect quarter from user question
        quarter_mapping = {
            r'\b(q1|quarter\s*1|first\s*quarter)\b': 'Q1 2024-25',
            r'\b(q2|quarter\s*2|second\s*quarter)\b': 'Q2 2024-25',
            r'\b(q3|quarter\s*3|third\s*quarter)\b': 'Q3 2024-25',
            r'\b(q4|quarter\s*4|fourth\s*quarter)\b': 'Q4 2024-25',
        }
        selected_quarter = None
        question_lower = user_question.lower()
        for pattern, quarter in quarter_mapping.items():
            if re.search(pattern, question_lower, re.IGNORECASE):
                selected_quarter = quarter
                logger.info(f"Detected quarter: {selected_quarter} for query: {user_question}")
                break
        # Default to Q4 2024-25 for quarterly_distribution if no quarter specified
        if "quarter" in question_lower and not selected_quarter:
            selected_quarter = "Q4 2024-25"
            logger.info(f"No specific quarter detected, defaulting to {selected_quarter}")

        system_prompt = f"""
You are an intelligent Salesforce analytics assistant. Your task is to convert user questions into a JSON-based analysis plan for lead, case, event, opportunity, or task data.

Available lead fields: {sample_lead_fields}
Available case fields: {sample_case_fields}
Available event fields: {sample_event_fields}
Available opportunity fields: {sample_opportunity_fields}
Available task fields: {sample_task_fields}

## Keyword-to-Column Mappings
### Lead Data Mappings:
{json.dumps(lead_keyword_mappings, indent=2)}
### Case Data Mappings:
{json.dumps(case_keyword_mappings, indent=2)}
### Event Data Mappings:
{json.dumps(event_keyword_mappings, indent=2)}
### Opportunity Data Mappings:
{json.dumps(opportunity_keyword_mappings, indent=2)}
### Task Data Mappings:
{json.dumps(task_keyword_mappings, indent=2)}

## Instructions:
- Detect if the question pertains to leads, cases, events, opportunities, or tasks based on keywords like "lead", "case", "event", "opportunity", or "task".
- Use keyword-to-column mappings to select the correct field (e.g., "disqualification reason" → `Disqualification_Reason__c`).
- For terms like "2BHK", "3BHK", filter `Property_Size__c` (e.g., `Property_Size__c: ["2BHK", "3BHK"]`).
- For "residential" or "commercial", filter `Property_Type__c` (e.g., `Property_Type__c: "Residential"`).
- For project categories (e.g., "ARANYAM VALLEY"), filter `Project_Category__c` (e.g., `Project_Category__c: "ARANYAM VALLEY"`).
- For "interested", filter `Customer_Feedback__c = "Interested"`.
- For "hot lead", "cold lead", "warm lead", filter `Rating` (e.g., `Rating: "Hot"`).
- For "qualified", filter `Customer_Feedback__c = "Interested"`.
- For "disqualified", "disqualification", or "unqualified", filter `Customer_Feedback__c = "Not Interested"`.
- For "sale", filter `Lead_Converted__c = true`.
- For "open lead", filter `Customer_Feedback__c` in `["Discussion Pending", null]` (i.e., `Customer_Feedback__c: {{"$in": ["Discussion Pending", null]}}`).
- For "opportunity versus lead" or "lead versus opportunity" queries (including "how many", "breakdown", "show me", or "%"), set `analysis_type` to `opportunity_vs_lead` for counts or `opportunity_vs_lead_percentage` for percentages. Use `Lead_Converted__c = true` for opportunities and count all `Id` for leads.
- Data is available from 2024-04-01T00:00:00Z to 2025-03-31T23:59:59Z. Adjust dates outside this range to the nearest valid date.
- For date-specific queries (e.g., "4 January 2024"), filter `CreatedDate` for that date.
- For "today", use 2025-06-13T00:00:00Z to 2025-06-13T23:59:59Z (UTC).
- For "last week" or "last month", calculate relative to 2025-06-13T00:00:00Z (UTC).
- For Hinglish like "2025 ka data", filter `CreatedDate` for that year.

- For non-null filters, use `{{"$ne": null}}`.
- If the user mentions "task status", use the `Status` field for tasks.

- If the user mentions "Total Appointment",use the `Appointment_Status__c` is in ["Completed",""Scheduled","Cancelled","No show"] within the `conversion_funnel` analysis.
- If the user mentions "completed task", map to `Status` with value "Completed" for tasks.
- If the user mentions "pending follow-up", map to `Follow_Up_Status__c` with value "Pending" for tasks.
- If the user mentions "interested", map to `Customer_Feedback__c` with value "Interested" for leads or tasks.
- If the user mentions "not interested", map to `Customer_Feedback__c` with value "Not Interested" for leads or tasks.
- If the user mentions "meeting done", map to `Appointment_Status__c` with value "Completed" for events.
- If the user mentions "meeting booked", map to `Appointment_Status__c` with value "Scheduled" for tasks.

## Quarter Detection:
- Detect quarters from keywords:
  - "Q1", "quarter 1", "first quarter" → "Q1 2024-25" (2024-04-01T00:00:00Z to 2024-06-30T23:59:59Z)
  - "Q2", "quarter 2", "second quarter" → "Q2 2024-25" (2024-07-01T00:00:00Z to 2024-09-30T23:59:59Z)
  - "Q3", "quarter 3", "third quarter" → "Q3 2024-25" (2024-10-01T00:00:00Z to 2024-12-31T23:59:59Z)
  - "Q4", "quarter 4", "fourth quarter" → "Q4 2024-25" (2025-01-01T00:00:00Z to 2025-03-31T23:59:59Z)
- For `quarterly_distribution`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
- If no quarter is specified for `quarterly_distribution`, default to "Q4 2024-25".
- For `quarterly_distribution` or `opportunity_vs_lead`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
- If no quarter is specified for `quarterly_distribution` or `opportunity_vs_lead`, default to "Q4 2024-25".

## Analysis Types:
- count: Count records.
- distribution: Frequency of values.
- filter: List records.
- recent: Recent records.
- top: Top values.
- percentage: Percentage of matching records.
- quarterly_distribution: Group by quarters.
- source_wise_funnel: Group by `LeadSource` and `Lead_Source_Sub_Category__c`.
- conversion_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, etc.).
- opportunity_vs_lead: Compare count of leads (all `Id`) with opportunities (`Lead_Converted__c = true`).
- opportunity_vs_lead_percentage: Calculate percentage of leads converted to opportunities (`Lead_Converted__c = true` / total leads).

## Lead Conversion Funnel:
For "lead conversion funnel" or "funnel analysis":
- `analysis_type`: "conversion_funnel"
- Fields: `["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c"]`
- Metrics:
  - Total Leads: All leads.
  - Valid Leads: `Customer_Feedback__c != "Junk"`.
  - SOL: `Status = "Qualified"`.
  - Meeting Booked: `Status = "Qualified"` and `Is_Appointment_Booked__c = True`.
  - Disqualified Leads: `Customer_Feedback__c = "Not Interested"`.
  - Open Leads: `Customer_Feedback__c` in `["Discussion Pending", None]`.
  - Total Appointment : `Appointment_Status__c` in `["Completed",""Scheduled","Cancelled","No show"]`.
  - Junk %: ((Total Leads - Valid Leads) / Total Leads) * 100.
  - VL:SOL: Valid Leads / SOL.
  - SOL:MB: SOL / Meeting Booked.
  - MB:MD: Meeting Booked / Meeting Done (using events data where `Appointment_Status__c = "Completed"` for Meeting Done).
  - Meeting Done: Count Events where `Appointment_Status__c = "Completed"`.

- For tasks:
  - "completed task" → Use `Status = "Completed"`.
  - "open task" → Use `Status = "Open"`.
  - "pending follow-up" → Use `Follow_Up_Status__c = "Pending"`.
  - "no follow-up" → Use `Follow_Up_Status__c = "None"`.
  - "interested" → Use `Customer_Feedback__c = "Interested"`.
  - "not interested" → Use `Customer_Feedback__c = "Not Interested"`.
  - "meeting done" → Use `Appointment_Status__c = "Completed"`.
  - "meeting booked" → Use `Appointment_Status__c = "Scheduled"`.

## Quarterly Distribution:
For "product wise sale" or "quarterly" queries:
- `analysis_type`: "quarterly_distribution"
- Field: `Lead_Converted__c` for sales.
- Include `quarter` (e.g., `quarter: "Q1 2024-25"`).
- For tasks, use fields like `Status` or `Follow_Up_Status__c` to show distributions.

## JSON Response Format:
{{
  "analysis_type": "type_name",
  "object_type": "lead" or "case" or "event" or "opportunity" or "task",
  "field": "field_name",
  "fields": ["field_name"],
  "filters": {{"field1": "value1", "field2": {{"$ne": null}}}},
  "quarter": "Q1 2024-25" or "Q2 2024-25" or "Q3 2024-25" or "Q4 2024-25",
  "limit": 10,
  "explanation": "Explain what will be done"
}}

User Question: {user_question}

Respond with valid JSON only.
"""

        ml_url = f"{watsonx_url}/ml/v1/text/generation?version=2023-07-07"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {
            "input": system_prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 400,
                "temperature": 0.2,
                "repetition_penalty": 1.1,
                "stop_sequences": ["\n\n"]
            },
            "model_id": watsonx_model_id,
            "project_id": watsonx_project_id
        }

        logger.info(f"Querying WatsonX AI with model: {watsonx_model_id}")
        response = requests.post(ml_url, headers=headers, json=body, timeout=90)

        if response.status_code != 200:
            error_msg = f"WatsonX AI Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {"analysis_type": "error", "message": error_msg}

        result = response.json()
        generated_text = result.get("results", [{}])[0].get("generated_text", "").strip()
        logger.info(f"WatsonX generated response: {generated_text}")

        try:
            # Extract JSON from response
            generated_text = re.sub(r'```json\n?', '', generated_text)
            generated_text = re.sub(r'\n?```', '', generated_text)
            generated_text = re.sub(r'\b null\b', 'null', generated_text)
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Extracted JSON string: {json_str}")
                analysis_plan = json.loads(json_str)

                # Set defaults
                if "analysis_type" not in analysis_plan:
                    analysis_plan["analysis_type"] = "filter"
                if "explanation" not in analysis_plan:
                    analysis_plan["explanation"] = "Analysis based on user question"
                if "object_type" not in analysis_plan:
                    analysis_plan["object_type"] = "lead"
                    if "lead" in user_question.lower():
                        analysis_plan["object_type"] = "lead"
                    elif "case" in user_question.lower():
                        analysis_plan["object_type"] = "case"
                    elif "event" in user_question.lower():
                        analysis_plan["object_type"] = "event"
                    elif "opportunity" in user_question.lower():
                        analysis_plan["object_type"] = "opportunity"
                    elif "task" in user_question.lower():
                        analysis_plan["object_type"] = "task"

                # Add quarter to analysis_plan
                if selected_quarter:
                    analysis_plan["quarter"] = selected_quarter
                    analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
                elif analysis_plan["analysis_type"] == "quarterly_distribution":
                    analysis_plan["quarter"] = "Q4 2024-25"  # Default
                    analysis_plan["explanation"] += " (Defaulted to Q4 2024-25)"

                # Handle filters
                if "filters" in analysis_plan:
                    for field, condition in analysis_plan["filters"].items():
                        if isinstance(condition, dict) and "$ne" in condition and condition["$ne"] == "null":
                            condition["$ne"] = None
                        elif isinstance(condition, dict):
                            for key, value in condition.items():
                                if value == "null":
                                    condition[key] = None
                        elif condition == "null":
                            analysis_plan["filters"][field] = None

                logger.info(f"Parsed analysis plan: {analysis_plan}")
                return analysis_plan
            else:
                logger.warning("No valid JSON found in WatsonX response")
                return parse_intent_fallback(user_question, generated_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            return parse_intent_fallback(user_question, generated_text)

    except Exception as e:
        error_msg = f"WatsonX query failed: {str(e)}"
        logger.error(error_msg)
        return {"analysis_type": "error", "explanation": error_msg}

def parse_intent_fallback(user_question, ai_response):
    question_lower = user_question.lower()
    filters = {}
    object_type = "lead"
    if "lead" in question_lower:
        object_type = "lead"
    elif "case" in question_lower:
        object_type = "case"
    elif "event" in question_lower:
        object_type = "event"
    elif "opportunity" in question_lower:
        object_type = "opportunity"
    elif "task" in question_lower:
        object_type = "task"

    # Detect quarter
    quarter_mapping = {
        r'\b(q1|quarter\s*1|first\s*quarter)\b': 'Q1 2024-25',
        r'\b(q2|quarter\s*2|second\s*quarter)\b': 'Q2 2024-25',
        r'\b(q3|quarter\s*3|third\s*quarter)\b': 'Q3 2024-25',
        r'\b(q4|quarter\s*4|fourth\s*quarter)\b': 'Q4 2024-25',
    }
    selected_quarter = None
    for pattern, quarter in quarter_mapping.items():
        if re.search(pattern, question_lower, re.IGNORECASE):
            selected_quarter = quarter
            break

    # Handle specific filters
    if object_type == "lead":
        if "disqualification" in question_lower :
            filters["Customer_Feedback__c"] = "Not Interested"
        elif "interested" in question_lower and "not interested" not in question_lower:
            filters["Customer_Feedback__c"] = "Interested"
        elif "not interested" in question_lower:
            filters["Customer_Feedback__c"] = "Not Interested"
        elif "qualified" in question_lower:
            filters["Status"] = "Qualified"
        elif "unqualified" in question_lower:
            filters["Status"] = "Unqualified"
        elif "interested" in question_lower:
            filters["Customer_Feedback__c"] = "Interested"
            
        elif "open lead" in question_lower:
            filters["Customer_Feedback__c"] = {"$in": ["Discussion Pending", None]}
        elif "hot lead" in question_lower:
            filters["Rating"] = "Hot"
        elif "cold lead" in question_lower:
            filters["Rating"] = "Cold"
        elif "warm lead" in question_lower:
            filters["Rating"] = "Warm"
        elif "junk lead" in question_lower:
            filters["Customer_Feedback__c"] = "Junk"
        elif "sale" in question_lower:
            filters["Lead_Converted__c"] = True
        elif "completed task" in question_lower:
            filters["Status"] = "Completed"
            
        elif "completed event" in question_lower:
            filters["Appointment_Status__c"] = "Completed"
        elif "product sale" in question_lower:
            analysis_plan = {
                "analysis_type": "quarterly_distribution",
                "object_type": "lead",
                "fields": ["Lead_Converted__c"],
                "filters": {},
                "explanation": "Showing distribution of Lead_Converted__c for each quarter to represent sales"
            }
            if selected_quarter:
                analysis_plan["quarter"] = selected_quarter
                analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
            return analysis_plan

    # Handle date filters
    current_date_utc = pd.to_datetime("2025-06-13T09:38:00Z", utc=True)  # 03:08 PM IST = 09:38 UTC
    data_start = pd.to_datetime("2024-04-01T00:00:00Z", utc=True)
    data_end = pd.to_datetime("2025-03-31T23:59:59Z", utc=True)

    if "today" in question_lower:
        filters["CreatedDate"] = {
            "$gte": current_date_utc.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": current_date_utc.strftime("%Y-%m-%dT23:59:59Z")
        }
    elif "last week" in question_lower:
        last_week_end = current_date_utc - pd.Timedelta(days=current_date_utc.weekday() + 1)
        last_week_start = last_week_end - pd.Timedelta(days=6)
        last_week_start = max(last_week_start, data_start)
        last_week_end = min(last_week_end, data_end)
        filters["CreatedDate"] = {
            "$gte": last_week_start.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": last_week_end.strftime("%Y-%m-%dT23:59:59Z")
        }
    elif "last month" in question_lower:
        last_month_end = (current_date_utc.replace(day=1) - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)
        last_month_start = max(last_month_start, data_start)
        last_month_end = min(last_month_end, data_end)
        filters["CreatedDate"] = {
            "$gte": last_month_start.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": last_month_end.strftime("%Y-%m-%dT23:59:59Z")
        }

    date_pattern = r'\b(\d{1,2})(?:th|rd|st|nd)?\s*(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec)\s*(\d{4})\b'
    date_match = re.search(date_pattern, question_lower, re.IGNORECASE)
    if date_match:
        day = int(date_match.group(1))
        month_str = date_match.group(2).lower()
        year = int(date_match.group(3))
        month_mapping = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
            'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
            'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }
        month = month_mapping.get(month_str)
        if month:
            try:
                specific_date = pd.to_datetime(f"{year}-{month}-{day}T00:00:00Z", utc=True)
                date_str = specific_date.strftime('%Y-%m-%d')
                filters["CreatedDate"] = {
                    "$gte": f"{date_str}T00:00:00Z",
                    "$lte": f"{date_str}T23:59:59Z"
                }
            except ValueError as e:
                logger.warning(f"Invalid date parsed: {e}")
                return {
                    "analysis_type": "error",
                    "explanation": f"Invalid date specified: {e}"
                }

    hinglish_year_pattern = r'\b(\d{4})\s*ka\s*data\b'
    hinglish_year_match = re.search(hinglish_year_pattern, question_lower, re.IGNORECASE)
    if hinglish_year_match:
        year = hinglish_year_match.group(1)
        year_start = pd.to_datetime(f"{year}-01-01T00:00:00Z", utc=True)
        year_end = pd.to_datetime(f"{year}-12-31T23:59:59Z", utc=True)
        gte = max(year_start, data_start)
        lte = min(year_end, data_end)
        filters["CreatedDate"] = {
            "$gte": gte.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": lte.strftime("%Y-%m-%dT23:59:59Z")
        }

    analysis_plan = {
        "analysis_type": "filter",
        "object_type": object_type,
        "filters": filters,
        "explanation": f"Filtering {object_type} records for: {user_question}"
    }
    if selected_quarter:
        analysis_plan["quarter"] = selected_quarter
        analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
    return analysis_plan