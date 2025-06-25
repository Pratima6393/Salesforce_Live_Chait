# # config.py
# import os
# from dotenv import load_dotenv

# # Configure logging
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# # Salesforce credentials
# client_id = os.getenv('SF_CLIENT_ID')
# client_secret = os.getenv('SF_CLIENT_SECRET')
# username = os.getenv('SF_USERNAME')
# password = os.getenv('SF_PASSWORD')
# login_url = os.getenv('SF_LOGIN_URL')
# SF_LEADS_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
# SF_USERS_URL = "https://waveinfratech.my.salesforce.com/services/data/v61.0/query/?q="
# SF_CASES_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
# SF_EVENTS_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
# SF_OPPORTUNITIES_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
# SF_TASKS_URL = "https://waveinfratech.my.salesforce.com/services/data/v62.0/query/?q="

# # WatsonX configuration
# WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
# WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
# WATSONX_URL = os.getenv('WATSONX_URL')
# WATSONX_MODEL_ID = os.getenv('WATSONX_MODEL_ID')
# IBM_CLOUD_IAM_URL = os.getenv('IBM_CLOUD_IAM_URL')

# # Define query limits
# LEAD_QUERY_LIMIT = 30000
# CASE_QUERY_LIMIT = 30000
# EVENT_QUERY_LIMIT = 30000

# # Field mappings for Salesforce objects

# LEAD_FIELD_MAPPING = {
#     'id': 'Id',
#     'lead_id__c': 'Lead_Id__c',
#     'customer_feedback__c': 'Customer_Feedback__c',
#     'city__c': 'City__c',
#     'leadsource': 'LeadSource',
#     'lead_source_sub_category__c': 'Lead_Source_Sub_Category__c',
#     'project_category__c': 'Project_Category__c',
#     'project__c': 'Project__c',
#     'property_size__c': 'Property_Size__c',
#     'property_type__c': 'Property_Type__c',
#     'budget_range__c': 'Budget_Range__c',
#     'rating': 'Rating',
#     'status': 'Status',
#     'Contact_Medium__c': 'Contact_Medium__c',
#     'ownerid': 'OwnerId',
#     'createddate': 'CreatedDate',
#     'open_lead_reasons__c': 'Open_Lead_reasons__c',
#     'junk_reason__c': 'Junk_Reason__c',
#     'disqualification_date__c': 'Disqualification_Date__c',
#     'disqualification_reason__c': 'Disqualification_Reason__c',
#     'disqualified_date_time__c': 'Disqualified_Date_Time__c',
#     'Transfer_Status__c'        :  'Transfer_Status__c',
#     'is_appointment_booked__c': 'Is_Appointment_Booked__c',
#     'lead_converted__c': 'Lead_Converted__c'
     
# }


# USER_FIELD_MAPPING = {
#     'id': 'Id',
#     'first_name': 'FirstName',
#     'firstname': 'FirstName',
#     'last_name': 'LastName',
#     'lastname': 'LastName',
#     'name': 'Name',
#     'email': 'Email',
#     'username': 'Username',
#     'profile': 'ProfileId',
#     'profileid': 'ProfileId',
#     'role': 'UserRoleId',
#     'userroleid': 'UserRoleId',
#     'is_active': 'IsActive',
#     'isactive': 'IsActive',
#     'created_date': 'CreatedDate',
#     'createddate': 'CreatedDate',
#     'last_login_date': 'LastLoginDate',
#     'lastlogindate': 'LastLoginDate'
# }

# CASE_FIELD_MAPPING = {
#     'id': 'Id',
#     'action_taken__c': 'Action_Taken__c',
#     'back_office_date__c': 'Back_Office_Date__c',
#     'back_office_remarks__c': 'Back_Office_Remarks__c',
#     'corporate_closure_remark__c': 'Corporate_Closure_Remark__c',
#     'corporate_closure_by__c': 'Corporate_Closure_by__c',
#     'corporate_closure_date__c': 'Corporate_Closure_date__c',
#     'description': 'Description',
#     'feedback__c': 'Feedback__c',
#     'first_assigned_by__c': 'First_Assigned_By__c',
#     'first_assigned_to__c': 'First_Assigned_To__c',
#     'first_assigned_on_date_and_time__c': 'First_Assigned_on_Date_and_Time__c',
#     'opportunity__c': 'Opportunity__c',
#     'origin': 'Origin',
#     're_assigned_by1__c': 'Re_Assigned_By1__c',
#     're_assigned_on_date_and_time__c': 'Re_Assigned_On_Date_And_Time__c',
#     're_assigned_to__c': 'Re_Assigned_To__c',
#     're_open_date_and_time__c': 'Re_Open_Date_and_time__c',
#     're_open_by__c': 'Re_Open_by__c',
#     'resolved_by__c': 'Resolved_By__c',
#     'service_request_number__c': 'Service_Request_Number__c',
#     'service_request_type__c': 'Service_Request_Type__c',
#     'service_sub_category__c': 'Service_Sub_catogery__c',
#     'subject': 'Subject',
#     'type': 'Type',
#     'createddate': 'CreatedDate'
# }


# EVENT_FIELD_MAPPING = {
#     'id': 'Id',
#     'account_id': 'AccountId',
#     'appointment_status__c': 'Appointment_Status__c',
#     'created_by_id': 'CreatedById',
#     'created_date': 'CreatedDate'
# }

# OPPORTUNITY_FIELD_MAPPING = {
#     'id': 'Id',
#     'Lead_Id__c': 'Lead_Id__c',
#     'Project__c': 'Project__c',
#     'Project_Category__c': 'Project_Category__c',
#     'CreatedById': 'CreatedById',
#     'OwnerId': 'OwnerId',
#     'CreatedDate': 'CreatedDate',
#     'LeadSource': 'LeadSource',
#     'Lead_Source_Sub_Category__c': 'Lead_Source_Sub_Category__c',
#     'Lead_Rating_By_Sales__c': 'Lead_Rating_By_Sales__c',
#     'Range_Budget__c': 'Range_Budget__c',
#     'Property_Type__c': 'Property_Type__c',
#     'Property_Size__c': 'Property_Size__c',
#     'Sales_Team_Feedback__c': 'Sales_Team_Feedback__c',
#     'Sales_Open_Reason__c': 'Sales_Open_Reason__c',
#     'Disqualification_Reason__c': 'Disqualification_Reason__c',
#     'Disqualified_Date__c': 'Disqualified_Date__c',
#     'StageName': 'StageName',
#     'SAP_Customer_code__c': 'SAP_Customer_code__c',
#     'Registration_Number__c': 'Registration_Number__c',
#     'Sales_Order_Number__c': 'Sales_Order_Number__c',
#     'Sales_Order_Date__c':  'Sales_Order_Date__c',
#     'Age__c': 'Age__c',
#     'SAP_City__c': 'SAP_City__c',
#     'Country_SAP__c': 'Country_SAP__c',
#     'State__c  ': 'State__c  '
# }
# # Display name mappings for user-friendly output
# # Field mappings for Salesforce Task object
# TASK_FIELD_MAPPING = {
#     'id': 'Id',
#     'lead_id__c': 'Lead_Id__c',
#     'opp_lead_id__c': 'Opp_Lead_Id__c',
#     'transfer_status__c': 'Transfer_Status__c',
#     'customer_feedback__c': 'Customer_Feedback__c',
#     'sales_team_feedback__c': 'Sales_Team_Feedback__c',
#     'status': 'Status',
#     'follow_up_status__c': 'Follow_Up_Status__c',
#     'subject': 'Subject',
#     'ownerid': 'OwnerId',
#     'createdbyid': 'CreatedById'
# }
# #==========================================
# # Display name mappings for user-friendly output
# TASK_FIELD_DISPLAY_NAMES = {
#     'id': 'Id',
#     'lead_id__c': 'Lead_Id__c',
#     'opp_lead_id__c': 'Opp_Lead_Id__c',
#     'transfer_status__c': 'Transfer_Status__c',
#     'customer_feedback__c': 'Customer_Feedback__c',
#     'sales_team_feedback__c': 'Sales_Team_Feedback__c',
#     'status': 'Status',
#     'follow_up_status__c': 'Follow_Up_Status__c',
#     'subject': 'Subject',
#     'ownerid': 'OwnerId',
#     'createdbyid': 'CreatedById'
# }

# # Possible values for categorical fields (for validation or dropdowns)
# TASK_FIELD_VALUES = {
#     'Status': ['Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred'],
#     'Follow_Up_Status__c': ['Pending', 'Completed', 'Overdue', 'Not Required'],
#     'Customer_Feedback__c': ['Junk', 'Positive', 'Negative', 'Neutral', 'Interested', 'Not Interested'],
#     'Transfer_Status__c': ['Pending', 'Transferred', 'Rejected']
# }

# # Field types for validation or formatting
# TASK_FIELD_TYPES = {
#     'Id': 'string',
#     'Lead_Id__c': 'string',
#     'Opp_Lead_Id__c': 'string',
#     'Transfer_Status__c': 'category',
#     'Customer_Feedback__c': 'category',
#     'Sales_Team_Feedback__c': 'string',
#     'Status': 'category',
#     'Follow_Up_Status__c': 'category',
#     'Subject': 'string',
#     'OwnerId': 'string',
#     'CreatedById': 'string'
# }
# #===============================================

# FIELD_DISPLAY_NAMES = {
#     'id': 'Id',
#     'lead_id__c': 'Lead_Id__c',
#     'customer_feedback__c': 'Customer_Feedback__c',
#     'city__c': 'City__c',
#     'leadsource': 'LeadSource',
#     'lead_source_sub_category__c': 'Lead_Source_Sub_Category__c',
#     'project_category__c': 'Project_Category__c',
#     'project__c': 'Project__c',
#     'property_size__c': 'Property_Size__c',
#     'property_type__c': 'Property_Type__c',
#     'budget_range__c': 'Budget_Range__c',
#     'rating': 'Rating',
#     'status': 'Status',
#     'Contact_Medium__c': 'Contact_Medium__c',
#     'ownerid': 'OwnerId',
#     'createddate': 'CreatedDate',
#     'open_lead_reasons__c': 'Open_Lead_reasons__c',
#     'junk_reason__c': 'Junk_Reason__c',
#     'disqualification_date__c': 'Disqualification_Date__c',
#     'disqualification_reason__c': 'Disqualification_Reason__c',
#     'disqualified_date_time__c': 'Disqualified_Date_Time__c',
#     'Transfer_Status__c'        :  'Transfer_Status__c',
#     'is_appointment_booked__c':  'is_appointment_booked__c',
#     'lead_converted__c': 'lead_converted__c'
    
    
# }

# # Possible values for categorical fields (for validation or dropdowns)
# FIELD_VALUES = {
#     'Status': ['Qualified', 'Unqualified', 'Open', 'Converted', 'Disqualified'],
#     'LeadSource': ['Website', 'Facebook', 'Google Ads', 'Referral', 'Email Campaign', 'Event', 'Phone Inquiry'],
#     'Property_Size__c': ['1BHK', '2BHK', '3BHK', '4BHK', 'Villa'],
#     'Property_Type__c': ['Apartment', 'Independent House', 'Villa', 'Plot', 'Commercial'],
#     'Purpose_of_Purchase__c': ['Investment', 'Self-Use', 'Rental', 'Resale'],
#     'Budget_Range__c': ['<1Cr', '1-2Cr', '1.5Cr', '2-3Cr', '3-5Cr', '>5Cr'],
#     'Contact_on_Whatsapp__c': ['Yes', 'No'],
#     'Lead_Converted__c': ['Yes', 'No'],
#     'Same_As_Permanent_Address__c': ['Yes', 'No'],
#     #'Is_Junk__c': ['Yes', 'No'],  # Removed as per requirement
#     'Is_Appointment_Booked__c': ['Yes', 'No'],
#     'Customer_Interested__c': ['Yes', 'No'],
#     'Customer_feedback_is_junk__c': ['Yes', 'No'],
#     'Customer_Feedback__c': ['Junk', 'Positive', 'Negative', 'Neutral', 'Interested', 'Not Interested']
# }

# # Field types for validation or formatting
# FIELD_TYPES = {
#     'CreatedDate': 'datetime',
#     'Follow_Up_Date_Time__c': 'datetime',
#     'Disqualification_Date__c': 'date',
#     'Disqualified_Date_Time__c': 'datetime',
#     'Preferred_Date_of_Visit__c': 'date',
#     'Preferred_Time_of_Visit__c': 'time',
#     'Phone__c': 'string',
#     'Mobile__c': 'string',
#     'Email__c': 'email',
#     'IP_Address__c': 'string',
#     'Budget_Range__c': 'category',
#     'Property_Size__c': 'category',
#     'Status': 'category',
#     'LeadSource': 'category',
#     'Max_Price__c': 'float',
#     'Min_Price__c': 'float',
#     'Customer_Feedback__c': 'category'
# }

# def get_minimal_lead_fields():
#     return [
#         'Id', 'Lead_Id__c','Customer_Feedback__c','Junk_Reason__c ', 'City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
#                  'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
#                  'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
#                  'Disqualified_Date_Time__c' , 'lead_converted__c', 'Disqualification_Date__c', 'is_appointment_booked__c'
#     ]

# def get_standard_lead_fields():
#     return [
#        'Id', 'Lead_Id__c','Customer_Feedback__c','Junk_Reason__c ', 'City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
#                  'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
#                  'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
#                  'Disqualified_Date_Time__c' , 'lead_converted__c', 'Disqualification_Date__c', 'is_appointment_booked__c'
#     ]


# def get_extended_lead_fields():
#     return [
#         'Id', 'Lead_Id__c','Customer_Feedback__c', 'Junk_Reason__c ','City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
#                  'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
#                  'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
#                  'Disqualified_Date_Time__c' ,  'lead_converted__c', 'Disqualification_Date__c', 'is_appointment_booked__c'
#     ]

# def get_safe_user_fields():
#     return ['Id', 'Name', 'FirstName', 'LastName', 'Email', 'IsActive', 'CreatedDate']

# def get_minimal_case_fields():
#     return [
#         'Id', 'Service_Request_Number__c', 'Type', 'Subject', 'CreatedDate',
#         'Origin', 'Feedback__c', 'Corporate_Closure_Remark__c'
#     ]

# def get_standard_case_fields():
#     return [
#         'Id', 'Service_Request_Number__c', 'Type', 'Subject', 'Origin',
#         'CreatedDate', 'Corporate_Closure_by__c', 'Corporate_Closure_date__c',
#         'Description', 'Feedback__c'
#     ]

# def get_extended_case_fields():
#     return [
#         'Id', 'Action_Taken__c', 'Back_Office_Date__c', 'Back_Office_Remarks__c',
#         'Corporate_Closure_Remark__c', 'Corporate_Closure_by__c', 'Corporate_Closure_date__c',
#         'Description', 'Feedback__c', 'First_Assigned_By__c', 'First_Assigned_To__c',
#         'First_Assigned_on_Date_and_Time__c', 'Opportunity__c', 'Origin',
#         'Re_Assigned_By1__c', 'Re_Assigned_On_Date_And_Time__c', 'Re_Assigned_To__c',
#         'Re_Open_Date_and_time__c', 'Re_Open_by__c', 'Resolved_By__c',
#         'Service_Request_Number__c', 'Service_Request_Type__c', 'Service_Sub_catogery__c',
#         'Subject', 'Type', 'CreatedDate'
#     ]
    
# def get_minimal_event_fields():
#     return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedDate']

# def get_standard_event_fields():
#     return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedById', 'CreatedDate']


# def get_extended_event_fields():
#     return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedById', 'CreatedDate', 'WhoId']


# def get_minimal_opportunity_fields():
#     return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
#     'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
#     'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
#     'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
#     'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
#     'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ' ]

# def get_standard_opportunity_fields():
#     return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
#     'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
#     'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
#     'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
#     'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
#     'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ']

# def get_extended_opportunity_fields():
#     return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
#     'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
#     'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
#     'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
#     'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
#     'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ']
    
    
# # Functions to get Task fields
# def get_minimal_task_fields():
#     return [
#         'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
#         'Customer_Feedback__c', 'Status', 'Subject', 'OwnerId', 'CreatedById'
#     ]

# def get_standard_task_fields():
#     return [
#         'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
#         'Customer_Feedback__c', 'Sales_Team_Feedback__c', 'Status',
#         'Follow_Up_Status__c', 'Subject', 'OwnerId', 'CreatedById'
#     ]

# def get_extended_task_fields():
#     return [
#         'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
#         'Customer_Feedback__c', 'Sales_Team_Feedback__c', 'Status',
#         'Follow_Up_Status__c', 'Subject', 'OwnerId', 'CreatedById'
#     ]

#==================================new code======================
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

client_id = os.getenv('SF_CLIENT_ID')
client_secret = os.getenv('SF_CLIENT_SECRET')
username = os.getenv('SF_USERNAME')
password = os.getenv('SF_PASSWORD')
login_url = os.getenv('SF_LOGIN_URL')
SF_LEADS_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
SF_USERS_URL = "https://waveinfratech.my.salesforce.com/services/data/v61.0/query/?q="
SF_CASES_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
SF_EVENTS_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
SF_OPPORTUNITIES_URL = "https://waveinfratech.my.salesforce.com/services/data/v58.0/query/?q="
SF_TASKS_URL = "https://waveinfratech.my.salesforce.com/services/data/v62.0/query/?q="

# WatsonX configuration
WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
WATSONX_URL = os.getenv('WATSONX_URL')
WATSONX_MODEL_ID = os.getenv('WATSONX_MODEL_ID')
IBM_CLOUD_IAM_URL = os.getenv('IBM_CLOUD_IAM_URL')


LEAD_QUERY_LIMIT = 30000
CASE_QUERY_LIMIT = 30000
EVENT_QUERY_LIMIT = 30000

LEAD_FIELD_MAPPING = {
    'id': 'Id',
    'lead_id__c': 'Lead_Id__c',
    'customer_feedback__c': 'Customer_Feedback__c',
    'city__c': 'City__c',
    'leadsource': 'LeadSource',
    'lead_source_sub_category__c': 'Lead_Source_Sub_Category__c',
    'project_category__c': 'Project_Category__c',
    'project__c': 'Project__c',
    'property_size__c': 'Property_Size__c',
    'property_type__c': 'Property_Type__c',
    'budget_range__c': 'Budget_Range__c',
    'rating': 'Rating',
    'status': 'Status',
    'Contact_Medium__c': 'Contact_Medium__c',
    'ownerid': 'OwnerId',
    'createddate': 'CreatedDate',
    'open_lead_reasons__c': 'Open_Lead_reasons__c',
    'junk_reason__c': 'Junk_Reason__c',
    'disqualification_date__c': 'Disqualification_Date__c',
    'disqualification_reason__c': 'Disqualification_Reason__c',
    'disqualified_date_time__c': 'Disqualified_Date_Time__c',
    'Transfer_Status__c'        :  'Transfer_Status__c',
    'is_appointment_booked__c': 'Is_Appointment_Booked__c',
    'lead_converted__c': 'Lead_Converted__c'
     
}


USER_FIELD_MAPPING = {
    'id': 'Id',
    'first_name': 'FirstName',
    'firstname': 'FirstName',
    'last_name': 'LastName',
    'lastname': 'LastName',
    'name': 'Name',
    'email': 'Email',
    'Department': 'Department',
    'username': 'Username',
    'profile': 'ProfileId',
    'profileid': 'ProfileId',
    'role': 'UserRoleId',
    'userroleid': 'UserRoleId',
    'is_active': 'IsActive',
    'isactive': 'IsActive',
    'created_date': 'CreatedDate',
    'createddate': 'CreatedDate',
    'last_login_date': 'LastLoginDate',
    'lastlogindate': 'LastLoginDate'
}

CASE_FIELD_MAPPING = {
    'id': 'Id',
    'action_taken__c': 'Action_Taken__c',
    'back_office_date__c': 'Back_Office_Date__c',
    'back_office_remarks__c': 'Back_Office_Remarks__c',
    'corporate_closure_remark__c': 'Corporate_Closure_Remark__c',
    'corporate_closure_by__c': 'Corporate_Closure_by__c',
    'corporate_closure_date__c': 'Corporate_Closure_date__c',
    'description': 'Description',
    'feedback__c': 'Feedback__c',
    'first_assigned_by__c': 'First_Assigned_By__c',
    'first_assigned_to__c': 'First_Assigned_To__c',
    'first_assigned_on_date_and_time__c': 'First_Assigned_on_Date_and_Time__c',
    'opportunity__c': 'Opportunity__c',
    'origin': 'Origin',
    're_assigned_by1__c': 'Re_Assigned_By1__c',
    're_assigned_on_date_and_time__c': 'Re_Assigned_On_Date_And_Time__c',
    're_assigned_to__c': 'Re_Assigned_To__c',
    're_open_date_and_time__c': 'Re_Open_Date_and_time__c',
    're_open_by__c': 'Re_Open_by__c',
    'resolved_by__c': 'Resolved_By__c',
    'service_request_number__c': 'Service_Request_Number__c',
    'service_request_type__c': 'Service_Request_Type__c',
    'service_sub_category__c': 'Service_Sub_catogery__c',
    'subject': 'Subject',
    'type': 'Type',
    'createddate': 'CreatedDate'
}


EVENT_FIELD_MAPPING = {
    'id': 'Id',
    'account_id': 'AccountId',
    'appointment_status__c': 'Appointment_Status__c',
    'created_by_id': 'CreatedById',
    'created_date': 'CreatedDate',
    'owner_id':'OwnerId'
}

OPPORTUNITY_FIELD_MAPPING = {
    'id': 'Id',
    'Lead_Id__c': 'Lead_Id__c',
    'Project__c': 'Project__c',
    'Project_Category__c': 'Project_Category__c',
    'CreatedById': 'CreatedById',
    'OwnerId': 'OwnerId',
    'CreatedDate': 'CreatedDate',
    'LeadSource': 'LeadSource',
    'Lead_Source_Sub_Category__c': 'Lead_Source_Sub_Category__c',
    'Lead_Rating_By_Sales__c': 'Lead_Rating_By_Sales__c',
    'Range_Budget__c': 'Range_Budget__c',
    'Property_Type__c': 'Property_Type__c',
    'Property_Size__c': 'Property_Size__c',
    'Sales_Team_Feedback__c': 'Sales_Team_Feedback__c',
    'Sales_Open_Reason__c': 'Sales_Open_Reason__c',
    'Disqualification_Reason__c': 'Disqualification_Reason__c',
    'Disqualified_Date__c': 'Disqualified_Date__c',
    'StageName': 'StageName',
    'SAP_Customer_code__c': 'SAP_Customer_code__c',
    'Registration_Number__c': 'Registration_Number__c',
    'Sales_Order_Number__c': 'Sales_Order_Number__c',
    'Sales_Order_Date__c':  'Sales_Order_Date__c',
    'Age__c': 'Age__c',
    'SAP_City__c': 'SAP_City__c',
    'Country_SAP__c': 'Country_SAP__c',
    'State__c  ': 'State__c  '
}
# Display name mappings for user-friendly output
# Field mappings for Salesforce Task object
TASK_FIELD_MAPPING = {
    'id': 'Id',
    'lead_id__c': 'Lead_Id__c',
    'opp_lead_id__c': 'Opp_Lead_Id__c',
    'transfer_status__c': 'Transfer_Status__c',
    'customer_feedback__c': 'Customer_Feedback__c',
    'sales_team_feedback__c': 'Sales_Team_Feedback__c',
    'status': 'Status',
    'follow_up_status__c': 'Follow_Up_Status__c',
    'subject': 'Subject',
    'ownerid': 'OwnerId',
    'createdbyid': 'CreatedById'
}
#==========================================
# Display name mappings for user-friendly output
TASK_FIELD_DISPLAY_NAMES = {
    'id': 'Id',
    'lead_id__c': 'Lead_Id__c',
    'opp_lead_id__c': 'Opp_Lead_Id__c',
    'transfer_status__c': 'Transfer_Status__c',
    'customer_feedback__c': 'Customer_Feedback__c',
    'sales_team_feedback__c': 'Sales_Team_Feedback__c',
    'status': 'Status',
    'follow_up_status__c': 'Follow_Up_Status__c',
    'subject': 'Subject',
    'ownerid': 'OwnerId',
    'createdbyid': 'CreatedById'
}

# Possible values for categorical fields (for validation or dropdowns)
TASK_FIELD_VALUES = {
    'Status': ['Not Started', 'In Progress', 'Completed', 'Waiting on someone else', 'Deferred'],
    'Follow_Up_Status__c': ['Pending', 'Completed', 'Overdue', 'Not Required'],
    'Customer_Feedback__c': ['Junk', 'Positive', 'Negative', 'Neutral', 'Interested', 'Not Interested'],
    'Transfer_Status__c': ['Pending', 'Transferred', 'Rejected']
}

# Field types for validation or formatting
TASK_FIELD_TYPES = {
    'Id': 'string',
    'Lead_Id__c': 'string',
    'Opp_Lead_Id__c': 'string',
    'Transfer_Status__c': 'category',
    'Customer_Feedback__c': 'category',
    'Sales_Team_Feedback__c': 'string',
    'Status': 'category',
    'Follow_Up_Status__c': 'category',
    'Subject': 'string',
    'OwnerId': 'string',
    'CreatedById': 'string'
}
#===============================================

FIELD_DISPLAY_NAMES = {
    'id': 'Id',
    'lead_id__c': 'Lead_Id__c',
    'customer_feedback__c': 'Customer_Feedback__c',
    'city__c': 'City__c',
    'leadsource': 'LeadSource',
    'lead_source_sub_category__c': 'Lead_Source_Sub_Category__c',
    'project_category__c': 'Project_Category__c',
    'project__c': 'Project__c',
    'property_size__c': 'Property_Size__c',
    'property_type__c': 'Property_Type__c',
    'budget_range__c': 'Budget_Range__c',
    'rating': 'Rating',
    'status': 'Status',
    'Contact_Medium__c': 'Contact_Medium__c',
    'ownerid': 'OwnerId',
    'createddate': 'CreatedDate',
    'open_lead_reasons__c': 'Open_Lead_reasons__c',
    'junk_reason__c': 'Junk_Reason__c',
    'disqualification_date__c': 'Disqualification_Date__c',
    'disqualification_reason__c': 'Disqualification_Reason__c',
    'disqualified_date_time__c': 'Disqualified_Date_Time__c',
    'Transfer_Status__c'        :  'Transfer_Status__c',
    'is_appointment_booked__c':  'is_appointment_booked__c',
    'lead_converted__c': 'lead_converted__c'
    
    
}

# Possible values for categorical fields (for validation or dropdowns)
FIELD_VALUES = {
    'Status': ['Qualified', 'Unqualified', 'Open', 'Converted', 'Disqualified'],
    'LeadSource': ['Website', 'Facebook', 'Google Ads', 'Referral', 'Email Campaign', 'Event', 'Phone Inquiry'],
    'Property_Size__c': ['1BHK', '2BHK', '3BHK', '4BHK', 'Villa'],
    'Property_Type__c': ['Apartment', 'Independent House', 'Villa', 'Plot', 'Commercial'],
    'Purpose_of_Purchase__c': ['Investment', 'Self-Use', 'Rental', 'Resale'],
    'Budget_Range__c': ['<1Cr', '1-2Cr', '1.5Cr', '2-3Cr', '3-5Cr', '>5Cr'],
    'Contact_on_Whatsapp__c': ['Yes', 'No'],
    'Lead_Converted__c': ['Yes', 'No'],
    'Same_As_Permanent_Address__c': ['Yes', 'No'],
    #'Is_Junk__c': ['Yes', 'No'],  # Removed as per requirement
    'Is_Appointment_Booked__c': ['Yes', 'No'],
    'Customer_Interested__c': ['Yes', 'No'],
    'Customer_feedback_is_junk__c': ['Yes', 'No'],
    'Customer_Feedback__c': ['Junk', 'Positive', 'Negative', 'Neutral', 'Interested', 'Not Interested']
}

# Field types for validation or formatting
FIELD_TYPES = {
    'CreatedDate': 'datetime',
    'Follow_Up_Date_Time__c': 'datetime',
    'Disqualification_Date__c': 'date',
    'Disqualified_Date_Time__c': 'datetime',
    'Preferred_Date_of_Visit__c': 'date',
    'Preferred_Time_of_Visit__c': 'time',
    'Phone__c': 'string',
    'Mobile__c': 'string',
    'Email__c': 'email',
    'IP_Address__c': 'string',
    'Budget_Range__c': 'category',
    'Property_Size__c': 'category',
    'Status': 'category',
    'LeadSource': 'category',
    'Max_Price__c': 'float',
    'Min_Price__c': 'float',
    'Customer_Feedback__c': 'category'
}

def get_minimal_lead_fields():
    return [
        'Id', 'Lead_Id__c','Customer_Feedback__c','Junk_Reason__c ', 'City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
                 'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
                 'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
                 'Disqualified_Date_Time__c' , 'Lead_Converted__c', 'Disqualification_Date__c', 'is_appointment_booked__c'
    ]

def get_standard_lead_fields():
    return [
       'Id', 'Lead_Id__c','Customer_Feedback__c','Junk_Reason__c ', 'City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
                 'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
                 'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
                 'Disqualified_Date_Time__c' ,'Lead_Converted__c', 'Disqualification_Date__c', 'is_appointment_booked__c'
    ]


def get_extended_lead_fields():
    return [
        'Id', 'Lead_Id__c','Customer_Feedback__c', 'Junk_Reason__c ','City__c', 'LeadSource', 'Lead_Source_Sub_Category__c',
                 'Project__c', 'Project_Category__c', 'Budget_Range__c', 'Property_Size__c', 'Property_Type__c',  'Rating',
                 'Status', 'Contact_Medium__c', 'OwnerId', 'CreatedDate', 'Open_Lead_reasons__c','Transfer_Status__c','Disqualification_Reason__c',
                 'Disqualified_Date_Time__c' ,'Lead_Converted__c' ,'Disqualification_Date__c', 'is_appointment_booked__c'
    ]

def get_safe_user_fields():
    return ['Id', 'Name', 'FirstName', 'LastName', 'Email', 'Department', 'Username', 'UserRoleId',  'CreatedDate']


def get_minimal_user_fields():
    return ['Id', 'Name', 'FirstName', 'LastName', 'Email', 'Department', 'Username', 'UserRoleId',  'CreatedDate']

def get_standard_user_fields():
    return ['Id', 'Name', 'FirstName', 'LastName', 'Email', 'Department', 'Username', 'UserRoleId',  'CreatedDate']

def get_extended_user_fields():
    return ['Id', 'Name', 'FirstName', 'LastName', 'Email', 'Department', 'Username', 'UserRoleId',  'CreatedDate']
#===============================new code==============================


def get_minimal_case_fields():
    return [
        'Id', 'Service_Request_Number__c', 'Type', 'Subject', 'CreatedDate',
        'Origin', 'Feedback__c', 'Corporate_Closure_Remark__c'
    ]

def get_standard_case_fields():
    return [
        'Id', 'Service_Request_Number__c', 'Type', 'Subject', 'Origin',
        'CreatedDate', 'Corporate_Closure_by__c', 'Corporate_Closure_date__c',
        'Description', 'Feedback__c'
    ]

def get_extended_case_fields():
    return [
        'Id', 'Action_Taken__c', 'Back_Office_Date__c', 'Back_Office_Remarks__c',
        'Corporate_Closure_Remark__c', 'Corporate_Closure_by__c', 'Corporate_Closure_date__c',
        'Description', 'Feedback__c', 'First_Assigned_By__c', 'First_Assigned_To__c',
        'First_Assigned_on_Date_and_Time__c', 'Opportunity__c', 'Origin',
        'Re_Assigned_By1__c', 'Re_Assigned_On_Date_And_Time__c', 'Re_Assigned_To__c',
        'Re_Open_Date_and_time__c', 'Re_Open_by__c', 'Resolved_By__c',
        'Service_Request_Number__c', 'Service_Request_Type__c', 'Service_Sub_catogery__c',
        'Subject', 'Type', 'CreatedDate'
    ]
    
def get_minimal_event_fields():
    return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedDate', 'OwnerId']

def get_standard_event_fields():
    return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedById', 'CreatedDate', 'OwnerId']


def get_extended_event_fields():
    return ['Id', 'AccountId', 'Appointment_Status__c', 'CreatedById', 'CreatedDate', 'WhoId', 'OwnerId']


def get_minimal_opportunity_fields():
    return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
    'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
    'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
    'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
    'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
    'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ' ]

def get_standard_opportunity_fields():
    return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
    'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
    'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
    'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
    'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
    'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ']

def get_extended_opportunity_fields():
    return ['Id', 'Lead_Id__c', 'Project__c', 'Project_Category__c', 'CreatedById', 'OwnerId', 
    'CreatedDate', 'LeadSource', 'Lead_Source_Sub_Category__c', 'Lead_Rating_By_Sales__c', 
    'Range_Budget__c', 'Property_Type__c', 'Property_Size__c', 'Sales_Team_Feedback__c', 
    'Sales_Open_Reason__c', 'Disqualification_Reason__c', 'Disqualified_Date__c', 
    'StageName', 'SAP_Customer_code__c', 'Registration_Number__c', 'Sales_Order_Number__c', 
    'Sales_Order_Date__c', 'Age__c', 'SAP_City__c', 'Country_SAP__c', 'State__c ']
    
    
# Functions to get Task fields
def get_minimal_task_fields():
    return [
        'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
        'Customer_Feedback__c', 'Status', 'Subject', 'OwnerId', 'CreatedById'
    ]

def get_standard_task_fields():
    return [
        'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
        'Customer_Feedback__c', 'Sales_Team_Feedback__c', 'Status',
        'Follow_Up_Status__c', 'Subject', 'OwnerId', 'CreatedById'
    ]

def get_extended_task_fields():
    return [
        'Id', 'Lead_Id__c', 'Opp_Lead_Id__c', 'Transfer_Status__c',
        'Customer_Feedback__c', 'Sales_Team_Feedback__c', 'Status',
        'Follow_Up_Status__c', 'Subject', 'OwnerId', 'CreatedById'
    ]