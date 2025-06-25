
#================================new code for the today=====================
import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio

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
