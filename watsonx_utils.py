
# import requests
# import json
# import re
# import pandas as pd
# from config import WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL, WATSONX_MODEL_ID, IBM_CLOUD_IAM_URL, logger

# def validate_watsonx_config():
#     missing_configs = []
#     if not WATSONX_API_KEY:
#         missing_configs.append("WATSONX_API_KEY")
#     if not WATSONX_PROJECT_ID:
#         missing_configs.append("WATSONX_PROJECT_ID")
#     if missing_configs:
#         error_msg = f"Missing WatsonX configuration: {', '.join(missing_configs)}"
#         logger.error(error_msg)
#         return False, error_msg
#     if len(WATSONX_API_KEY.strip()) < 10:
#         return False, "WATSONX_API_KEY appears to be invalid (too short)"
#     if len(WATSONX_PROJECT_ID.strip()) < 10:
#         return False, "WATSONX_PROJECT_ID appears to be invalid (too short)"
#     return True, "Configuration valid"

# def get_watsonx_token():
#     is_valid, validation_msg = validate_watsonx_config()
#     if not is_valid:
#         raise ValueError(f"Configuration error: {validation_msg}")
#     headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
#     data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_API_KEY.strip()}
#     logger.info("Requesting IBM Cloud IAM token...")
#     try:
#         response = requests.post(IBM_CLOUD_IAM_URL, headers=headers, data=data, timeout=90)
#         logger.info(f"IAM Token Response Status: {response.status_code}")
#         if response.status_code == 200:
#             token_data = response.json()
#             access_token = token_data.get("access_token")
#             if not access_token:
#                 raise ValueError("No access_token in response")
#             logger.info("Successfully obtained IAM token")
#             return access_token
#         else:
#             error_details = {
#                 "status_code": response.status_code,
#                 "response_text": response.text[:1000],
#                 "headers": dict(response.headers),
#                 "request_body": data
#             }
#             logger.error(f"IAM Token request failed: {error_details}")
#             raise requests.exceptions.HTTPError(f"IAM API Error {response.status_code}: {response.text}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"IAM Token request exception: {str(e)}")
#         raise

# def create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df):
#     context = {
#         "data_summary": {
#             "total_leads": len(leads_df),
#             "total_users": len(users_df),
#             "total_cases": len(cases_df),
#             "total_events": len(events_df),
#             "total_opportunities": len(opportunities_df),
#             "total_tasks": len(task_df),
#             "available_lead_fields": list(leads_df.columns) if not leads_df.empty else [],
#             "available_user_fields": list(users_df.columns) if not users_df.empty else [],
#             "available_case_fields": list(cases_df.columns) if not cases_df.empty else [],
#             "available_event_fields": list(events_df.columns) if not leads_df.empty else [],
#             "available_opportunity_fields": list(opportunities_df.columns) if not opportunities_df.empty else [],
#             "available_task_fields": list(task_df.columns) if not task_df.empty else []
#         }
#     }
#     if not leads_df.empty:
#         context["lead_field_info"] = {}
#         for col in leads_df.columns:
#             sample_values = leads_df[col].dropna().unique()[:5].tolist()
#             context["lead_field_info"][col] = {
#                 "sample_values": [str(v) for v in sample_values],
#                 "null_count": leads_df[col].isnull().sum(),
#                 "data_type": str(leads_df[col].dtype)
#             }
#     if not cases_df.empty:
#         context["case_field_info"] = {}
#         for col in cases_df.columns:
#             sample_values = cases_df[col].dropna().unique()[:5].tolist()
#             context["case_field_info"][col] = {
#                 "sample_values": [str(v) for v in sample_values],
#                 "null_count": cases_df[col].isnull().sum(),
#                 "data_type": str(cases_df[col].dtype)
#             }
#     if not events_df.empty:
#         context["event_field_info"] = {}
#         for col in events_df.columns:
#             sample_values = events_df[col].dropna().unique()[:5].tolist()
#             context["event_field_info"][col] = {
#                 "sample_values": [str(v) for v in sample_values],
#                 "null_count": events_df[col].isnull().sum(),
#                 "data_type": str(events_df[col].dtype)
#             }
#     if not opportunities_df.empty:
#         context["opportunity_field_info"] = {}
#         for col in opportunities_df.columns:
#             sample_values = opportunities_df[col].dropna().unique()[:5].tolist()
#             context["opportunity_field_info"][col] = {
#                 "sample_values": [str(v) for v in sample_values],
#                 "null_count": opportunities_df[col].isnull().sum(),
#                 "data_type": str(opportunities_df[col].dtype)
#             }
#     if not task_df.empty:
#         context["task_field_info"] = {}
#         for col in task_df.columns:
#             sample_values = task_df[col].dropna().unique()[:5].tolist()
#             context["task_field_info"][col] = {
#                 "sample_values": [str(v) for v in sample_values],
#                 "null_count": task_df[col].isnull().sum(),
#                 "data_type": str(task_df[col].dtype)
#             }
#     return context

# def query_watsonx_ai(user_question, data_context, leads_df=None, cases_df=None, events_df=None, users_df=None, opportunities_df=None, task_df=None):
#     try:
#         is_valid, validation_msg = validate_watsonx_config()
#         if not is_valid:
#             return {"analysis_type": "error", "explanation": f"Configuration error: {validation_msg}"}

#         logger.info("Getting WatsonX access token...")
#         token = get_watsonx_token()

#         sample_lead_fields = ', '.join(data_context['data_summary']['available_lead_fields'])
#         sample_user_fields = ', '.join(data_context['data_summary']['available_user_fields'])
#         sample_case_fields = ', '.join(data_context['data_summary']['available_case_fields'])
#         sample_event_fields = ', '.join(data_context['data_summary']['available_event_fields'])
#         sample_opportunity_fields = ', '.join(data_context['data_summary']['available_opportunity_fields'])
#         sample_task_fields = ', '.join(data_context['data_summary']['available_task_fields'])

#         # Detect new funnel queries
#         if any(keyword in user_question.lower() for keyword in ["product wise funnel", "product-wise funnel"]):
#             return {
#                 "analysis_type": "product_wise_funnel",
#                 "object_type": "lead",
#                 "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "Project_Category__c"],
#                 "group_by": "Project_Category__c",
#                 "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by Project_Category__c"
#             }
#         if any(keyword in user_question.lower() for keyword in ["source wise funnel", "source-wise funnel"]):
#             return {
#                 "analysis_type": "source_wise_funnel",
#                 "object_type": "lead",
#                 "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "LeadSource"],
#                 "group_by": "LeadSource",
#                 "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by LeadSource"
#             }
#         if any(keyword in user_question.lower() for keyword in ["user wise funnel", "user-wise funnel"]):
#             return {
#                 "analysis_type": "user_wise_funnel",
#                 "object_type": "lead",
#                 "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "OwnerId"],
#                 "group_by": "OwnerId",
#                 "join": {"table": "users_df", "left_on": "OwnerId", "right_on": "Id", "fields": ["Name"]},
#                 "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by OwnerId, joining with users_df to display user names"
#             }

#         # Detect user-wise sales queries
#         if any(keyword in user_question.lower() for keyword in ["sale by user", "user wise sale", "user-wise sale", "sales by user"]):
#             return {
#                 "analysis_type": "user_sales_summary",
#                 "object_type": "opportunity",
#                 "fields": ["OwnerId", "Sales_Order_Number__c"],
#                 "filters": {"Sales_Order_Number__c": {"$ne": None}},
#                 "explanation": "Show count of closed-won opportunities grouped by user"
#             }
            
#         if "user wise meeting done" in user_question.lower():
#             return {
#                 "analysis_type": "user_meeting_summary",
#                 "object_type": "event",
#                 "fields": ["OwnerId", "Appointment_Status__c"],
#                 "filters": {"Appointment_Status__c": "Completed"},
#                 "explanation": "Show count of completed meetings grouped by user"
#             }
#         if "department wise meeting done" in user_question.lower():
#             return {
#                 "analysis_type": "dept_user_meeting_summary",
#                 "object_type": "event",
#                 "fields": ["OwnerId", "Appointment_Status__c", "Department"],
#                 "filters": {"Appointment_Status__c": "Completed"},
#                 "explanation": "Show count of completed meetings grouped by user and department"
#             }
            
#         if "total meeting done" in user_question.lower():
#             return {
#                 "analysis_type": "count",
#                 "object_type": "event",
#                 "fields": ["Appointment_Status__c"],
#                 "filters": {"Appointment_Status__c": "Completed"},
#                 "explanation": "Show total count of completed meetings"
#             }
        
#         # Updated to handle both singular and plural forms
#         if "disqualification reason" in user_question.lower() or "disqualification reasons" in user_question.lower():
#             return {
#                 "analysis_type": "disqualification_summary",
#                 "object_type": "lead",
#                 "field": "Disqualification_Reason__c",
#                 "filters": {},
#                 "explanation": "Show disqualification reasons with count and percentage"
#             }
            
#         if "junk reason" in user_question.lower():
#             return {
#                 "analysis_type": "junk_reason_summary",
#                 "object_type": "lead",
#                 "field": "Junk_Reason__c",
#                 "filters": {},
#                 "explanation": "Show junk reasons with count and percentage"
#             }
            
#         if any(keyword in user_question.lower() for keyword in ["disqualification"]) and any(pct in user_question.lower() for pct in ["%", "percent", "percentage"]):
#             return {
#                 "analysis_type": "percentage",
#                 "object_type": "lead",
#                 "fields": ["Customer_Feedback__c"],
#                 "filters": {"Customer_Feedback__c": "Not Interested"},
#                 "explanation": "Calculate percentage of disqualification leads where Customer_Feedback__c is 'Not Interested'"
#             }

#         # Define keyword-to-column mappings
#         lead_keyword_mappings = {
#             "current lead funnel": "Status",
#             "disqualification reasons": "Disqualification_Reason__c",
#             "conversion rates": "Status",
#             "lead source subcategory": "Lead_Source_Sub_Category__c",
#             "(Facebook, Google, Website)": "Lead_Source_Sub_Category__c",
#             "customer feedback": "Customer_Feedback__c",
#             "interested": "Customer_Feedback__c",
#             "not interested": "Customer_Feedback__c",
#             "property size": "Property_Size__c",
#             "property type": "Property_Type__c",
#             "bhk": "Property_Size__c",
#             "2bhk": "Property_Size__c",
#             "3bhk": "Property_Size__c",
#             "residential": "Property_Type__c",
#             "commercial": "Property_Type__c",
#             "rating": "Property_Type__c",
#             "budget range": "Budget_Range__c",
#             "frequently requested product": "Project_Category__c",
#             "time frame": "Preferred_Date_of_Visit__c",
#             "follow up": "Follow_Up_Date_Time__c",
#             "location": "Preferred_Location__c",
#             "crm team member": "OwnerId",
#             "lead to sale ratio": "Status",
#             "time between contact and conversion": "CreatedDate",
#             "follow-up consistency": "Follow_UP_Remarks__c",
#             "junk lead": "Customer_Feedback__c",
#             "idle lead": "Follow_Up_Date_Time__c",
#             "seasonality pattern": "CreatedDate",
#             "quality lead": "Rating",
#             "time gap": "CreatedDate",
#             "missing location": "Preferred_Location__c",
#             "product preference": "Project_Category__c",
#             "project": "Project__c",
#             "project name": "Project__c",
#             "budget preference": "Budget_Range__c",
#             "campaign": "Campaign_Name__c",
#             "open lead": "Customer_Feedback__c",
#             "hot lead": "Rating",
#             "cold lead": "Rating",
#             "warm lead": "Rating",
#             "product": "Project_Category__c",
#             "product name": "Project_Category__c",
#             "disqualified": "Status",
#             "disqualification": "Customer_Feedback__c",
#             "unqualified": "Status",
#             "qualified": "Status",
#             "lead conversion funnel": "Status",
#             "funnel analysis": "Status",
#             "Junk": "Customer_Feedback__c",
#             "aranyam valley": "Project_Category__c",
#             "armonia villa": "Project_Category__c",
#             "comm booth": "Project_Category__c",
#             "commercial plots": "Project_Category__c",
#             "dream bazaar": "Project_Category__c",
#             "dream homes": "Project_Category__c",
#             "eden": "Project_Category__c",
#             "eligo": "Project_Category__c",
#             "ews": "Project_Category__c",
#             "ews_001_(410)": "Project_Category__c",
#             "executive floors": "Project_Category__c",
#             "fsi": "Project_Category__c",
#             "generic": "Project_Category__c",
#             "golf range": "Project_Category__c",
#             "harmony greens": "Project_Category__c",
#             "hssc": "Project_Category__c",
#             "hubb": "Project_Category__c",
#             "institutional": "Project_Category__c",
#             "institutional_we": "Project_Category__c",
#             "lig": "Project_Category__c",
#             "lig_001_(310)": "Project_Category__c",
#             "livork": "Project_Category__c",
#             "mayfair park": "Project_Category__c",
#             "new plots": "Project_Category__c",
#             "none": "Project_Category__c",
#             "old plots": "Project_Category__c",
#             "plot-res-if": "Project_Category__c",
#             "plots-comm": "Project_Category__c",
#             "plots-res": "Project_Category__c",
#             "prime floors": "Project_Category__c",
#             "sco": "Project_Category__c",
#             "sco.": "Project_Category__c",
#             "swamanorath": "Project_Category__c",
#             "trucia": "Project_Category__c",
#             "veridia": "Project_Category__c",
#             "veridia-3": "Project_Category__c",
#             "veridia-4": "Project_Category__c",
#             "veridia-5": "Project_Category__c",
#             "veridia-6": "Project_Category__c",
#             "veridia-7": "Project_Category__c",
#             "villas": "Project_Category__c",
#             "wave floor": "Project_Category__c",
#             "wave floor 85": "Project_Category__c",
#             "wave floor 99": "Project_Category__c",
#             "wave galleria": "Project_Category__c",
#             "wave garden": "Project_Category__c",
#             "wave garden gh2-ph-2": "Project_Category__c"
#         }

#         case_keyword_mappings = {
#             "case type": "Type",
#             "feedback": "Feedback__c",
#             "service request": "Service_Request_Number__c",
#             "origin": "Origin",
#             "closure remark": "Corporate_Closure_Remark__c"
#         }

#         event_keyword_mappings = {
#             "event status": "Appointment_Status__c",
#             "scheduled event": "Appointment_Status__c",
#             "cancelled event": "Appointment_Status__c",
#             "total appointments": "Appointment_status__c",
#             "user wise meeting done": ["OwnerId", "Appointment_Status__c"]
#         }

#         opportunity_keyword_mappings = {
#             "qualified opportunity": "Sales_Team_Feedback__c",
#             "disqualified opportunity": "Sales_Team_Feedback__c",
#             "amount": "Amount",
#             "close date": "CloseDate",
#             "opportunity type": "Opportunity_Type__c",
#             "new business": "Opportunity_Type__c",
#             "renewal": "Opportunity_Type__c",
#             "upsell": "Opportunity_Type__c",
#             "cross-sell": "Opportunity_Type__c",
#             "total sale": "Sales_Order_Number__c",
#             "source-wise sale": "LeadSource",
#             "source with sale": "LeadSource",
#             "lead source subcategory with sale": "Lead_Source_Sub_Category__c",
#             "subcategory with sale": "Lead_Source_Sub_Category__c",
#             "product-wise sales": "Project_Category__c",
#             "products with sales": "Project_Category__c",
#             "product sale": "Project_Category__c",
#             "project-wise sales": "Project__c",
#             "project with sale": "Project__c",
#             "project sale": "Project__c",
#             "sales by user": "OwnerId",
#             "user-wise sale": "OwnerId"
#         }

#         task_keyword_mappings = {
#             "task status": "Status",
#             "follow up status": "Follow_Up_Status__c",
#             "task feedback": "Customer_Feedback__c",
#             "sales feedback": "Sales_Team_Feedback__c",
#             "transfer status": "Transfer_Status__c",
#             "task subject": "Subject",
#             "completed task": "Status",
#             "open task": "Status",
#             "pending follow-up": "Follow_Up_Status__c",
#             "no follow-up": "Follow_Up_Status__c"
#         }

#         # Detect quarter from user question
#         quarter_mapping = {
#             r'\b(q1|quarter\s*1|first\s*quarter)\b': 'Q1 2024-25',
#             r'\b(q2|quarter\s*2|second\s*quarter)\b': 'Q2 2024-25',
#             r'\b(q3|quarter\s*3|third\s*quarter)\b': 'Q3 2024-25',
#             r'\b(q4|quarter\s*4|fourth\s*quarter)\b': 'Q4 2024-25',
#         }
#         selected_quarter = None
#         question_lower = user_question.lower()
#         for pattern, quarter in quarter_mapping.items():
#             if re.search(pattern, question_lower, re.IGNORECASE):
#                 selected_quarter = quarter
#                 logger.info(f"Detected quarter: {selected_quarter} for query: {user_question}")
#                 break
#         if "quarter" in question_lower and not selected_quarter:
#             selected_quarter = "Q4 2024-25"
#             logger.info(f"No specific quarter detected, defaulting to {selected_quarter}")

#         system_prompt = f"""
# You are an intelligent Salesforce analytics assistant. Your task is to convert user questions into a JSON-based analysis plan for lead, case, event, opportunity, or task data.

# Available lead fields: {sample_lead_fields}
# Available user fields: {sample_user_fields}
# Available case fields: {sample_case_fields}
# Available event fields: {sample_event_fields}
# Available opportunity fields: {sample_opportunity_fields}
# Available task fields: {sample_task_fields}

# ## Keyword-to-Column Mappings
# ### Lead Data Mappings:
# {json.dumps(lead_keyword_mappings, indent=2)}
# ### Case Data Mappings:
# {json.dumps(case_keyword_mappings, indent=2)}
# ### Event Data Mappings:
# {json.dumps(event_keyword_mappings, indent=2)}
# ### Opportunity Data Mappings:
# {json.dumps(opportunity_keyword_mappings, indent=2)}
# ### Task Data Mappings:
# {json.dumps(task_keyword_mappings, indent=2)}

# ## Instructions:
# - Detect if the question pertains to leads, cases, events, opportunities, or tasks based on keywords like "lead", "case", "event", "opportunity", or "task".
# - Use keyword-to-column mappings to select the correct field (e.g., "disqualified opportunity" → `Sales_Team_Feedback__c` for opportunities).
# - Use keyword-to-column mappings to select the correct field (e.g., "disqualification reason" → `Disqualification_Reason__c`).
# - For terms like "2BHK", "3BHK", filter `Property_Size__c` (e.g., `Property_Size__c: ["2BHK", "3BHK"]`).
# - For "residential" or "commercial", filter `Property_Type__c` (e.g., `Property_Type__c: "Residential"`).
# - For project categories (e.g., "ARANYAM VALLEY"), filter `Project_Category__c` (e.g., `Project_Category__c: "ARANYAM VALLEY"`).
# - For "interested", filter `Customer_Feedback__c = "Interested"`.
# - For "qualified opportunity", filter `Sales_Team_Feedback__c = "Qualified"` for opportunities.
# - For "disqualified opportunity", filter `Sales_Team_Feedback__c = "Disqualified"` or `Sales_Team_Feedback__c = "Not Interested"` for opportunities (use the value that matches your data).
# - For "hot lead", "cold lead", "warm lead", filter `Rating` (e.g., `Rating: "Hot"`).
# - For "qualified", filter `Customer_Feedback__c = "Interested"`.
# - For "disqualified", "disqualification", or "unqualified", filter `Customer_Feedback__c = "Not Interested"`.
# - For "total sale", filter `Sales_Order_Number__c` where it is not null (i.e., `Sales_Order_Number__c: {{"$ne": null}}`) for opportunities to count completed sales.
# - For "sale", filter `Sales_Order_Number__c` where it is not null (i.e., `Sales_Order_Number__c: {{"$ne": null}}`) for opportunities to count completed sales.
# - For "product-wise sales" or "products with sales", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Project_Category__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Project_Category__c` to show the count of sales per product.
# - For "project-wise sale", "project with sale", or "project sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Project__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Project__c` to show the count of sales per project.
# - For "source-wise sale" or "source with sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `LeadSource`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `LeadSource` to show the count of sales per source.
# - For "lead source subcategory with sale" or "subcategory with sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Lead_Source_Sub_Category__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Lead_Source_Sub_Category__c` to show the count of sales per subcategory.
# - For "open lead", filter `Customer_Feedback__c` in `["Discussion Pending", null]` (i.e., `Customer_Feedback__c: {{"$in": ["Discussion Pending", null]}}`).
# - For "lead convert opportunity" or "lead versus opportunity" queries (including "how many", "breakdown", "show me", or "%"), set `analysis_type` to `opportunity_vs_lead` for counts or `opportunity_vs_lead_percentage` for percentages. Use `Customer_Feedback__c = Interested` for opportunities and count all `Id` for leads.
# - Data is available from 2024-04-01T00:00:00Z to 2025-03-31T23:59:59Z. Adjust dates outside this range to the nearest valid date.
# - For date-specific queries (e.g., "4 January 2024"), filter `CreatedDate` for that date.
# - For "today", use 2025-07-01T00:00:00Z to 2025-07-01T23:59:59Z (UTC).
# - For "last week" or "last month", calculate relative to 2025-07-01T00:00:00Z (UTC).
# - For Hinglish like "2025 ka data", filter `CreatedDate` for that year.
# - For "sale by user" or "user-wise sale", set `analysis_type` to `user_sales_summary`, `object_type` to `opportunity`, and join `opportunities_df` with `users_df` on `OwnerId` (opportunities) to `Id` (users).
# - For non-null filters, use `{{"$ne": null}}`.
# - For "product wise funnel" or "product-wise funnel", set `analysis_type` to `product_wise_funnel`, `object_type` to `lead`, and group by `Project_Category__c`. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
# - For "source wise funnel" or "source-wise funnel", set `analysis_type` to `source_wise_funnel`, `object_type` to `lead`, and group by `LeadSource`. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
# - For "user wise funnel" or "user-wise funnel", set `analysis_type` to `user_wise_funnel`, `object_type` to `lead`, and group by `OwnerId`, joining with `users_df` on `OwnerId` (leads) to `Id` (users) to display user names. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
# - If the user mentions "task status", use the `Status` field for tasks.
# - If the user mentions "Total Appointment", use the `Appointment_Status__c` in ["Completed", "Scheduled", "Cancelled", "No show"] within the `conversion_funnel` analysis.
# - If the user mentions "completed task", map to `Status` with value "Completed" for tasks.
# - If the user mentions "pending follow-up", map to `Follow_Up_Status__c` with value "Pending" for tasks.
# - If the user mentions "interested", map to `Customer_Feedback__c` with value "Interested" for leads or tasks.
# - If the user mentions "not interested", map to `Customer_Feedback__c` with value "Not Interested" for leads or tasks.
# - If the user mentions "meeting done", map to `Appointment_Status__c` with value "Completed" for events.
# - If the user mentions "meeting booked", map to `Status` with value "Qualified" for leads.
# - If the user mentions "user wise meeting done", set `analysis_type` to `user_meeting_summary`, `object_type` to `event`, and join `events_df` with `users_df` on `OwnerId` (events) to `Id` (users). Count events where `Appointment_Status__c = "Completed"`, grouped by user name.

# ## Quarter Detection:
# - Detect quarters from keywords:
#   - "Q1", "quarter 1", "first quarter" → "Q1 2024-25" (2024-04-01T00:00:00Z to 2024-06-30T23:59:59Z)
#   - "Q2", "quarter 2", "second quarter" → "Q2 2024-25" (2024-07-01T00:00:00Z to 2024-09-30T23:59:59Z)
#   - "Q3", "quarter 3", "third quarter" → "Q3 2024-25" (2024-10-01T00:00:00Z to 2024-12-31T23:59:59Z)
#   - "Q4", "quarter 4", "fourth quarter" → "Q4 2024-25" (2025-01-01T00:00:00Z to 2025-03-31T23:59:59Z)
# - For `quarterly_distribution`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
# - If no quarter is specified for `quarterly_distribution`, default to "Q1 - Q4".
# - For `quarterly_distribution` or `opportunity_vs_lead`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
# - If no quarter is specified for `quarterly_distribution` or `opportunity_vs_lead`, default to "Q1 - Q4".

# ## Analysis Types:
# - count: Count records.
# - distribution: Frequency of values.
# - filter: List records.
# - recent: Recent records.
# - top: Top values.
# - percentage: Percentage of matching records.
# - quarterly_distribution: Group by quarters.
# - source_wise_funnel: Group by `LeadSource` and `Lead_Source_Sub_Category__c`.
# - conversion_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, etc.).
# - opportunity_vs_lead: Compare count of leads (all `Id`) with opportunities (`Customer_Feedback__c = Interested`).
# - opportunity_vs_lead_percentage: Calculate percentage of leads converted to opportunities (`Customer_Feedback__c = Interested` / total leads).
# - user_meeting_summary: Count completed meetings (`Appointment_Status__c = "Completed"`) per user.
# - dept_user_meeting_summary: Count completed meetings (`Appointment_Status__c = "Completed"`) per user and department.
# - user_sales_summary: Count closed-won opportunities per user, joining `opportunities_df` with `users_df` on `OwnerId` to `Id`.
# - product_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `Project_Category__c`.
# - source_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `LeadSource`.
# - user_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `OwnerId`, joining with `users_df`.

# ## Lead Conversion Funnel:
# For "lead conversion funnel", "funnel analysis", "product wise funnel", "source wise funnel", or "user wise funnel":
# - `analysis_type`: "conversion_funnel", "product_wise_funnel", "source_wise_funnel", or "user_wise_funnel"
# - Fields: `["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c"]` (add `Project_Category__c`, `LeadSource`, or `OwnerId` for grouping in product_wise_funnel, source_wise_funnel, or user_wise_funnel respectively)
# - Metrics:
#   - Total Leads: All leads.
#   - Valid Leads: `Customer_Feedback__c != "Junk"`.
#   - SOL: `Status = "Qualified"`.
#   - Meeting Booked: `Status = "Qualified"` and `Is_Appointment_Booked__c = True`.
#   - Disqualified Leads: `Customer_Feedback__c = "Not Interested"`.
#   - Open Leads: `Customer_Feedback__c` in `["Discussion Pending", null]`.
#   - Total Appointment: `Appointment_Status__c` in `["Completed", "Scheduled", "Cancelled", "No show"]`.
#   - Junk %: ((Total Leads - Valid Leads) / Total Leads) * 100.
#   - VL:SOL: Valid Leads / SOL.
#   - SOL:MB: SOL / Meeting Booked.
#   - MB:MD: Meeting Booked / Meeting Done (using events data where `Appointment_Status__c = "Completed"` for Meeting Done).
#   - Meeting Done: Count Events where `Appointment_Status__c = "Completed"`.

# - For opportunities:
#   - "disqualified opportunity" → Use `Sales_Team_Feedback__c = "Disqualified"`.
#   - "qualified opportunity" → Use `Sales_Team_Feedback__c = "Qualified"`.
#   - "total sale" → Use `Sales_Order_Number__c: {{"$ne": null}}` to count opportunities with a sale order number.

# - For tasks:
#   - "completed task" → Use `Status = "Completed"`.
#   - "open task" → Use `Status = "Open"`.
#   - "pending follow-up" → Use `Follow_Up_Status__c = "Pending"`.
#   - "no follow-up" → Use `Follow_Up_Status__c = "None"`.
#   - "interested" → Use `Customer_Feedback__c = "Interested"`.
#   - "not interested" → Use `Customer_Feedback__c = "Not Interested"`.

# ## JSON Response Format:
# {{
#   "analysis_type": "type_name",
#   "object_type": "lead" or "case" or "event" or "opportunity" or "task",
#   "field": "field_name",
#   "fields": ["field_name"],
#   "filters": {{"field1": "value1", "field2": {{"$ne": null}}}},
#   "group_by": "field_name" (for product_wise_funnel, source_wise_funnel, user_wise_funnel),
#   "join": {{"table": "table_name", "left_on": "left_field", "right_on": "right_field", "fields": ["field_name"]}} (for user_wise_funnel),
#   "quarter": "Q1 2024-25" or "Q2 2024-25" or "Q3 2024-25" or "Q4 2024-25",
#   "limit": 10,
#   "explanation": "Explain what will be done"
# }}

# User Question: {user_question}

# Respond with valid JSON only.
# """

#         ml_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-07-07"
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {token}"
#         }
#         body = {
#             "input": system_prompt,
#             "parameters": {
#                 "decoding_method": "greedy",
#                 "max_new_tokens": 400,
#                 "temperature": 0.2,
#                 "repetition_penalty": 1.1,
#                 "stop_sequences": ["\n\n"]
#             },
#             "model_id": WATSONX_MODEL_ID,
#             "project_id": WATSONX_PROJECT_ID
#         }

#         logger.info(f"Querying WatsonX AI with model: {WATSONX_MODEL_ID}")
#         response = requests.post(ml_url, headers=headers, json=body, timeout=90)

#         if response.status_code != 200:
#             error_msg = f"WatsonX AI Error {response.status_code}: {response.text}"
#             logger.error(error_msg)
#             return {"analysis_type": "error", "message": error_msg}

#         result = response.json()
#         generated_text = result.get("results", [{}])[0].get("generated_text", "").strip()
#         logger.info(f"WatsonX generated response: {generated_text}")

#         try:
#             generated_text = re.sub(r'```json\n?', '', generated_text)
#             generated_text = re.sub(r'\n?```', '', generated_text)
#             generated_text = re.sub(r'\b null\b', 'null', generated_text)
#             json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group(0)
#                 logger.info(f"Extracted JSON string: {json_str}")
#                 analysis_plan = json.loads(json_str)

#                 if "analysis_type" not in analysis_plan:
#                     analysis_plan["analysis_type"] = "filter"
#                 if "explanation" not in analysis_plan:
#                     analysis_plan["explanation"] = "Analysis based on user question"
#                 if "object_type" not in analysis_plan:
#                     analysis_plan["object_type"] = "lead"
#                     if "lead" in user_question.lower():
#                         analysis_plan["object_type"] = "lead"
#                     elif "case" in user_question.lower():
#                         analysis_plan["object_type"] = "case"
#                     elif "event" in user_question.lower():
#                         analysis_plan["object_type"] = "event"
#                     elif "opportunity" in user_question.lower():
#                         analysis_plan["object_type"] = "opportunity"
#                     elif "task" in user_question.lower():
#                         analysis_plan["object_type"] = "task"

#                 if selected_quarter:
#                     analysis_plan["quarter"] = selected_quarter
#                     analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
#                 elif analysis_plan["analysis_type"] == "quarterly_distribution":
#                     analysis_plan["quarter"] = "Q4 2024-25"
#                     analysis_plan["explanation"] += " (Defaulted to Q4 2024-25)"

#                 if "filters" in analysis_plan:
#                     for field, condition in analysis_plan["filters"].items():
#                         if isinstance(condition, dict) and "$ne" in condition and condition["$ne"] == "null":
#                             condition["$ne"] = None
#                         elif isinstance(condition, dict):
#                             for key, value in condition.items():
#                                 if value == "null":
#                                     condition[key] = None
#                         elif condition == "null":
#                             analysis_plan["filters"][field] = None

#                 logger.info(f"Parsed analysis plan: {analysis_plan}")
#                 return analysis_plan
#             else:
#                 logger.warning("No valid JSON found in WatsonX response")
#                 return parse_intent_fallback(user_question, generated_text)
#         except json.JSONDecodeError as e:
#             logger.warning(f"JSON parsing failed: {e}")
#             return parse_intent_fallback(user_question, generated_text)

#     except Exception as e:
#         error_msg = f"WatsonX query failed: {str(e)}"
#         logger.error(error_msg)
#         return {"analysis_type": "error", "explanation": error_msg}

# def parse_intent_fallback(user_question, ai_response):
#     question_lower = user_question.lower()
#     filters = {}
#     object_type = "lead"
#     if "lead" in question_lower:
#         object_type = "lead"
#     elif "case" in question_lower:
#         object_type = "case"
#     elif "event" in question_lower:
#         object_type = "event"
#     elif "opportunity" in question_lower:
#         object_type = "opportunity"
#     elif "task" in question_lower:
#         object_type = "task"

#     quarter_mapping = {
#         r'\b(q1|quarter\s*1|first\s*quarter)\b': 'Q1 2024-25',
#         r'\b(q2|quarter\s*2|second\s*quarter)\b': 'Q2 2024-25',
#         r'\b(q3|quarter\s*3|third\s*quarter)\b': 'Q3 2024-25',
#         r'\b(q4|quarter\s*4|fourth\s*quarter)\b': 'Q4 2024-25',
#     }
#     selected_quarter = None
#     for pattern, quarter in quarter_mapping.items():
#         if re.search(pattern, question_lower, re.IGNORECASE):
#             selected_quarter = quarter
#             break

#     if "today" in question_lower:
#         filters["CreatedDate"] = {
#             "$gte": "2025-07-01T00:00:00Z",
#             "$lte": "2025-07-01T23:59:59Z"
#         }
#     elif "last week" in question_lower:
#         last_week_end = pd.to_datetime("2025-07-01T00:00:00Z", utc=True) - pd.Timedelta(days=pd.to_datetime("2025-07-01").weekday() + 1)
#         last_week_start = last_week_end - pd.Timedelta(days=6)
#         last_week_start = max(last_week_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
#         last_week_end = min(last_week_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
#         filters["CreatedDate"] = {
#             "$gte": last_week_start.strftime("%Y-%m-%dT00:00:00Z"),
#             "$lte": last_week_end.strftime("%Y-%m-%dT23:59:59Z")
#         }
#     elif "last month" in question_lower:
#         last_month_end = (pd.to_datetime("2025-07-01T00:00:00Z", utc=True).replace(day=1) - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59)
#         last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)
#         last_month_start = max(last_month_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
#         last_month_end = min(last_month_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
#         filters["CreatedDate"] = {
#             "$gte": last_month_start.strftime("%Y-%m-%dT00:00:00Z"),
#             "$lte": last_month_end.strftime("%Y-%m-%dT23:59:59Z")
#         }

#     date_pattern = r'\b(\d{1,2})(?:th|rd|st|nd)?\s*(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec)\s*(\d{4})\b'
#     date_match = re.search(date_pattern, question_lower, re.IGNORECASE)
#     if date_match:
#         day = int(date_match.group(1))
#         month_str = date_match.group(2).lower()
#         year = int(date_match.group(3))
#         month_mapping = {
#             'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
#             'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
#             'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
#             'november': 11, 'nov': 11, 'december': 12, 'dec': 12
#         }
#         month = month_mapping.get(month_str)
#         if month:
#             try:
#                 specific_date = pd.to_datetime(f"{year}-{month}-{day}T00:00:00Z", utc=True)
#                 date_str = specific_date.strftime('%Y-%m-%d')
#                 filters["CreatedDate"] = {
#                     "$gte": f"{date_str}T00:00:00Z",
#                     "$lte": f"{date_str}T23:59:59Z"
#                 }
#             except ValueError as e:
#                 logger.warning(f"Invalid date parsed: {e}")
#                 return {
#                     "analysis_type": "error",
#                     "explanation": f"Invalid date specified: {e}"
#                 }

#     hinglish_year_pattern = r'\b(\d{4})\s*ka\s*data\b'
#     hinglish_year_match = re.search(hinglish_year_pattern, question_lower, re.IGNORECASE)
#     if hinglish_year_match:
#         year = hinglish_year_match.group(1)
#         year_start = pd.to_datetime(f"{year}-01-01T00:00:00Z", utc=True)
#         year_end = pd.to_datetime(f"{year}-12-31T23:59:59Z", utc=True)
#         gte = max(year_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
#         lte = min(year_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
#         filters["CreatedDate"] = {
#             "$gte": gte.strftime("%Y-%m-%dT00:00:00Z"),
#             "$lte": lte.strftime("%Y-%m-%dT23:59:59Z")
#         }

#     if "disqualified opportunity" in question_lower and object_type == "opportunity":
#         filters["Sales_Team_Feedback__c"] = "Disqualified"
#     if ("total sale" in question_lower or "sale" in question_lower) and object_type == "opportunity":
#         filters["Sales_Order_Number__c"] = {"$ne": None}
#     if ("project-wise sale" in question_lower or "project with sale" in question_lower or "project sale" in question_lower) and object_type == "opportunity":
#         analysis_plan = {
#             "analysis_type": "distribution",
#             "object_type": "opportunity",
#             "fields": ["Project__c"],
#             "filters": {"Sales_Order_Number__c": {"$ne": None}},
#             "explanation": "Distribution of sales by project"
#         }
#     elif ("source-wise sale" in question_lower or "source with sale" in question_lower) and object_type == "opportunity":
#         analysis_plan = {
#             "analysis_type": "distribution",
#             "object_type": "opportunity",
#             "fields": ["LeadSource"],
#             "filters": {"Sales_Order_Number__c": {"$ne": None}},
#             "explanation": "Distribution of sales by source"
#         }
#     elif ("lead source subcategory with sale" in question_lower or "subcategory with sale" in question_lower) and object_type == "opportunity":
#         analysis_plan = {
#             "analysis_type": "distribution",
#             "object_type": "opportunity",
#             "fields": ["Lead_Source_Sub_Category__c"],
#             "filters": {"Sales_Order_Number__c": {"$ne": None}},
#             "explanation": "Distribution of sales by lead source subcategory"
#         }
#     else:
#         analysis_plan = {
#             "analysis_type": "filter",
#             "object_type": object_type,
#             "filters": filters,
#             "explanation": f"Filtering {object_type} records for: {user_question}"
#         }

#     if selected_quarter:
#         analysis_plan["quarter"] = selected_quarter
#         analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
#     return analysis_plan


#===================================wed day 3/7/25 update=======================


import requests
import json
import re
import pandas as pd
from config import WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL, WATSONX_MODEL_ID, IBM_CLOUD_IAM_URL, logger

def validate_watsonx_config():
    missing_configs = []
    if not WATSONX_API_KEY:
        missing_configs.append("WATSONX_API_KEY")
    if not WATSONX_PROJECT_ID:
        missing_configs.append("WATSONX_PROJECT_ID")
    if missing_configs:
        error_msg = f"Missing WatsonX configuration: {', '.join(missing_configs)}"
        logger.error(error_msg)
        return False, error_msg
    if len(WATSONX_API_KEY.strip()) < 10:
        return False, "WATSONX_API_KEY appears to be invalid (too short)"
    if len(WATSONX_PROJECT_ID.strip()) < 10:
        return False, "WATSONX_PROJECT_ID appears to be invalid (too short)"
    return True, "Configuration valid"

def get_watsonx_token():
    is_valid, validation_msg = validate_watsonx_config()
    if not is_valid:
        raise ValueError(f"Configuration error: {validation_msg}")
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_API_KEY.strip()}
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
            "available_event_fields": list(events_df.columns) if not leads_df.empty else [],
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
    try:
        is_valid, validation_msg = validate_watsonx_config()
        if not is_valid:
            return {"analysis_type": "error", "explanation": f"Configuration error: {validation_msg}"}

        logger.info("Getting WatsonX access token...")
        token = get_watsonx_token()

        sample_lead_fields = ', '.join(data_context['data_summary']['available_lead_fields'])
        sample_user_fields = ', '.join(data_context['data_summary']['available_user_fields'])
        sample_case_fields = ', '.join(data_context['data_summary']['available_case_fields'])
        sample_event_fields = ', '.join(data_context['data_summary']['available_event_fields'])
        sample_opportunity_fields = ', '.join(data_context['data_summary']['available_opportunity_fields'])
        sample_task_fields = ', '.join(data_context['data_summary']['available_task_fields'])

        # Detect new funnel queries
        if any(keyword in user_question.lower() for keyword in ["product wise funnel", "product-wise funnel"]):
            return {
                "analysis_type": "product_wise_funnel",
                "object_type": "lead",
                "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "Project_Category__c"],
                "group_by": "Project_Category__c",
                "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by Project_Category__c"
            }
            
        if any(keyword in user_question.lower() for keyword in ["project wise funnel", "project-wise funnel"]):
            return {
                "analysis_type": "project_wise_funnel",
                "object_type": "lead",
                "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "Project__c"],
                "group_by": "Project__c",
                "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by Project__c"
            }
        
        if any(keyword in user_question.lower() for keyword in ["source wise funnel", "source-wise funnel"]):
            return {
                "analysis_type": "source_wise_funnel",
                "object_type": "lead",
                "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "LeadSource"],
                "group_by": "LeadSource",
                "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by LeadSource"
            }
        if any(keyword in user_question.lower() for keyword in ["user wise funnel", "user-wise funnel"]):
            return {
                "analysis_type": "user_wise_funnel",
                "object_type": "lead",
                "fields": ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c", "OwnerId"],
                "group_by": "OwnerId",
                "join": {"table": "users_df", "left_on": "OwnerId", "right_on": "Id", "fields": ["Name"]},
                "explanation": "Compute lead conversion funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by OwnerId, joining with users_df to display user names"
            }

        # Detect user-wise sales queries
        if any(keyword in user_question.lower() for keyword in ["sale by user", "user wise sale", "user-wise sale", "sales by user"]):
            return {
                "analysis_type": "user_sales_summary",
                "object_type": "opportunity",
                "fields": ["OwnerId", "Sales_Order_Number__c"],
                "filters": {"Sales_Order_Number__c": {"$ne": None}},
                "explanation": "Show count of closed-won opportunities grouped by user"
            }
            
        if "user wise meeting done" in user_question.lower():
            return {
                "analysis_type": "user_meeting_summary",
                "object_type": "event",
                "fields": ["OwnerId", "Appointment_Status__c"],
                "filters": {"Appointment_Status__c": "Completed"},
                "explanation": "Show count of completed meetings grouped by user"
            }
        if "department wise meeting done" in user_question.lower():
            return {
                "analysis_type": "dept_user_meeting_summary",
                "object_type": "event",
                "fields": ["OwnerId", "Appointment_Status__c", "Department"],
                "filters": {"Appointment_Status__c": "Completed"},
                "explanation": "Show count of completed meetings grouped by user and department"
            }
            
        if "total meeting done" in user_question.lower():
            return {
                "analysis_type": "count",
                "object_type": "event",
                "fields": ["Appointment_Status__c"],
                "filters": {"Appointment_Status__c": "Completed"},
                "explanation": "Show total count of completed meetings"
            }
        
        # Updated to handle both singular and plural forms
        if "disqualification reason" in user_question.lower() or "disqualification reasons" in user_question.lower():
            return {
                "analysis_type": "disqualification_summary",
                "object_type": "lead",
                "field": "Disqualification_Reason__c",
                "filters": {},
                "explanation": "Show disqualification reasons with count and percentage"
            }
            
        if "junk reason" in user_question.lower():
            return {
                "analysis_type": "junk_reason_summary",
                "object_type": "lead",
                "field": "Junk_Reason__c",
                "filters": {},
                "explanation": "Show junk reasons with count and percentage"
            }
            
        if any(keyword in user_question.lower() for keyword in ["disqualification"]) and any(pct in user_question.lower() for pct in ["%", "percent", "percentage"]):
            return {
                "analysis_type": "percentage",
                "object_type": "lead",
                "fields": ["Customer_Feedback__c"],
                "filters": {"Customer_Feedback__c": "Not Interested"},
                "explanation": "Calculate percentage of disqualification leads where Customer_Feedback__c is 'Not Interested'"
            }

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
            "open lead": "Customer_Feedback__c",
            "hot lead": "Rating",
            "cold lead": "Rating",
            "warm lead": "Rating",
            "product": "Project_Category__c",
            "product name": "Project_Category__c",
            "disqualified": "Status",
            "disqualification": "Customer_Feedback__c",
            "unqualified": "Status",
            "qualified": "Status",
            "lead conversion funnel": "Status",
            "funnel analysis": "Status",
            "Junk": "Customer_Feedback__c",
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
            "total appointments": "Appointment_status__c",
            "user wise meeting done": ["OwnerId", "Appointment_Status__c"]
        }

        opportunity_keyword_mappings = {
            "qualified opportunity": "Sales_Team_Feedback__c",
            "disqualified opportunity": "Sales_Team_Feedback__c",
            "amount": "Amount",
            "close date": "CloseDate",
            "opportunity type": "Opportunity_Type__c",
            "new business": "Opportunity_Type__c",
            "renewal": "Opportunity_Type__c",
            "upsell": "Opportunity_Type__c",
            "cross-sell": "Opportunity_Type__c",
            "total sale": "Sales_Order_Number__c",
            "source-wise sale": "LeadSource",
            "source with sale": "LeadSource",
            "lead source subcategory with sale": "Lead_Source_Sub_Category__c",
            "subcategory with sale": "Lead_Source_Sub_Category__c",
            "product-wise sales": "Project_Category__c",
            "products with sales": "Project_Category__c",
            "product sale": "Project_Category__c",
            "project-wise sales": "Project__c",
            "project with sale": "Project__c",
            "project sale": "Project__c",
            "sales by user": "OwnerId",
            "user-wise sale": "OwnerId"
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
        if "quarter" in question_lower and not selected_quarter:
            selected_quarter = "Q4 2024-25"
            logger.info(f"No specific quarter detected, defaulting to {selected_quarter}")

        system_prompt = f"""
You are an intelligent Salesforce analytics assistant. Your task is to convert user questions into a JSON-based analysis plan for lead, case, event, opportunity, or task data.

Available lead fields: {sample_lead_fields}
Available user fields: {sample_user_fields}
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
- Use keyword-to-column mappings to select the correct field (e.g., "disqualified opportunity" → `Sales_Team_Feedback__c` for opportunities).
- Use keyword-to-column mappings to select the correct field (e.g., "disqualification reason" → `Disqualification_Reason__c`).
- For terms like "2BHK", "3BHK", filter `Property_Size__c` (e.g., `Property_Size__c: ["2BHK", "3BHK"]`).
- For "residential" or "commercial", filter `Property_Type__c` (e.g., `Property_Type__c: "Residential"`).
- For project categories (e.g., "ARANYAM VALLEY"), filter `Project_Category__c` (e.g., `Project_Category__c: "ARANYAM VALLEY"`).
- For "interested", filter `Customer_Feedback__c = "Interested"`.
- For "qualified opportunity", filter `Sales_Team_Feedback__c = "Qualified"` for opportunities.
- For "disqualified opportunity", filter `Sales_Team_Feedback__c = "Disqualified"` or `Sales_Team_Feedback__c = "Not Interested"` for opportunities (use the value that matches your data).
- For "hot lead", "cold lead", "warm lead", filter `Rating` (e.g., `Rating: "Hot"`).
- For "qualified", filter `Customer_Feedback__c = "Interested"`.
- For "disqualified", "disqualification", or "unqualified", filter `Customer_Feedback__c = "Not Interested"`.
- For "total sale", filter `Sales_Order_Number__c` where it is not null (i.e., `Sales_Order_Number__c: {{"$ne": null}}`) for opportunities to count completed sales.
- For "sale", filter `Sales_Order_Number__c` where it is not null (i.e., `Sales_Order_Number__c: {{"$ne": null}}`) for opportunities to count completed sales.
- For "product-wise sales" or "products with sales", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Project_Category__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Project_Category__c` to show the count of sales per product.
- For "project-wise sale", "project with sale", or "project sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Project__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Project__c` to show the count of sales per project.
- For "source-wise sale" or "source with sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `LeadSource`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `LeadSource` to show the count of sales per source.
- For "lead source subcategory with sale" or "subcategory with sale", set `analysis_type` to `distribution`, `object_type` to `opportunity`, `field` to `Lead_Source_Sub_Category__c`, and filter `Sales_Order_Number__c: {{"$ne": null}}` to include only opportunities with completed sales. Group by `Lead_Source_Sub_Category__c` to show the count of sales per subcategory.
- For "open lead", filter `Customer_Feedback__c` in `["Discussion Pending", null]` (i.e., `Customer_Feedback__c: {{"$in": ["Discussion Pending", null]}}`).
- For "lead convert opportunity" or "lead versus opportunity" queries (including "how many", "breakdown", "show me", or "%"), set `analysis_type` to `opportunity_vs_lead` for counts or `opportunity_vs_lead_percentage` for percentages. Use `Customer_Feedback__c = Interested` for opportunities and count all `Id` for leads.
- Data is available from 2024-04-01T00:00:00Z to 2025-03-31T23:59:59Z. Adjust dates outside this range to the nearest valid date.
- For date-specific queries (e.g., "4 January 2024"), filter `CreatedDate` for that date.
- For "today", use 2025-07-01T00:00:00Z to 2025-07-01T23:59:59Z (UTC).
- For "last week" or "last month", calculate relative to 2025-07-01T00:00:00Z (UTC).
- For Hinglish like "2025 ka data", filter `CreatedDate` for that year.
- For "sale by user" or "user-wise sale", set `analysis_type` to `user_sales_summary`, `object_type` to `opportunity`, and join `opportunities_df` with `users_df` on `OwnerId` (opportunities) to `Id` (users).
- For non-null filters, use `{{"$ne": null}}`.
- For "project wise funnel" or "project-wise funnel", set `analysis_type` to `project_wise_funnel`, `object_type` to `lead`, and group by `Project__c`. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
- For "product wise funnel" or "product-wise funnel", set `analysis_type` to `product_wise_funnel`, `object_type` to `lead`, and group by `Project_Category__c`. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
- For "source wise funnel" or "source-wise funnel", set `analysis_type` to `source_wise_funnel`, `object_type` to `lead`, and group by `LeadSource`. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
- For "user wise funnel" or "user-wise funnel", set `analysis_type` to `user_wise_funnel`, `object_type` to `lead`, and group by `OwnerId`, joining with `users_df` on `OwnerId` (leads) to `Id` (users) to display user names. Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done).
- If the user mentions "task status", use the `Status` field for tasks.
- If the user mentions "Total Appointment", use the `Appointment_Status__c` in ["Completed", "Scheduled", "Cancelled", "No show"] within the `conversion_funnel` analysis.
- If the user mentions "completed task", map to `Status` with value "Completed" for tasks.
- If the user mentions "pending follow-up", map to `Follow_Up_Status__c` with value "Pending" for tasks.
- If the user mentions "interested", map to `Customer_Feedback__c` with value "Interested" for leads or tasks.
- If the user mentions "not interested", map to `Customer_Feedback__c` with value "Not Interested" for leads or tasks.
- If the user mentions "meeting done", map to `Appointment_Status__c` with value "Completed" for events.
- If the user mentions "meeting booked", map to `Status` with value "Qualified" for leads.
- If the user mentions "user wise meeting done", set `analysis_type` to `user_meeting_summary`, `object_type` to `event`, and join `events_df` with `users_df` on `OwnerId` (events) to `Id` (users). Count events where `Appointment_Status__c = "Completed"`, grouped by user name.

## Quarter Detection:
- Detect quarters from keywords:
  - "Q1", "quarter 1", "first quarter" → "Q1 2024-25" (2024-04-01T00:00:00Z to 2024-06-30T23:59:59Z)
  - "Q2", "quarter 2", "second quarter" → "Q2 2024-25" (2024-07-01T00:00:00Z to 2024-09-30T23:59:59Z)
  - "Q3", "quarter 3", "third quarter" → "Q3 2024-25" (2024-10-01T00:00:00Z to 2024-12-31T23:59:59Z)
  - "Q4", "quarter 4", "fourth quarter" → "Q4 2024-25" (2025-01-01T00:00:00Z to 2025-03-31T23:59:59Z)
- For `quarterly_distribution`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
- If no quarter is specified for `quarterly_distribution`, default to "Q1 - Q4".
- For `quarterly_distribution` or `opportunity_vs_lead`, include `quarter` in the response (e.g., `quarter: "Q1 2024-25"`).
- If no quarter is specified for `quarterly_distribution` or `opportunity_vs_lead`, default to "Q1 - Q4".

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
- opportunity_vs_lead: Compare count of leads (all `Id`) with opportunities (`Customer_Feedback__c = Interested`).
- opportunity_vs_lead_percentage: Calculate percentage of leads converted to opportunities (`Customer_Feedback__c = Interested` / total leads).
- user_meeting_summary: Count completed meetings (`Appointment_Status__c = "Completed"`) per user.
- dept_user_meeting_summary: Count completed meetings (`Appointment_Status__c = "Completed"`) per user and department.
- user_sales_summary: Count closed-won opportunities per user, joining `opportunities_df` with `users_df` on `OwnerId` to `Id`.
- product_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `Project_Category__c`.
- project_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `Project__c`.

- source_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `LeadSource`.
- user_wise_funnel: Compute funnel metrics (Total Leads, Valid Leads, SOL, Meeting Booked, Disqualified Leads, Open Leads, Total Appointment, Junk %, VL:SOL, SOL:MB, MB:MD, Meeting Done) grouped by `OwnerId`, joining with `users_df`.

## Lead Conversion Funnel:
For "lead conversion funnel", "funnel analysis", "product wise funnel", "project wise funnel", "source wise funnel", or "user wise funnel":
- `analysis_type`: "conversion_funnel", "product_wise_funnel", "source_wise_funnel", "project_wise_funnel", or "user_wise_funnel"
- Fields: `["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c"]` (add `Project_Category__c`, `LeadSource`, `Project__c`, or `OwnerId` for grouping in product_wise_funnel, source_wise_funnel, project_wise_funnel, or user_wise_funnel respectively)
- Metrics:
  - Total Leads: All leads.
  - Valid Leads: `Customer_Feedback__c != "Junk"`.
  - SOL: `Status = "Qualified"`.
  - Meeting Booked: `Status = "Qualified"` and `Is_Appointment_Booked__c = True`.
  - Disqualified Leads: `Customer_Feedback__c = "Not Interested"`.
  - Open Leads: `Customer_Feedback__c` in `["Discussion Pending", null]`.
  - Total Appointment: `Appointment_Status__c` in `["Completed", "Scheduled", "Cancelled", "No show"]`.
  - Junk %: ((Total Leads - Valid Leads) / Total Leads) * 100.
  - VL:SOL: Valid Leads / SOL.
  - SOL:MB: SOL / Meeting Booked.
  - MB:MD: Meeting Booked / Meeting Done (using events data where `Appointment_Status__c = "Completed"` for Meeting Done).
  - Meeting Done: Count Events where `Appointment_Status__c = "Completed"`.

- For opportunities:
  - "disqualified opportunity" → Use `Sales_Team_Feedback__c = "Disqualified"`.
  - "qualified opportunity" → Use `Sales_Team_Feedback__c = "Qualified"`.
  - "total sale" → Use `Sales_Order_Number__c: {{"$ne": null}}` to count opportunities with a sale order number.

- For tasks:
  - "completed task" → Use `Status = "Completed"`.
  - "open task" → Use `Status = "Open"`.
  - "pending follow-up" → Use `Follow_Up_Status__c = "Pending"`.
  - "no follow-up" → Use `Follow_Up_Status__c = "None"`.
  - "interested" → Use `Customer_Feedback__c = "Interested"`.
  - "not interested" → Use `Customer_Feedback__c = "Not Interested"`.

## JSON Response Format:
{{
  "analysis_type": "type_name",
  "object_type": "lead" or "case" or "event" or "opportunity" or "task",
  "field": "field_name",
  "fields": ["field_name"],
  "filters": {{"field1": "value1", "field2": {{"$ne": null}}}},
  "group_by": "field_name" (for product_wise_funnel, source_wise_funnel, user_wise_funnel, project_wise_funnel),
  "join": {{"table": "table_name", "left_on": "left_field", "right_on": "right_field", "fields": ["field_name"]}} (for user_wise_funnel),
  "quarter": "Q1 2024-25" or "Q2 2024-25" or "Q3 2024-25" or "Q4 2024-25",
  "limit": 10,
  "explanation": "Explain what will be done"
}}

User Question: {user_question}

Respond with valid JSON only.
"""

        ml_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-07-07"
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
            "model_id": WATSONX_MODEL_ID,
            "project_id": WATSONX_PROJECT_ID
        }

        logger.info(f"Querying WatsonX AI with model: {WATSONX_MODEL_ID}")
        response = requests.post(ml_url, headers=headers, json=body, timeout=90)

        if response.status_code != 200:
            error_msg = f"WatsonX AI Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {"analysis_type": "error", "message": error_msg}

        result = response.json()
        generated_text = result.get("results", [{}])[0].get("generated_text", "").strip()
        logger.info(f"WatsonX generated response: {generated_text}")

        try:
            generated_text = re.sub(r'```json\n?', '', generated_text)
            generated_text = re.sub(r'\n?```', '', generated_text)
            generated_text = re.sub(r'\b null\b', 'null', generated_text)
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Extracted JSON string: {json_str}")
                analysis_plan = json.loads(json_str)

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

                if selected_quarter:
                    analysis_plan["quarter"] = selected_quarter
                    analysis_plan["explanation"] += f" (Filtered for {selected_quarter})"
                elif analysis_plan["analysis_type"] == "quarterly_distribution":
                    analysis_plan["quarter"] = "Q4 2024-25"
                    analysis_plan["explanation"] += " (Defaulted to Q4 2024-25)"

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

    if "today" in question_lower:
        filters["CreatedDate"] = {
            "$gte": "2025-07-01T00:00:00Z",
            "$lte": "2025-07-01T23:59:59Z"
        }
    elif "last week" in question_lower:
        last_week_end = pd.to_datetime("2025-07-01T00:00:00Z", utc=True) - pd.Timedelta(days=pd.to_datetime("2025-07-01").weekday() + 1)
        last_week_start = last_week_end - pd.Timedelta(days=6)
        last_week_start = max(last_week_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
        last_week_end = min(last_week_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
        filters["CreatedDate"] = {
            "$gte": last_week_start.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": last_week_end.strftime("%Y-%m-%dT23:59:59Z")
        }
    elif "last month" in question_lower:
        last_month_end = (pd.to_datetime("2025-07-01T00:00:00Z", utc=True).replace(day=1) - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)
        last_month_start = max(last_month_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
        last_month_end = min(last_month_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
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
        gte = max(year_start, pd.to_datetime("2024-04-01T00:00:00Z", utc=True))
        lte = min(year_end, pd.to_datetime("2025-03-31T23:59:59Z", utc=True))
        filters["CreatedDate"] = {
            "$gte": gte.strftime("%Y-%m-%dT00:00:00Z"),
            "$lte": lte.strftime("%Y-%m-%dT23:59:59Z")
        }

    if "disqualified opportunity" in question_lower and object_type == "opportunity":
        filters["Sales_Team_Feedback__c"] = "Disqualified"
    if ("total sale" in question_lower or "sale" in question_lower) and object_type == "opportunity":
        filters["Sales_Order_Number__c"] = {"$ne": None}
    if ("project-wise sale" in question_lower or "project with sale" in question_lower or "project sale" in question_lower) and object_type == "opportunity":
        analysis_plan = {
            "analysis_type": "distribution",
            "object_type": "opportunity",
            "fields": ["Project__c"],
            "filters": {"Sales_Order_Number__c": {"$ne": None}},
            "explanation": "Distribution of sales by project"
        }
    elif ("source-wise sale" in question_lower or "source with sale" in question_lower) and object_type == "opportunity":
        analysis_plan = {
            "analysis_type": "distribution",
            "object_type": "opportunity",
            "fields": ["LeadSource"],
            "filters": {"Sales_Order_Number__c": {"$ne": None}},
            "explanation": "Distribution of sales by source"
        }
    elif ("lead source subcategory with sale" in question_lower or "subcategory with sale" in question_lower) and object_type == "opportunity":
        analysis_plan = {
            "analysis_type": "distribution",
            "object_type": "opportunity",
            "fields": ["Lead_Source_Sub_Category__c"],
            "filters": {"Sales_Order_Number__c": {"$ne": None}},
            "explanation": "Distribution of sales by lead source subcategory"
        }
    else:
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