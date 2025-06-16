

# salesforce_utils.py
import requests
import pandas as pd
from urllib.parse import quote
from config import (
    client_id, client_secret, username, password, login_url, 
    SF_LEADS_URL, SF_USERS_URL, SF_CASES_URL, SF_EVENTS_URL, SF_OPPORTUNITIES_URL, SF_TASKS_URL,
    get_minimal_lead_fields, get_standard_lead_fields, get_extended_lead_fields,
    get_safe_user_fields, get_minimal_case_fields, get_standard_case_fields, get_extended_case_fields,
    get_minimal_event_fields, get_standard_event_fields, get_extended_event_fields,
    get_minimal_opportunity_fields, get_standard_opportunity_fields, get_extended_opportunity_fields,
    get_minimal_task_fields, get_standard_task_fields, get_extended_task_fields,
    logger
)

def get_access_token():
    if not all([client_id, client_secret, username, password, login_url]):
        raise ValueError("Missing required Salesforce credentials in environment variables")
    payload = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret, 'username': username, 'password': password}
    try:
        res = requests.post(login_url, data=payload, timeout=30)
        res.raise_for_status()
        token_data = res.json()
        return token_data['access_token']
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to authenticate with Salesforce: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise

def test_fields_incrementally(access_token, base_url, field_sets, object_type="Lead"):
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    field_sets_ordered = {'extended': field_sets['extended'], 'standard': field_sets['standard'], 'minimal': field_sets['minimal']}
    for field_set_name, fields in field_sets_ordered.items():
        test_query = f"SELECT {', '.join(fields)} FROM {object_type} LIMIT 1"
        test_url = base_url + quote(test_query)
        try:
            response = requests.get(test_url, headers=headers, timeout=30)
            if response.status_code == 200:
                logger.info(f"✅ {object_type} {field_set_name} fields work fine")
                return fields, field_set_name
            else:
                logger.warning(f"❌ {object_type} {field_set_name} failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            logger.warning(f"❌ {object_type} {field_set_name} error: {e}")
    return None, None

def debug_individual_fields(access_token, base_url, fields_to_test, object_type="Lead"):
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    working_fields = ['Id']
    problematic_fields = []
    for field in fields_to_test:
        if field == 'Id':
            continue
        test_query = f"SELECT Id, {field} FROM {object_type} LIMIT 1"
        test_url = base_url + quote(test_query)
        try:
            response = requests.get(test_url, headers=headers, timeout=30)
            if response.status_code == 200:
                working_fields.append(field)
                logger.info(f"✅ {object_type} {field} - OK")
            else:
                problematic_fields.append(field)
                logger.warning(f"❌ {object_type} {field} - FAILED: {response.text[:100]}")
        except Exception as e:
            problematic_fields.append(field)
            logger.error(f"❌ {object_type} {field} - ERROR: {e}")
    logger.info(f"Working {object_type} fields: {working_fields}")
    logger.info(f"Problematic {object_type} fields: {problematic_fields}")
    return working_fields

def make_arrow_compatible(df):
    df_copy = df.copy()
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            df_copy[col] = df_copy[col].astype(str).replace('nan', None)
        elif df_copy[col].dtype.name.startswith('datetime'):
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce', utc=True)
    return df_copy

def load_salesforce_data():
    try:
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        # Load Lead data
        lead_field_sets = {
            'minimal': get_minimal_lead_fields(),
            'standard': get_standard_lead_fields(),
            'extended': get_extended_lead_fields()
        }
        lead_fields, lead_field_set_used = test_fields_incrementally(access_token, SF_LEADS_URL, lead_field_sets, "Lead")
        if not lead_fields:
            logger.warning("All lead field sets failed, testing individual fields...")
            lead_fields = debug_individual_fields(access_token, SF_LEADS_URL, get_extended_lead_fields(), "Lead")
        if not lead_fields or len(lead_fields) <= 1:
            logger.error("Could not find any working Lead fields")
            lead_df = pd.DataFrame()
        else:
            start_date = "2024-04-01T00:00:00Z"
            end_date = "2025-03-31T23:59:59Z"
            lead_query = f"SELECT {', '.join(lead_fields)} FROM Lead WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date} ORDER BY CreatedDate DESC"
            lead_url = SF_LEADS_URL + quote(lead_query)
            logger.info(f"Executing lead query with {len(lead_fields)} fields: {lead_field_set_used or 'custom'}")
            
            lead_resp = requests.get(lead_url, headers=headers, timeout=60)
            if lead_resp.status_code != 200:
                logger.error(f"Lead query failed: {lead_resp.status_code} - {lead_resp.text}")
                lead_df = pd.DataFrame()
            else:
                leads_json = lead_resp.json()
                leads_records = leads_json.get('records', [])
                all_leads = leads_records
                while 'nextRecordsUrl' in leads_json:
                    next_url = "https://waveinfratech.my.salesforce.com" + leads_json['nextRecordsUrl']
                    lead_resp = requests.get(next_url, headers=headers, timeout=60)
                    if lead_resp.status_code != 200:
                        logger.error(f"Failed to fetch next lead page: {lead_resp.status_code} - {lead_resp.text}")
                        break
                    leads_json = lead_resp.json()
                    all_leads.extend(leads_json.get('records', []))
                
                clean_lead_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_leads]
                lead_df = pd.DataFrame(clean_lead_records)
                lead_df = make_arrow_compatible(lead_df)
                logger.info(f"Successfully loaded {len(lead_df)} leads")
                logger.info(f"lead_df columns: {list(lead_df.columns)}")
                logger.info(f"lead_df dtypes:\n{lead_df.dtypes}")
                for col in ['Is_Junk__c', 'Rating', 'Project__c', 'Campaign_Name__c', 'Customer_Feedback__c', 'Junk_Reason__c']:
                    if col in lead_df.columns:
                        logger.info(f"Sample {col} values: {lead_df[col].dropna().unique()[:5]}")
                if 'CreatedDate' in lead_df.columns:
                    lead_df['CreatedDate'] = pd.to_datetime(lead_df['CreatedDate'], utc=True, errors='coerce')
                    invalid_dates = lead_df['CreatedDate'].isna().sum()
                    logger.info(f"Number of invalid lead CreatedDate values: {invalid_dates}")
                    if invalid_dates > 0:
                        logger.warning(f"Found {invalid_dates} leads with invalid CreatedDate values")
                    sample_dates = lead_df['CreatedDate'].dropna().head(5).tolist()
                    logger.info(f"Sample lead CreatedDate values: {sample_dates}")

        # Load User data
        try:
            user_fields = get_safe_user_fields()
            user_query = f"SELECT {', '.join(user_fields)} FROM User WHERE IsActive = true LIMIT 200"
            user_url = SF_USERS_URL + quote(user_query)
            user_resp = requests.get(user_url, headers=headers, timeout=30)
            if user_resp.status_code == 200:
                users_json = user_resp.json()
                users_records = users_json.get('records', [])
                clean_user_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in users_records]
                user_df = pd.DataFrame(clean_user_records)
                user_df = make_arrow_compatible(user_df)
                logger.info(f"Successfully loaded {len(user_df)} users")
            else:
                logger.warning(f"User query failed: {user_resp.status_code}")
                user_df = pd.DataFrame()
        except Exception as e:
            logger.warning(f"User query error (continuing without users): {e}")
            user_df = pd.DataFrame()

        # Load Case data
        case_field_sets = {
            'minimal': get_minimal_case_fields(),
            'standard': get_standard_case_fields(),
            'extended': get_extended_case_fields()
        }
        case_fields, case_field_set_used = test_fields_incrementally(access_token, SF_CASES_URL, case_field_sets, "Case")
        if not case_fields:
            logger.warning("All case field sets failed, testing individual fields...")
            case_fields = debug_individual_fields(access_token, SF_CASES_URL, get_extended_case_fields(), "Case")
        if not case_fields or len(case_fields) <= 1:
            logger.error("Could not find any working Case fields")
            case_df = pd.DataFrame()
        else:
            start_date = "2024-04-01T00:00:00Z"
            end_date = "2025-03-31T23:59:59Z"
            case_query = f"SELECT {', '.join(case_fields)} FROM Case WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date} ORDER BY CreatedDate DESC"
            case_url = SF_CASES_URL + quote(case_query)
            logger.info(f"Executing case query with {len(case_fields)} fields: {case_field_set_used or 'custom'}")
            
            case_resp = requests.get(case_url, headers=headers, timeout=60)
            if case_resp.status_code != 200:
                logger.error(f"Case query failed: {case_resp.status_code} - {case_resp.text}")
                case_df = pd.DataFrame()
            else:
                cases_json = case_resp.json()
                cases_records = cases_json.get('records', [])
                all_cases = cases_records
                while 'nextRecordsUrl' in cases_json:
                    next_url = "https://waveinfratech.my.salesforce.com" + cases_json['nextRecordsUrl']
                    case_resp = requests.get(next_url, headers=headers, timeout=60)
                    if case_resp.status_code != 200:
                        logger.error(f"Failed to fetch next case page: {case_resp.status_code} - {case_resp.text}")
                        break
                    cases_json = case_resp.json()
                    all_cases.extend(cases_json.get('records', []))
                
                clean_case_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_cases]
                case_df = pd.DataFrame(clean_case_records)
                case_df = make_arrow_compatible(case_df)
                logger.info(f"Successfully loaded {len(case_df)} cases")
                logger.info(f"case_df columns: {list(case_df.columns)}")
                logger.info(f"case_df dtypes:\n{case_df.dtypes}")
                for col in ['Service_Request_Number__c', 'Type', 'Feedback__c', 'Origin', 'Corporate_Closure_Remark__c']:
                    if col in case_df.columns:
                        logger.info(f"Sample {col} values: {case_df[col].dropna().unique()[:5]}")
                if 'CreatedDate' in case_df.columns:
                    case_df['CreatedDate'] = pd.to_datetime(case_df['CreatedDate'], utc=True, errors='coerce')
                    invalid_dates = case_df['CreatedDate'].isna().sum()
                    logger.info(f"Number of invalid case CreatedDate values: {invalid_dates}")
                    if invalid_dates > 0:
                        logger.warning(f"Found {invalid_dates} cases with invalid CreatedDate values")
                    sample_dates = case_df['CreatedDate'].dropna().head(5).tolist()
                    logger.info(f"Sample case CreatedDate values: {sample_dates}")

        # Load Event data
        event_field_sets = {
            'minimal': get_minimal_event_fields(),
            'standard': get_standard_event_fields(),
            'extended': get_extended_event_fields()
        }
        event_fields, event_field_set_used = test_fields_incrementally(access_token, SF_EVENTS_URL, event_field_sets, "Event")
        if not event_fields:
            logger.warning("All event field sets failed, testing individual fields...")
            event_fields = debug_individual_fields(access_token, SF_EVENTS_URL, get_extended_event_fields(), "Event")
        if not event_fields or len(event_fields) <= 1:
            logger.error("Could not find any working Event fields")
            event_df = pd.DataFrame()
        else:
            start_date = "2024-04-01T00:00:00Z"
            end_date = "2025-03-31T23:59:59Z"
            event_query = f"SELECT {', '.join(event_fields)} FROM Event WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date} ORDER BY CreatedDate DESC"
            event_url = SF_EVENTS_URL + quote(event_query)
            logger.info(f"Executing event query with {len(event_fields)} fields: {event_field_set_used or 'custom'}")
            
            event_resp = requests.get(event_url, headers=headers, timeout=60)
            if event_resp.status_code != 200:
                logger.error(f"Event query failed: {event_resp.status_code} - {event_resp.text}")
                event_df = pd.DataFrame()
            else:
                events_json = event_resp.json()
                events_records = events_json.get('records', [])
                all_events = events_records
                while 'nextRecordsUrl' in events_json:
                    next_url = "https://waveinfratech.my.salesforce.com" + events_json['nextRecordsUrl']
                    event_resp = requests.get(next_url, headers=headers, timeout=60)
                    if event_resp.status_code != 200:
                        logger.error(f"Failed to fetch next event page: {event_resp.status_code} - {event_resp.text}")
                        break
                    events_json = event_resp.json()
                    all_events.extend(events_json.get('records', []))
                
                clean_event_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_events]
                event_df = pd.DataFrame(clean_event_records)
                event_df = make_arrow_compatible(event_df)
                logger.info(f"Successfully loaded {len(event_df)} events")
                logger.info(f"event_df columns: {list(event_df.columns)}")
                logger.info(f"event_df dtypes:\n{event_df.dtypes}")
                for col in ['Appointment_Status__c', 'Subject', 'StartDateTime', 'EndDateTime']:
                    if col in event_df.columns:
                        logger.info(f"Sample {col} values: {event_df[col].dropna().unique()[:5]}")
                if 'CreatedDate' in event_df.columns:
                    event_df['CreatedDate'] = pd.to_datetime(event_df['CreatedDate'], utc=True, errors='coerce')
                    invalid_dates = event_df['CreatedDate'].isna().sum()
                    logger.info(f"Number of invalid event CreatedDate values: {invalid_dates}")
                    if invalid_dates > 0:
                        logger.warning(f"Found {invalid_dates} events with invalid CreatedDate values")
                    sample_dates = event_df['CreatedDate'].dropna().head(5).tolist()
                    logger.info(f"Sample event CreatedDate values: {sample_dates}")

        # Load Opportunity data
        opportunity_field_sets = {
            'minimal': get_minimal_opportunity_fields(),
            'standard': get_standard_opportunity_fields(),
            'extended': get_extended_opportunity_fields()
        }
        opportunity_fields, opportunity_field_set_used = test_fields_incrementally(access_token, SF_OPPORTUNITIES_URL, opportunity_field_sets, "Opportunity")
        if not opportunity_fields:
            logger.warning("All opportunity field sets failed, testing individual fields...")
            opportunity_fields = debug_individual_fields(access_token, SF_OPPORTUNITIES_URL, get_extended_opportunity_fields(), "Opportunity")
        if not opportunity_fields or len(opportunity_fields) <= 1:
            logger.error("Could not find any working Opportunity fields")
            opportunity_df = pd.DataFrame()
        else:
            start_date = "2024-04-01T00:00:00Z"
            end_date = "2025-03-31T23:59:59Z"
            opportunity_query = f"SELECT {', '.join(opportunity_fields)} FROM Opportunity WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date} ORDER BY CreatedDate DESC"
            opportunity_url = SF_OPPORTUNITIES_URL + quote(opportunity_query)
            logger.info(f"Executing opportunity query with {len(opportunity_fields)} fields: {opportunity_field_set_used or 'custom'}")
            
            opportunity_resp = requests.get(opportunity_url, headers=headers, timeout=60)
            if opportunity_resp.status_code != 200:
                logger.error(f"Opportunity query failed: {opportunity_resp.status_code} - {opportunity_resp.text}")
                opportunity_df = pd.DataFrame()
            else:
                opportunities_json = opportunity_resp.json()
                opportunities_records = opportunities_json.get('records', [])
                all_opportunities = opportunities_records
                while 'nextRecordsUrl' in opportunities_json:
                    next_url = "https://waveinfratech.my.salesforce.com" + opportunities_json['nextRecordsUrl']
                    opportunity_resp = requests.get(next_url, headers=headers, timeout=60)
                    if opportunity_resp.status_code != 200:
                        logger.error(f"Failed to fetch next opportunity page: {opportunity_resp.status_code} - {opportunity_resp.text}")
                        break
                    opportunities_json = opportunity_resp.json()
                    all_opportunities.extend(opportunities_json.get('records', []))
                
                clean_opportunity_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_opportunities]
                opportunity_df = pd.DataFrame(clean_opportunity_records)
                opportunity_df = make_arrow_compatible(opportunity_df)
                logger.info(f"Successfully loaded {len(opportunity_df)} opportunities")
                logger.info(f"opportunity_df columns: {list(opportunity_df.columns)}")
                logger.info(f"opportunity_df dtypes:\n{opportunity_df.dtypes}")
                for col in ['StageName', 'Amount', 'CloseDate', 'Opportunity_Type__c']:
                    if col in opportunity_df.columns:
                        logger.info(f"Sample {col} values: {opportunity_df[col].dropna().unique()[:5]}")
                if 'CreatedDate' in opportunity_df.columns:
                    opportunity_df['CreatedDate'] = pd.to_datetime(opportunity_df['CreatedDate'], utc=True, errors='coerce')
                    invalid_dates = opportunity_df['CreatedDate'].isna().sum()
                    logger.info(f"Number of invalid opportunity CreatedDate values: {invalid_dates}")
                    if invalid_dates > 0:
                        logger.warning(f"Found {invalid_dates} opportunities with invalid CreatedDate values")
                    sample_dates = opportunity_df['CreatedDate'].dropna().head(5).tolist()
                    logger.info(f"Sample opportunity CreatedDate values: {sample_dates}")

        # Load Task data
        task_field_sets = {
            'minimal': get_minimal_task_fields(),
            'standard': get_standard_task_fields(),
            'extended': get_extended_task_fields()
        }
        task_fields, task_field_set_used = test_fields_incrementally(access_token, SF_TASKS_URL, task_field_sets, "Task")
        if not task_fields:
            logger.warning("All task field sets failed, testing individual fields...")
            task_fields = debug_individual_fields(access_token, SF_TASKS_URL, get_extended_task_fields(), "Task")
        if not task_fields or len(task_fields) <= 1:
            logger.error("Could not find any working Task fields")
            task_df = pd.DataFrame()
        else:
            start_date = "2024-04-01T00:00:00Z"
            end_date = "2025-03-31T23:59:59Z"
            task_query = f"SELECT {', '.join(task_fields)} FROM Task WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date} ORDER BY CreatedDate DESC"
            task_url = SF_TASKS_URL + quote(task_query)
            logger.info(f"Executing task query with {len(task_fields)} fields: {task_field_set_used or 'custom'}")
            
            task_resp = requests.get(task_url, headers=headers, timeout=60)
            if task_resp.status_code != 200:
                logger.error(f"Task query failed: {task_resp.status_code} - {task_resp.text}")
                task_df = pd.DataFrame()
            else:
                tasks_json = task_resp.json()
                tasks_records = tasks_json.get('records', [])
                all_tasks = tasks_records
                while 'nextRecordsUrl' in tasks_json:
                    next_url = "https://waveinfratech.my.salesforce.com" + tasks_json['nextRecordsUrl']
                    task_resp = requests.get(next_url, headers=headers, timeout=60)
                    if task_resp.status_code != 200:
                        logger.error(f"Failed to fetch next task page: {task_resp.status_code} - {task_resp.text}")
                        break
                    tasks_json = task_resp.json()
                    all_tasks.extend(tasks_json.get('records', []))
                
                clean_task_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_tasks]
                task_df = pd.DataFrame(clean_task_records)
                task_df = make_arrow_compatible(task_df)
                logger.info(f"Successfully loaded {len(task_df)} tasks")
                logger.info(f"task_df columns: {list(task_df.columns)}")
                logger.info(f"task_df dtypes:\n{task_df.dtypes}")
                for col in ['Status', 'Follow_Up_Status__c', 'Customer_Feedback__c', 'Subject', 'Transfer_Status__c']:
                    if col in task_df.columns:
                        logger.info(f"Sample {col} values: {task_df[col].dropna().unique()[:5]}")
                if 'CreatedDate' in task_df.columns:
                    task_df['CreatedDate'] = pd.to_datetime(task_df['CreatedDate'], utc=True, errors='coerce')
                    invalid_dates = task_df['CreatedDate'].isna().sum()
                    logger.info(f"Number of invalid task CreatedDate values: {invalid_dates}")
                    if invalid_dates > 0:
                        logger.warning(f"Found {invalid_dates} tasks with invalid CreatedDate values")
                    sample_dates = task_df['CreatedDate'].dropna().head(5).tolist()
                    logger.info(f"Sample task CreatedDate values: {sample_dates}")

        return lead_df, user_df, case_df, event_df, opportunity_df, task_df, None
    except Exception as e:
        error_msg = f"Error loading Salesforce data: {str(e)}"
        logger.error(error_msg)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), error_msg
