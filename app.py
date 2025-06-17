
# #===============================new final code====================

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import json
# from datetime import datetime

# from config import (
#     client_id,
#     client_secret,
#     username,
#     password,
#     login_url,
#     WATSONX_URL,
#     WATSONX_PROJECT_ID,
#     WATSONX_MODEL_ID
# )

# from watsonx_utils import (
#     validate_watsonx_config,
#     create_data_context,
#     query_watsonx_ai,
#     parse_intent_fallback,
#     get_watsonx_token
# )
# from salesforce_utils import load_salesforce_data
# from analysis_engine import execute_analysis, display_analysis_result
# from ai import summarize_analysis_result_with_ai  # AI summarizer with chunking


# # Predefined project and subproject lists
# WAVE_CITY_SUBPROJECTS = [
#     "ARANYAM VALLEY", "ARMONIA VILLA", "DREAM BAZAAR", "DREAM HOMES", "EDEN", "ELIGO", "EWS", "EWS_001_(410)",
#     "EXECUTIVE FLOORS", "FSI", "Generic", "Golf Range", "INSTITUTIONAL", "LIG", "LIG_001_(310)", "Mayfair Park",
#     "NEW PLOTS", "OLD PLOTS", "PRIME FLOORS", "SCO.", "SWAMANORATH", "VERIDIA", "VERIDIA-3", "VERIDIA-4",
#     "VERIDIA-5", "VERIDIA-6", "VERIDIA-7", "VILLAS", "WAVE FLOOR", "WAVE GALLERIA"
# ]

# WAVE_ESTATE_SUBPROJECTS = [
#     "COMM BOOTH", "HARMONY GREENS", "INSTITUTIONAL_WE", "PLOT-RES-IF", "PLOTS-COMM", "PLOTS-RES", "SCO",
#     "WAVE FLOOR 85", "WAVE FLOOR 99", "WAVE GARDEN", "WAVE GARDEN GH2-Ph-2"
# ]

# WMCC_SUBPROJECTS = [
#     "AMORE", "HSSC", "LIVORK", "TRUCIA"
# ]

# PROJECT_OPTIONS = ["WAVE CITY", "WAVE ESTATE", "WMCC", "SELECT ALL"]

# # Page config and styling
# st.set_page_config(page_title="LeadBot Analytics", layout="wide", initial_sidebar_state="expanded")

# # Title and subtitle
# st.title("🤖 Wave Group (CRM-Analytics chat)")
# st.markdown("*Welcome To Wave, How May I help you?*")

# # Clear chat button
# if st.button("🧹 Clear Chat"):
#     st.session_state.conversation = []
#     st.session_state.show_details = False
#     st.session_state.show_graph = False
#     st.session_state.last_query_idx = -1
#     if 'last_backend_result' in st.session_state:
#         del st.session_state.last_backend_result
#     if 'ai_summary_text' in st.session_state:
#         del st.session_state.ai_summary_text
#     if 'ai_graph_data' in st.session_state:
#         del st.session_state.ai_graph_data
#     if 'ai_details_data' in st.session_state:
#         del st.session_state.ai_details_data
#     st.experimental_rerun()

# st.markdown("---")

# # Load Salesforce data with caching
# @st.cache_data(show_spinner=True)
# def load_data():
#     return load_salesforce_data()

# leads_df, users_df, cases_df, events_df, opportunities_df, task_df, load_error = load_data()

# if load_error:
#     st.error(f"❌ Error loading Salesforce data: {load_error}")
#     st.stop()

# data_context = create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df)

# # Initialize session state variables if not present
# if 'conversation' not in st.session_state:
#     st.session_state.conversation = []
# if 'show_details' not in st.session_state:
#     st.session_state.show_details = False
# if 'show_graph' not in st.session_state:
#     st.session_state.show_graph = False
# if 'last_query_idx' not in st.session_state:
#     st.session_state.last_query_idx = -1


# def reset_flags():
#     st.session_state.show_details = False
#     st.session_state.show_graph = False


# def plot_graph(graph_data):
#     if not graph_data:
#         st.info("No graphical data available for this query.")
#         return
#     for field, counts in graph_data.items():
#         df = pd.DataFrame(list(counts.items()), columns=[field, 'Count'])
#         if df.empty:
#             st.info(f"No data to plot for {field}.")
#             continue
#         fig = px.bar(df, x=field, y='Count', title=f"Distribution of {field}")
#         st.plotly_chart(fig, use_container_width=True)


# def get_financial_year_dates(selection, custom_year=None):
#     try:
#         if selection == "Current FY":
#             return pd.Timestamp("2024-04-01", tz="UTC"), pd.Timestamp("2025-03-31 23:59:59", tz="UTC")
#         elif selection == "Last FY":
#             return pd.Timestamp("2023-04-01", tz="UTC"), pd.Timestamp("2024-03-31 23:59:59", tz="UTC")
#         elif selection == "Custom" and custom_year:
#             year_int = int(custom_year)
#             return pd.Timestamp(f"{year_int}-04-01", tz="UTC"), pd.Timestamp(f"{year_int+1}-03-31 23:59:59", tz="UTC")
#     except Exception:
#         return None, None


# def process_query(user_question):
#     reset_flags()

#     product_project_keywords = ["product", "project", "sale", "lead", "conversion", "funnel", "source", "geography"]
#     is_special_query = any(k in user_question.lower() for k in product_project_keywords)

#     # Show Filters toggle - default off
#     show_filters = st.checkbox("FILTER", value=False, key="show_filters_toggle")

#     filters = {}

#     if show_filters and is_special_query:
#         # User wants to apply custom filters, show UI
#         st.markdown("### Filters")
#         col1, col2, col3 = st.columns([1, 1, 1])

#         with col1:
#             financial_year = st.selectbox("Financial Year", ["Current FY", "Last FY", "Custom"], key="financial_year")
#             custom_year = None
#             if financial_year == "Custom":
#                 custom_year = st.text_input("Enter starting year (e.g., 2024)", key="custom_year")

#         with col2:
#             selected_project = st.selectbox("Select Project(s)", PROJECT_OPTIONS, index=3, key="selected_project")

#         with col3:
#             if selected_project == "WAVE CITY":
#                 subprojects = WAVE_CITY_SUBPROJECTS
#             elif selected_project == "WAVE ESTATE":
#                 subprojects = WAVE_ESTATE_SUBPROJECTS
#             elif selected_project == "WMCC":
#                 subprojects = WMCC_SUBPROJECTS
#             elif selected_project == "SELECT ALL":
#                 subprojects = WAVE_CITY_SUBPROJECTS + WAVE_ESTATE_SUBPROJECTS + WMCC_SUBPROJECTS
#             else:
#                 subprojects = []

#             selected_subprojects = st.multiselect(
#                 "Select Product(s)",
#                 options=["Select All"] + subprojects,
#                 default=["Select All"],
#                 key="selected_subprojects"
#             )

#         if selected_subprojects and "Select All" in selected_subprojects:
#             selected_subprojects = subprojects

#         financial_year_start, financial_year_end = get_financial_year_dates(financial_year, custom_year)

#         if financial_year_start and financial_year_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": financial_year_start.isoformat(), "$lte": financial_year_end.isoformat()}

#         if selected_project != "SELECT ALL":
#             filters["Project__c"] = selected_project

#         if selected_subprojects and len(selected_subprojects) > 0:
#             filters["Project_Category__c"] = selected_subprojects

#     else:
#         # FILTER toggle is OFF: Remove any project/product filters completely
#         # Keep only financial year filter for sanity
#         financial_year_start, financial_year_end = get_financial_year_dates("Current FY", None)
#         if financial_year_start and financial_year_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": financial_year_start.isoformat(), "$lte": financial_year_end.isoformat()}

#     try:
#         analysis_plan = query_watsonx_ai(user_question, data_context, leads_df, cases_df, events_df, users_df, opportunities_df, task_df)
#     except Exception as e:
#         st.error(f"Error querying WatsonX AI: {e}")
#         analysis_plan = {"analysis_type": "error", "explanation": "AI query failed."}

#     if "filters" not in analysis_plan or not isinstance(analysis_plan["filters"], dict):
#         analysis_plan["filters"] = {}

#     if not show_filters:
#         # Remove any project/product filters from AI plan forcibly
#         for key in ["Project__c", "Project_Category__c"]:
#             if key in analysis_plan["filters"]:
#                 del analysis_plan["filters"][key]

#     # Merge filters (financial year or UI selected) into AI filters
#     for key, val in filters.items():
#         analysis_plan["filters"][key] = val

#     if analysis_plan.get("analysis_type") == "error":
#         fallback_plan = parse_intent_fallback(user_question, "")
#         backend_result = execute_analysis(fallback_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)
#         ai_summary_text = f"AI processing error: {analysis_plan.get('explanation', '')}\nShowing fallback analysis results."
#         graph_data = backend_result.get("graph_data", {})
#         details_data = []  # or fallback details if you want
#     else:
#         backend_result = execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)

#         ai_summary_text, ai_structured_data = summarize_analysis_result_with_ai(
#             backend_result,
#             user_question,
#             WATSONX_URL,
#             WATSONX_PROJECT_ID,
#             WATSONX_MODEL_ID,
#             get_watsonx_token
#         )
#         graph_data = ai_structured_data.get("graph_data", {})
#         details_data = ai_structured_data.get("details", [])

#     # Store AI summary and structured data for reuse in UI
#     st.session_state.last_backend_result = backend_result
#     st.session_state.ai_summary_text = ai_summary_text
#     st.session_state.ai_graph_data = graph_data
#     st.session_state.ai_details_data = details_data

#     st.session_state.conversation.append({"role": "user", "content": user_question})
#     st.session_state.conversation.append({"role": "assistant", "content": ai_summary_text})

#     st.markdown(f"""<p style="margin-top:20px;"><b>AI Summary:</b> {ai_summary_text}</p>""", unsafe_allow_html=True)

#     if st.button("Show Graph"):
#         st.session_state.show_graph = True

#     if st.button("Show Details"):
#         st.session_state.show_details = True

#     if st.session_state.show_graph:
#         plot_graph(st.session_state.ai_graph_data)

#     if st.session_state.show_details:
#         if not st.session_state.ai_details_data:
#             st.info("No detailed data available for this query.")
#         else:
#             df = pd.DataFrame(st.session_state.ai_details_data)
#             st.dataframe(df)

#     st.session_state.last_query_idx += 1


# # User input box for queries
# user_question = st.text_input("Enter your query:", key="user_input")

# if user_question:
#     process_query(user_question)


#================================new code for the today=====================



import streamlit as st
import pandas as pd
import plotly.express as px

from config import (
    client_id,
    client_secret,
    username,
    password,
    login_url,
    WATSONX_URL,
    WATSONX_PROJECT_ID,
    WATSONX_MODEL_ID
)

from watsonx_utils import (
    create_data_context,
    query_watsonx_ai,
    get_watsonx_token
)
from salesforce_utils import load_salesforce_data
from analysis_engine import execute_analysis
from ai import summarize_analysis_result_with_ai  # AI summarizer with chunking

# Set Streamlit page config at very top
st.set_page_config(page_title="LeadBot Analytics", layout="wide", initial_sidebar_state="expanded")

# Known projects/products list lowercase
ALL_PROJECTS = set([
    "aranyam valley", "armonia villa", "dream bazaar", "dream homes", "eden", "eligo", "ews", "ews_001_(410)",
    "executive floors", "fsi", "generic", "golf range", "institutional", "lig", "lig_001_(310)", "mayfair park",
    "new plots", "old plots", "prime floors", "sco.", "swamanorath", "veridia", "veridia-3", "veridia-4",
    "veridia-5", "veridia-6", "veridia-7", "villas", "wave floor", "wave galleria",
    "comm booth", "harmony greens", "institutional_we", "plot-res-if", "plots-comm", "plots-res",
    "amore", "hssc", "livork", "trucia",
    "wave city", "wave estate", "wmcc"
])

st.title("🤖 Wave Group (CRM Analytics Chat)")
st.markdown("*Welcome To Wave, How May I help you?*")

if st.button("🧹 Clear Chat"):
    st.session_state.clear()
    

st.markdown("---")

@st.cache_data(show_spinner=True)
def load_data():
    return load_salesforce_data()

# Load Salesforce data once
leads_df, users_df, cases_df, events_df, opportunities_df, task_df, load_error = load_data()

if load_error:
    st.error(f"❌ Error loading Salesforce data: {load_error}")
    st.stop()

data_context = create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df)

# Initialize session state variables
for key in [
    "conversation", "last_backend_result", "ai_summary_text",
    "ai_graph_data", "ai_details_data", "project_filter"
]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "conversation" else []

def detect_projects_in_query(query: str):
    query_lower = query.lower()
    matched = [p for p in ALL_PROJECTS if p in query_lower]
    return matched

def filter_dataframes_by_projects(leads_df, cases_df, events_df, opportunities_df, task_df, projects):
    if not projects:
        return leads_df, cases_df, events_df, opportunities_df, task_df

    projects_lower = [p.lower() for p in projects]

    filtered_leads = leads_df
    if 'Project_Category__c' in leads_df.columns:
        filtered_leads = leads_df[
            leads_df['Project_Category__c'].str.lower().isin(projects_lower)
        ]

    filtered_opportunities = opportunities_df
    if 'Project_Category__c' in opportunities_df.columns:
        filtered_opportunities = opportunities_df[
            opportunities_df['Project_Category__c'].str.lower().isin(projects_lower)
        ]

    # No filtering for other dfs (cases, events, tasks) assumed

    return filtered_leads, cases_df, events_df, filtered_opportunities, task_df

def process_user_query(user_question: str):
    matched_projects = detect_projects_in_query(user_question)
    st.session_state.project_filter = matched_projects if matched_projects else None

    filtered_leads_df, filtered_cases_df, filtered_events_df, filtered_opportunities_df, filtered_task_df = filter_dataframes_by_projects(
        leads_df, cases_df, events_df, opportunities_df, task_df,
        st.session_state.project_filter
    )

    # Fallback to full data if filtered leads are empty
    if filtered_leads_df.empty:
        st.warning("Filtered data is empty. Showing results for all projects/products.")
        filtered_leads_df = leads_df
        filtered_cases_df = cases_df
        filtered_events_df = events_df
        filtered_opportunities_df = opportunities_df
        filtered_task_df = task_df

    # Append filter info to user question
    if st.session_state.project_filter:
        filter_desc = ", ".join(st.session_state.project_filter)
        user_question_enhanced = f"{user_question} (Filtered for projects/products: {filter_desc})"
    else:
        user_question_enhanced = user_question

    analysis_plan = query_watsonx_ai(
        user_question_enhanced,
        data_context,
        filtered_leads_df,
        filtered_cases_df,
        filtered_events_df,
        users_df,
        filtered_opportunities_df,
        filtered_task_df
    )

    backend_result = execute_analysis(
        analysis_plan,
        filtered_leads_df,
        users_df,
        filtered_cases_df,
        filtered_events_df,
        filtered_opportunities_df,
        filtered_task_df,
        user_question=user_question_enhanced
    )
    st.session_state.last_backend_result = backend_result

    if backend_result is None or (isinstance(backend_result, dict) and backend_result.get("type") == "error"):
        st.error("Could not generate analysis for the selected filters or query.")
        return

    summary_text, ai_data = summarize_analysis_result_with_ai(
        backend_result,
        user_question_enhanced,
        WATSONX_URL,
        WATSONX_PROJECT_ID,
        WATSONX_MODEL_ID,
        get_watsonx_token
    )

    st.session_state.ai_summary_text = summary_text
    st.session_state.ai_graph_data = ai_data.get("graph_data", {})
    st.session_state.ai_details_data = ai_data.get("details", {})

    st.markdown("### AI Summary")
    st.write(summary_text)

    if st.session_state.ai_details_data:
        st.markdown("### Details")
        details = st.session_state.ai_details_data
        if isinstance(details, dict):
            for table_name, table_rows in details.items():
                st.markdown(f"#### {table_name}")
                try:
                    df = pd.DataFrame(table_rows)
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"Error displaying table '{table_name}': {e}")
        elif isinstance(details, list):
            try:
                df = pd.DataFrame(details)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error displaying details table: {e}")
        else:
            st.info("No valid details data to display.")

    # Graph selection with radio buttons: show one graph at a time or none
    if st.session_state.ai_graph_data:
        details_tables = []
        if isinstance(st.session_state.ai_details_data, dict):
            details_tables = list(st.session_state.ai_details_data.items())
        elif isinstance(st.session_state.ai_details_data, list):
            details_tables = [("Table 1", st.session_state.ai_details_data)]
        else:
            details_tables = []

        graph_options = ["None"] + [f"Graph {i+1}: {name}" for i, (name, _) in enumerate(details_tables)]
        selected_graph = st.radio("Select graph to show", options=graph_options, index=0)

        if selected_graph != "None":
            idx = graph_options.index(selected_graph) - 1
            table_name, table_rows = details_tables[idx]
            st.markdown(f"### Graph for {table_name}")

            df = pd.DataFrame(table_rows)
            funnel_cols = [col for col in df.columns if col.lower() in ['stage', 'metric', 'label', 'step', 'name']]
            value_cols = [col for col in df.columns if col.lower() in ['value', 'count', 'amount', 'ratio']]

            if funnel_cols and value_cols:
                stage_col = funnel_cols[0]
                value_col = value_cols[0]
                fig = px.funnel(df, x=value_col, y=stage_col, title=f"Funnel Chart - {table_name}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    fig = px.bar(df, x=df.columns[0], y=numeric_cols[0], title=f"Bar Chart - {table_name}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric data found for graph.")

def main():
    user_input = st.text_input("Ask your question about leads, sales, projects, etc. (Total Lead = 30777)", key="user_input")
    if user_input:
        st.session_state.conversation.append({"role": "user", "content": user_input})
        process_user_query(user_input)

main()
