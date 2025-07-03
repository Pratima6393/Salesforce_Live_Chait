import aiohttp
import asyncio
import pandas as pd
from urllib.parse import quote
from config import (
    client_id, client_secret, username, password, login_url, 
    SF_LEADS_URL, SF_USERS_URL, SF_CASES_URL, SF_EVENTS_URL, SF_OPPORTUNITIES_URL, SF_TASKS_URL,
    get_minimal_lead_fields, get_standard_lead_fields, get_extended_lead_fields,
    get_safe_user_fields, get_minimal_user_fields, get_standard_user_fields, get_extended_user_fields, get_minimal_case_fields, get_standard_case_fields, get_extended_case_fields,
    get_minimal_event_fields, get_standard_event_fields, get_extended_event_fields,
    get_minimal_opportunity_fields, get_standard_opportunity_fields, get_extended_opportunity_fields,
    get_minimal_task_fields, get_standard_task_fields, get_extended_task_fields,
    logger
)

async def get_access_token():
    if not all([client_id, client_secret, username, password, login_url]):
        raise ValueError("Missing required Salesforce credentials in environment variables")
    payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(login_url, data=payload, timeout=30) as res:
                res.raise_for_status()
                token_data = await res.json()
                return token_data['access_token']
    except Exception as e:
        logger.error(f"Failed to authenticate with Salesforce: {e}")
        raise

async def test_fields_incrementally(session, access_token, base_url, field_sets, object_type="Lead"):
    headers = {'Authorization': f'Bearer {access_token}'}
    field_sets_ordered = {'extended': field_sets['extended'], 'standard': field_sets['standard'], 'minimal': field_sets['minimal']}
    for field_set_name, fields in field_sets_ordered.items():
        test_query = f"SELECT {', '.join(fields)} FROM {object_type} LIMIT 1"
        test_url = base_url + quote(test_query)
        try:
            async with session.get(test_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    logger.info(f"✅ {object_type} {field_set_name} fields work fine")
                    return fields, field_set_name
                else:
                    text = await response.text()
                    logger.warning(f"❌ {object_type} {field_set_name} failed: {response.status} - {text[:200]}")
        except Exception as e:
            logger.warning(f"❌ {object_type} {field_set_name} error: {e}")
    return None, None

async def debug_individual_fields(session, access_token, base_url, fields_to_test, object_type="Lead"):
    headers = {'Authorization': f'Bearer {access_token}'}
    working_fields = ['Id']
    problematic_fields = []
    for field in fields_to_test:
        if field == 'Id':
            continue
        test_query = f"SELECT Id, {field} FROM {object_type} LIMIT 1"
        test_url = base_url + quote(test_query)
        try:
            async with session.get(test_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    working_fields.append(field)
                    logger.info(f"✅ {object_type} {field} - OK")
                else:
                    text = await response.text()
                    problematic_fields.append(field)
                    logger.warning(f"❌ {object_type} {field} - FAILED: {text[:100]}")
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

async def fetch_all_pages(session, start_url, headers):
    all_records = []
    next_url = start_url
    while next_url:
        try:
            async with session.get(next_url, headers=headers, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    all_records.extend(records)
                    next_url = "https://waveinfratech.my.salesforce.com" + data['nextRecordsUrl'] if 'nextRecordsUrl' in data else None
                else:
                    text = await response.text()
                    logger.error(f"Failed to fetch page: {response.status} - {text}")
                    break
        except Exception as e:
            logger.error(f"Error during pagination: {str(e)}")
            break
    return all_records

async def load_object_data(session, access_token, base_url, field_sets, object_type, date_filter=True):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Field selection
    field_sets_dict = {
        'minimal': field_sets['minimal'],
        'standard': field_sets['standard'],
        'extended': field_sets['extended']
    }
    fields, field_set_used = await test_fields_incrementally(session, access_token, base_url, field_sets_dict, object_type)
    
    if not fields:
        logger.warning(f"All {object_type} field sets failed, testing individual fields...")
        fields = await debug_individual_fields(session, access_token, base_url, field_sets['extended'], object_type)
    
    if not fields or len(fields) <= 1:
        logger.error(f"Could not find any working {object_type} fields")
        return pd.DataFrame()

    # Build query
    start_date = "2024-04-01T00:00:00Z"
    end_date = "2025-03-31T23:59:59Z"
    date_clause = f" WHERE CreatedDate >= {start_date} AND CreatedDate <= {end_date}" if date_filter else ""
    query = f"SELECT {', '.join(fields)} FROM {object_type}{date_clause} ORDER BY CreatedDate DESC"
    initial_url = base_url + quote(query)
    logger.info(f"Executing {object_type} query with {len(fields)} fields: {field_set_used or 'custom'}")

    # Fetch data
    try:
        all_records = await fetch_all_pages(session, initial_url, headers)
        if not all_records:
            logger.warning(f"No {object_type} records found")
            return pd.DataFrame()
        
        clean_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in all_records]
        df = pd.DataFrame(clean_records)
        df = make_arrow_compatible(df)
        logger.info(f"Successfully loaded {len(df)} {object_type}s")
        
        # Log sample data
        if 'CreatedDate' in df.columns:
            df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], utc=True, errors='coerce')
            invalid_dates = df['CreatedDate'].isna().sum()
            logger.info(f"Invalid CreatedDate values: {invalid_dates}")
            if invalid_dates > 0:
                logger.warning(f"Found {invalid_dates} {object_type}s with invalid CreatedDate values")
        
        return df
    except Exception as e:
        logger.error(f"Error loading {object_type} data: {str(e)}")
        return pd.DataFrame()

async def load_users(session, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        user_fields = get_safe_user_fields()
        user_query = f"SELECT {', '.join(user_fields)} FROM User WHERE IsActive = true LIMIT 200"
        user_url = SF_USERS_URL + quote(user_query)
        
        async with session.get(user_url, headers=headers, timeout=30) as response:
            if response.status == 200:
                users_json = await response.json()
                users_records = users_json.get('records', [])
                clean_records = [{k: v for k, v in record.items() if k != 'attributes'} for record in users_records]
                df = pd.DataFrame(clean_records)
                df = make_arrow_compatible(df)
                logger.info(f"Successfully loaded {len(df)} users")
                return df
            else:
                text = await response.text()
                logger.warning(f"User query failed: {response.status} - {text}")
                return pd.DataFrame()
    except Exception as e:
        logger.warning(f"User query error: {e}")
        return pd.DataFrame()

async def load_salesforce_data_async():
    try:
        access_token = await get_access_token()
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Prepare tasks for concurrent execution
            tasks = [
                load_object_data(
                    session, access_token, SF_LEADS_URL,
                    {'minimal': get_minimal_lead_fields(), 
                     'standard': get_standard_lead_fields(), 
                     'extended': get_extended_lead_fields()},
                    "Lead"
                ),
                load_object_data(
                    session, access_token, SF_USERS_URL,
                    {'minimal': get_minimal_user_fields(), 
                     'standard': get_standard_user_fields(), 
                     'extended': get_extended_user_fields()},
                    "User",
                    date_filter=False  # Remove date filter for User data
                ),
                load_object_data(
                    session, access_token, SF_CASES_URL,
                    {'minimal': get_minimal_case_fields(), 
                     'standard': get_standard_case_fields(), 
                     'extended': get_extended_case_fields()},
                    "Case"
                ),
                load_object_data(
                    session, access_token, SF_EVENTS_URL,
                    {'minimal': get_minimal_event_fields(), 
                     'standard': get_standard_event_fields(), 
                     'extended': get_extended_event_fields()},
                    "Event"
                ),
                load_object_data(
                    session, access_token, SF_OPPORTUNITIES_URL,
                    {'minimal': get_minimal_opportunity_fields(), 
                     'standard': get_standard_opportunity_fields(), 
                     'extended': get_extended_opportunity_fields()},
                    "Opportunity"
                ),
                load_object_data(
                    session, access_token, SF_TASKS_URL,
                    {'minimal': get_minimal_task_fields(), 
                     'standard': get_standard_task_fields(), 
                     'extended': get_extended_task_fields()},
                    "Task"
                )
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks)
            
            # Unpack results
            lead_df, user_df, case_df, event_df, opportunity_df, task_df = results
            return lead_df, user_df, case_df, event_df, opportunity_df, task_df, None
            
    except Exception as e:
        error_msg = f"Error loading Salesforce data: {str(e)}"
        logger.error(error_msg)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), error_msg

def load_salesforce_data():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(load_salesforce_data_async())
    except Exception as e:
        error_msg = f"Error in event loop: {str(e)}"
        logger.error(error_msg)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), error_msg