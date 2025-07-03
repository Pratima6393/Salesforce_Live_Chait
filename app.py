import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

from config import *
from watsonx_utils import (
    validate_watsonx_config,
    create_data_context,
    query_watsonx_ai,
    parse_intent_fallback,
    get_watsonx_token
)
from salesforce_utils import load_salesforce_data
from analysis_engine import execute_analysis, display_analysis_result
from ai import summarize_analysis_result_with_ai  # AI summarizer with chunking

# Predefined product lists per project
WAVE_CITY_PRODUCTS = [ 
    "ARANYAM VALLEY", "ARMONIA VILLA", "DREAM BAZAAR", "DREAM HOMES", "EDEN", "ELIGO", "EWS", "EWS_001_(410)",
    "EXECUTIVE FLOORS", "FSI", "Generic", "Golf Range", "INSTITUTIONAL", "LIG", "LIG_001_(310)", "Mayfair Park",
    "NEW PLOTS", "OLD PLOTS", "PRIME FLOORS", "SCO.", "SWAMANORATH", "VERIDIA", "VERIDIA-3", "VERIDIA-4",
    "VERIDIA-5", "VERIDIA-6", "VERIDIA-7", "VILLAS", "WAVE FLOOR", "WAVE GALLERIA"
]

WAVE_ESTATE_PRODUCTS = [ 
    "COMM BOOTH", "HARMONY GREENS", "INSTITUTIONAL_WE", "PLOT-RES-IF", "PLOTS-COMM", "PLOTS-RES", "SCO",
    "WAVE FLOOR 85", "WAVE FLOOR 99", "WAVE GARDEN", "WAVE GARDEN GH2-Ph-2"
]

WMCC_PRODUCTS = [ 
    "AMORE", "HSSC", "LIVORK", "TRUCIA"
]

PROJECT_TO_PRODUCTS = {
    "Wave City": set(WAVE_CITY_PRODUCTS),
    "Wave Estate": set(WAVE_ESTATE_PRODUCTS),
    "WMCC Sec 32": set(WMCC_PRODUCTS),
}

PROJECT_OPTIONS = ["WAVE CITY", "WAVE ESTATE", "WMCC", "SELECT ALL"]

# Page config
st.set_page_config(page_title="LeadBot Analytics", layout="wide", initial_sidebar_state="expanded")
st.title("🤖 Wave Group (CRM-BOT)")
st.markdown("Welcome To Wave, How May I help you?")

if st.button("🧹 Clear Chat"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()

st.markdown("---")

@st.cache_data(show_spinner=True)
def load_data():
    return load_salesforce_data()

leads_df, users_df, cases_df, events_df, opportunities_df, task_df, load_error = load_data()

if load_error:
    st.error(f"❌ Error loading Salesforce data: {load_error}")
    st.stop()

data_context = create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df)

for key in ['conversation', 'show_details', 'show_graph', 'last_query_idx']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'conversation' else False if 'show' in key else -1


def reset_flags():
    st.session_state.show_details = False
    st.session_state.show_graph = False


def plot_graph(graph_data):
    if not graph_data:
        st.info("No graphical data available.")
        return
    for field, counts in graph_data.items():
        df = pd.DataFrame(list(counts.items()), columns=[field, 'Count'])
        fig = px.bar(df, x=field, y='Count', title=f"Distribution of {field}")
        st.plotly_chart(fig, use_container_width=True)


def get_financial_year_dates(selection, custom_year=None):
    try:
        if selection == "Current FY":
            return pd.Timestamp("2024-04-01", tz="UTC"), pd.Timestamp("2025-03-31 23:59:59", tz="UTC")
        elif selection == "Last FY":
            return pd.Timestamp("2023-04-01", tz="UTC"), pd.Timestamp("2024-03-31 23:59:59", tz="UTC")
        elif selection == "Custom" and custom_year:
            year_int = int(custom_year)
            return pd.Timestamp(f"{year_int}-04-01", tz="UTC"), pd.Timestamp(f"{year_int+1}-03-31 23:59:59", tz="UTC")
    except:
        return None, None


def build_merged_project_product_table(graph_data):
    project_counts = graph_data.get("Project__c", {})
    product_counts = graph_data.get("Project_Category__c", {})

    rows = []
    sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)

    for proj_name, proj_count in sorted_projects:
        valid_products = {
            prod: cnt for prod, cnt in product_counts.items()
            if proj_name in PROJECT_TO_PRODUCTS and prod in PROJECT_TO_PRODUCTS[proj_name]
        }
        sorted_products = sorted(valid_products.items(), key=lambda x: x[1], reverse=True)

        first_product = True
        for prod_name, prod_count in sorted_products:
            if first_product:
                rows.append({
                    "Project": proj_name,
                    "Count": proj_count,
                    "Product": prod_name,
                    "Product Count": prod_count
                })
                first_product = False
            else:
                rows.append({
                    "Project": "",
                    "Count": "",
                    "Product": prod_name,
                    "Product Count": prod_count
                })

    return rows


def display_total_counts(df: pd.DataFrame):
    count_cols = [col for col in df.columns if "count" in col.lower()]
    if not count_cols:
        return
    totals = {}
    for col in count_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            totals[col] = df[col].sum()
    if totals:
        total_display = ", ".join(f"**{col}:** {val}" for col, val in totals.items())
        st.markdown(f"### Total Counts: {total_display}")


def process_query(user_question):
    reset_flags()

    product_project_keywords = ["product", "project", "sale", "lead", "conversion", "funnel", "source", "geography"]
    is_special_query = any(k in user_question.lower() for k in product_project_keywords)
    show_filters = st.checkbox("FILTER", value=False, key="show_filters_toggle")
    filters = {}

    if show_filters and is_special_query:
        st.markdown("### Filters")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            financial_year = st.selectbox("Financial Year", ["Current FY", "Last FY", "Custom"], key="financial_year")
            custom_year = st.text_input("Enter starting year (e.g., 2024)", key="custom_year") if financial_year == "Custom" else None
        with col2:
            selected_project = st.selectbox("Select Project(s)", PROJECT_OPTIONS, index=3, key="selected_project")
        with col3:
            subprojects = WAVE_CITY_PRODUCTS if selected_project == "WAVE CITY" else \
                          WAVE_ESTATE_PRODUCTS if selected_project == "WAVE ESTATE" else \
                          WMCC_PRODUCTS if selected_project == "WMCC" else \
                          WAVE_CITY_PRODUCTS + WAVE_ESTATE_PRODUCTS + WMCC_PRODUCTS
            selected_subprojects = st.multiselect("Select Product(s)", ["Select All"] + subprojects, default=["Select All"], key="selected_subprojects")
            if "Select All" in selected_subprojects:
                selected_subprojects = subprojects

        fy_start, fy_end = get_financial_year_dates(financial_year, custom_year)
        if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
            filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}
        if selected_project != "SELECT ALL":
            filters["Project__c"] = selected_project
        if selected_subprojects:
            filters["Project_Category__c"] = selected_subprojects
    else:
        fy_start, fy_end = get_financial_year_dates("Current FY")
        if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
            filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}

    try:
        analysis_plan = query_watsonx_ai(user_question, data_context, leads_df, cases_df, events_df, users_df, opportunities_df, task_df)
    except Exception as e:
        st.error(f"WatsonX AI error: {e}")
        return

    analysis_plan.setdefault("filters", {})

    if not show_filters:
        for key in ["Project__c", "Project_Category__c"]:
            analysis_plan["filters"].pop(key, None)

    analysis_plan["filters"].update(filters)

    backend_result = execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)
    ai_summary_text, ai_structured_data = summarize_analysis_result_with_ai(
        backend_result,
        user_question,
        WATSONX_URL,
        WATSONX_PROJECT_ID,
        WATSONX_MODEL_ID,
        get_watsonx_token
    )

    st.session_state.last_backend_result = backend_result
    st.session_state.ai_summary_text = ai_summary_text
    st.session_state.ai_graph_data = ai_structured_data.get("graph_data", {})
    st.session_state.ai_details_data = ai_structured_data.get("details", [])

    st.session_state.conversation.append({"role": "user", "content": user_question})
    st.session_state.conversation.append({"role": "assistant", "content": ai_summary_text})

    st.markdown(f"""<p style="margin-top:20px;"><b>AI Summary:</b> {ai_summary_text}</p>""", unsafe_allow_html=True)

    if st.button("Show Graph"):
        st.session_state.show_graph = True
    if st.button("Show Details"):
        st.session_state.show_details = True

    if st.session_state.show_graph:
        plot_graph(st.session_state.ai_graph_data)

    if st.session_state.show_details:
        if not st.session_state.ai_details_data:
            st.info("No detailed data available.")
        else:
            query_lower_words = set(user_question.lower().split())
            if "project" in query_lower_words and "product" in query_lower_words:
                merged_table = build_merged_project_product_table(st.session_state.ai_graph_data)
                df = pd.DataFrame(merged_table)
                st.subheader("📊 Project-wise Product Distribution")
                st.dataframe(df, use_container_width=True)
                display_total_counts(df)
            else:
                df = pd.DataFrame(st.session_state.ai_details_data)
                if df.empty or (df.isnull().all(axis=1).all()):
                    st.info("No detailed data available for this query.")
                    return
                st.dataframe(df, use_container_width=True)
                display_total_counts(df)


user_question = st.text_input("Enter your query:", key="user_input")

if user_question:
    process_query(user_question)

























































































# ---------------------------------------------------funnel-----------------------------------------------------








# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import json
# from datetime import datetime

# from config import *
# from watsonx_utils import (
#     validate_watsonx_config,
#     create_data_context,
#     query_watsonx_ai,
#     parse_intent_fallback,
#     get_watsonx_token
# )
# from salesforce_utils import load_salesforce_data
# from analysis_engine import execute_analysis, display_analysis_result
# from ai import summarize_analysis_result_with_ai

# # Predefined product lists per project
# WAVE_CITY_PRODUCTS = [ 
#     "ARANYAM VALLEY", "ARMONIA VILLA", "DREAM BAZAAR", "DREAM HOMES", "EDEN", "ELIGO", "EWS", "EWS_001_(410)",
#     "EXECUTIVE FLOORS", "FSI", "Generic", "Golf Range", "INSTITUTIONAL", "LIG", "LIG_001_(310)", "Mayfair Park",
#     "NEW PLOTS", "OLD PLOTS", "PRIME FLOORS", "SCO.", "SWAMANORATH", "VERIDIA", "VERIDIA-3", "VERIDIA-4",
#     "VERIDIA-5", "VERIDIA-6", "VERIDIA-7", "VILLAS", "WAVE FLOOR", "WAVE GALLERIA"
# ]

# WAVE_ESTATE_PRODUCTS = [ 
#     "COMM BOOTH", "HARMONY GREENS", "INSTITUTIONAL_WE", "PLOT-RES-IF", "PLOTS-COMM", "PLOTS-RES", "SCO",
#     "WAVE FLOOR 85", "WAVE FLOOR 99", "WAVE GARDEN", "WAVE GARDEN GH2-Ph-2"
# ]

# WMCC_PRODUCTS = [ 
#     "AMORE", "HSSC", "LIVORK", "TRUCIA"
# ]

# PROJECT_TO_PRODUCTS = {
#     "Wave City": set(WAVE_CITY_PRODUCTS),
#     "Wave Estate": set(WAVE_ESTATE_PRODUCTS),
#     "WMCC Sec 32": set(WMCC_PRODUCTS),
# }

# PROJECT_OPTIONS = ["WAVE CITY", "WAVE ESTATE", "WMCC", "SELECT ALL"]

# st.set_page_config(page_title="LeadBot Analytics", layout="wide", initial_sidebar_state="expanded")
# st.title("🤖 Wave Group (CRM-BOT)")
# st.markdown("Welcome To Wave, How May I help you?")

# if st.button("🧹 Clear Chat"):
#     for k in list(st.session_state.keys()):
#         del st.session_state[k]
#     st.experimental_rerun()

# st.markdown("---")

# @st.cache_data(show_spinner=True)
# def load_data():
#     return load_salesforce_data()

# leads_df, users_df, cases_df, events_df, opportunities_df, task_df, load_error = load_data()

# if load_error:
#     st.error(f"❌ Error loading Salesforce data: {load_error}")
#     st.stop()

# data_context = create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df)

# for key in ['conversation', 'show_details', 'show_graph', 'last_query_idx']:
#     if key not in st.session_state:
#         st.session_state[key] = [] if key == 'conversation' else False if 'show' in key else -1

# def reset_flags():
#     st.session_state.show_details = False
#     st.session_state.show_graph = False

# def plot_graph(graph_data):
#     if not graph_data:
#         st.info("No graphical data available.")
#         return
#     for field, counts in graph_data.items():
#         df = pd.DataFrame(list(counts.items()), columns=[field, 'Count'])
#         fig = px.bar(df, x=field, y='Count', title=f"Distribution of {field}")
#         st.plotly_chart(fig, use_container_width=True)

# def plot_funnel_chart(funnel_metrics):
#     if not funnel_metrics or not isinstance(funnel_metrics, list):
#         st.info("No funnel metrics data available for funnel chart.")
#         return
    
#     stages = [item.get("Stage", "") for item in funnel_metrics]
#     counts = [item.get("Count", 0) for item in funnel_metrics]

#     fig = go.Figure(go.Funnel(
#         y=stages,
#         x=counts,
#         textinfo="value+percent previous"
#     ))
#     fig.update_layout(title="Lead Conversion Funnel")
#     st.plotly_chart(fig, use_container_width=True)

# def plot_funnel_ratios_chart(funnel_ratios):
#     if not funnel_ratios or not isinstance(funnel_ratios, list):
#         st.info("No funnel ratios data available for ratio chart.")
#         return
    
#     ratios = [item.get("Ratio", "") for item in funnel_ratios]
#     values = [item.get("Value", 0) for item in funnel_ratios]

#     df = pd.DataFrame({"Ratio": ratios, "Value": values})

#     fig = px.bar(df, x="Ratio", y="Value", title="Funnel Conversion Ratios", text="Value")
#     fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
#     fig.update_layout(yaxis_title="Ratio", xaxis_title="Conversion Ratio", uniformtext_minsize=8, uniformtext_mode='hide')
#     st.plotly_chart(fig, use_container_width=True)

# def get_financial_year_dates(selection, custom_year=None):
#     try:
#         if selection == "Current FY":
#             return pd.Timestamp("2024-04-01", tz="UTC"), pd.Timestamp("2025-03-31 23:59:59", tz="UTC")
#         elif selection == "Last FY":
#             return pd.Timestamp("2023-04-01", tz="UTC"), pd.Timestamp("2024-03-31 23:59:59", tz="UTC")
#         elif selection == "Custom" and custom_year:
#             year_int = int(custom_year)
#             return pd.Timestamp(f"{year_int}-04-01", tz="UTC"), pd.Timestamp(f"{year_int+1}-03-31 23:59:59", tz="UTC")
#     except:
#         return None, None

# def build_merged_project_product_table(graph_data):
#     project_counts = graph_data.get("Project__c", {})
#     product_counts = graph_data.get("Project_Category__c", {})

#     rows = []
#     sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)

#     for proj_name, proj_count in sorted_projects:
#         valid_products = {
#             prod: cnt for prod, cnt in product_counts.items()
#             if proj_name in PROJECT_TO_PRODUCTS and prod in PROJECT_TO_PRODUCTS[proj_name]
#         }
#         sorted_products = sorted(valid_products.items(), key=lambda x: x[1], reverse=True)

#         first_product = True
#         for prod_name, prod_count in sorted_products:
#             if first_product:
#                 rows.append({
#                     "Project": proj_name,
#                     "Count": proj_count,
#                     "Product": prod_name,
#                     "Product Count": prod_count
#                 })
#                 first_product = False
#             else:
#                 rows.append({
#                     "Project": "",
#                     "Count": "",
#                     "Product": prod_name,
#                     "Product Count": prod_count
#                 })

#     return rows

# def display_total_counts(df: pd.DataFrame):
#     count_cols = [col for col in df.columns if "count" in col.lower()]
#     if not count_cols:
#         return
#     totals = {}
#     for col in count_cols:
#         if pd.api.types.is_numeric_dtype(df[col]):
#             totals[col] = df[col].sum()
#     if totals:
#         total_display = ", ".join(f"**{col}:** {val}" for col, val in totals.items())
#         st.markdown(f"### Total Counts: {total_display}")

# def process_query(user_question):
#     reset_flags()

#     product_project_keywords = ["product", "project", "sale", "lead", "conversion", "funnel", "source", "geography"]
#     is_special_query = any(k in user_question.lower() for k in product_project_keywords)
#     show_filters = st.checkbox("FILTER", value=False, key="show_filters_toggle")
#     filters = {}

#     if show_filters and is_special_query:
#         st.markdown("### Filters")
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col1:
#             financial_year = st.selectbox("Financial Year", ["Current FY", "Last FY", "Custom"], key="financial_year")
#             custom_year = st.text_input("Enter starting year (e.g., 2024)", key="custom_year") if financial_year == "Custom" else None
#         with col2:
#             selected_project = st.selectbox("Select Project(s)", PROJECT_OPTIONS, index=3, key="selected_project")
#         with col3:
#             subprojects = WAVE_CITY_PRODUCTS if selected_project == "WAVE CITY" else \
#                           WAVE_ESTATE_PRODUCTS if selected_project == "WAVE ESTATE" else \
#                           WMCC_PRODUCTS if selected_project == "WMCC" else \
#                           WAVE_CITY_PRODUCTS + WAVE_ESTATE_PRODUCTS + WMCC_PRODUCTS
#             selected_subprojects = st.multiselect("Select Product(s)", ["Select All"] + subprojects, default=["Select All"], key="selected_subprojects")
#             if "Select All" in selected_subprojects:
#                 selected_subprojects = subprojects

#         fy_start, fy_end = get_financial_year_dates(financial_year, custom_year)
#         if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}
#         if selected_project != "SELECT ALL":
#             filters["Project__c"] = selected_project
#         if selected_subprojects:
#             filters["Project_Category__c"] = selected_subprojects
#     else:
#         fy_start, fy_end = get_financial_year_dates("Current FY")
#         if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}

#     try:
#         analysis_plan = query_watsonx_ai(user_question, data_context, leads_df, cases_df, events_df, users_df, opportunities_df, task_df)
#     except Exception as e:
#         st.error(f"WatsonX AI error: {e}")
#         return

#     analysis_plan.setdefault("filters", {})

#     if not show_filters:
#         for key in ["Project__c", "Project_Category__c"]:
#             analysis_plan["filters"].pop(key, None)

#     analysis_plan["filters"].update(filters)

#     backend_result = execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)
#     ai_summary_text, ai_structured_data = summarize_analysis_result_with_ai(
#         backend_result,
#         user_question,
#         WATSONX_URL,
#         WATSONX_PROJECT_ID,
#         WATSONX_MODEL_ID,
#         get_watsonx_token
#     )

#     st.session_state.last_backend_result = backend_result
#     st.session_state.ai_summary_text = ai_summary_text
#     st.session_state.ai_graph_data = ai_structured_data.get("graph_data", {})
#     st.session_state.ai_details_data = ai_structured_data.get("details", [])
#     st.session_state.ai_funnel_metrics = ai_structured_data.get("funnel_metrics", None)
#     st.session_state.ai_funnel_ratios = ai_structured_data.get("funnel_ratios", None)

#     st.session_state.conversation.append({"role": "user", "content": user_question})
#     st.session_state.conversation.append({"role": "assistant", "content": ai_summary_text})

#     st.markdown(f"""<p style="margin-top:20px;"><b>AI Summary:</b> {ai_summary_text}</p>""", unsafe_allow_html=True)

#     if st.button("Show Graph"):
#         st.session_state.show_graph = True
#     if st.button("Show Details"):
#         st.session_state.show_details = True

#     query_lower = user_question.lower()

#     if st.session_state.show_graph:
#         if "funnel" in query_lower:
#             if st.session_state.ai_funnel_metrics:
#                 plot_funnel_chart(st.session_state.ai_funnel_metrics)
#             else:
#                 st.info("No funnel metrics data available to plot funnel chart.")
#             if st.session_state.ai_funnel_ratios:
#                 plot_funnel_ratios_chart(st.session_state.ai_funnel_ratios)
#             else:
#                 st.info("No funnel ratios data available to plot ratio chart.")
#         else:
#             plot_graph(st.session_state.ai_graph_data)

#     if st.session_state.show_details:
#         if "funnel" in query_lower:
#             if st.session_state.ai_funnel_metrics:
#                 st.subheader("Funnel Metrics Table")
#                 st.dataframe(pd.DataFrame(st.session_state.ai_funnel_metrics), use_container_width=True)
#             else:
#                 st.info("No Funnel Metrics data available.")

#             if st.session_state.ai_funnel_ratios:
#                 st.subheader("Funnel Ratios Table")
#                 st.dataframe(pd.DataFrame(st.session_state.ai_funnel_ratios), use_container_width=True)
#             else:
#                 st.info("No Funnel Ratios data available.")
#         else:
#             if not st.session_state.ai_details_data:
#                 st.info("No detailed data available.")
#             else:
#                 query_lower_words = set(user_question.lower().split())
#                 if "project" in query_lower_words and "product" in query_lower_words:
#                     merged_table = build_merged_project_product_table(st.session_state.ai_graph_data)
#                     df = pd.DataFrame(merged_table)
#                     st.subheader("📊 Project-wise Product Distribution")
#                     st.dataframe(df, use_container_width=True)
#                     display_total_counts(df)
#                 else:
#                     df = pd.DataFrame(st.session_state.ai_details_data)
#                     if df.empty or (df.isnull().all(axis=1).all()):
#                         st.info("No detailed data available for this query.")
#                         return
#                     st.dataframe(df, use_container_width=True)
#                     display_total_counts(df)

# user_question = st.text_input("Enter your query:", key="user_input")

# if user_question:
#     process_query(user_question)






















































































# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import json
# from datetime import datetime

# from config import *
# from watsonx_utils import (
#     validate_watsonx_config,
#     create_data_context,
#     query_watsonx_ai,
#     parse_intent_fallback,
#     get_watsonx_token
# )
# from salesforce_utils import load_salesforce_data
# from analysis_engine import execute_analysis, display_analysis_result
# from ai import summarize_analysis_result_with_ai

# # Predefined product lists per project
# WAVE_CITY_PRODUCTS = [ 
#     "ARANYAM VALLEY", "ARMONIA VILLA", "DREAM BAZAAR", "DREAM HOMES", "EDEN", "ELIGO", "EWS", "EWS_001_(410)",
#     "EXECUTIVE FLOORS", "FSI", "Generic", "Golf Range", "INSTITUTIONAL", "LIG", "LIG_001_(310)", "Mayfair Park",
#     "NEW PLOTS", "OLD PLOTS", "PRIME FLOORS", "SCO.", "SWAMANORATH", "VERIDIA", "VERIDIA-3", "VERIDIA-4",
#     "VERIDIA-5", "VERIDIA-6", "VERIDIA-7", "VILLAS", "WAVE FLOOR", "WAVE GALLERIA"
# ]

# WAVE_ESTATE_PRODUCTS = [ 
#     "COMM BOOTH", "HARMONY GREENS", "INSTITUTIONAL_WE", "PLOT-RES-IF", "PLOTS-COMM", "PLOTS-RES", "SCO",
#     "WAVE FLOOR 85", "WAVE FLOOR 99", "WAVE GARDEN", "WAVE GARDEN GH2-Ph-2"
# ]

# WMCC_PRODUCTS = [ 
#     "AMORE", "HSSC", "LIVORK", "TRUCIA"
# ]

# PROJECT_TO_PRODUCTS = {
#     "Wave City": set(WAVE_CITY_PRODUCTS),
#     "Wave Estate": set(WAVE_ESTATE_PRODUCTS),
#     "WMCC Sec 32": set(WMCC_PRODUCTS),
# }

# PROJECT_OPTIONS = ["WAVE CITY", "WAVE ESTATE", "WMCC", "SELECT ALL"]

# st.set_page_config(page_title="LeadBot Analytics", layout="wide", initial_sidebar_state="expanded")
# st.title("🤖 Wave Group (CRM-BOT)")
# st.markdown("Welcome To Wave, How May I help you?")

# if st.button("🧹 Clear Chat"):
#     for k in list(st.session_state.keys()):
#         del st.session_state[k]
#     st.experimental_rerun()

# st.markdown("---")

# @st.cache_data(show_spinner=True)
# def load_data():
#     return load_salesforce_data()

# leads_df, users_df, cases_df, events_df, opportunities_df, task_df, load_error = load_data()

# if load_error:
#     st.error(f"❌ Error loading Salesforce data: {load_error}")
#     st.stop()

# data_context = create_data_context(leads_df, users_df, cases_df, events_df, opportunities_df, task_df)

# for key in ['conversation', 'show_details', 'show_graph', 'last_query_idx']:
#     if key not in st.session_state:
#         st.session_state[key] = [] if key == 'conversation' else False if 'show' in key else -1

# def reset_flags():
#     st.session_state.show_details = False
#     st.session_state.show_graph = False

# def plot_graph(graph_data):
#     if not graph_data:
#         st.info("No graphical data available.")
#         return
#     for field, counts in graph_data.items():
#         df = pd.DataFrame(list(counts.items()), columns=[field, 'Count'])
#         fig = px.bar(df, x=field, y='Count', title=f"Distribution of {field}")
#         st.plotly_chart(fig, use_container_width=True)

# def plot_funnel_chart(funnel_metrics):
#     if not funnel_metrics or not isinstance(funnel_metrics, list):
#         st.info("No funnel metrics data available for funnel chart.")
#         return
    
#     stages = [item.get("Stage", "") for item in funnel_metrics]
#     counts = [item.get("Count", 0) for item in funnel_metrics]

#     fig = go.Figure(go.Funnel(
#         y=stages,
#         x=counts,
#         textinfo="value+percent previous"
#     ))
#     fig.update_layout(title="Lead Conversion Funnel")
#     st.plotly_chart(fig, use_container_width=True)

# def plot_funnel_ratios_chart(funnel_ratios):
#     if not funnel_ratios or not isinstance(funnel_ratios, list):
#         st.info("No funnel ratios data available for ratio chart.")
#         return

#     ratios = [item.get("Ratio", "") for item in funnel_ratios]
#     values = [item.get("Value", 0) for item in funnel_ratios]

#     fig = go.Figure(go.Funnel(
#         y=ratios,
#         x=values,
#         textinfo="value+percent previous"
#     ))
#     fig.update_layout(title="Funnel Conversion Ratios")
#     st.plotly_chart(fig, use_container_width=True)

# def get_financial_year_dates(selection):
#     try:
#         if selection == "Current FY":
#             return pd.Timestamp("2024-04-01", tz="UTC"), pd.Timestamp("2025-03-31 23:59:59", tz="UTC")
#         elif selection == "Last FY":
#             return pd.Timestamp("2023-04-01", tz="UTC"), pd.Timestamp("2024-03-31 23:59:59", tz="UTC")
#         else:
#             return None, None
#     except:
#         return None, None

# def build_merged_project_product_table(graph_data):
#     project_counts = graph_data.get("Project__c", {})
#     product_counts = graph_data.get("Project_Category__c", {})

#     rows = []
#     sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)

#     for proj_name, proj_count in sorted_projects:
#         valid_products = {
#             prod: cnt for prod, cnt in product_counts.items()
#             if proj_name in PROJECT_TO_PRODUCTS and prod in PROJECT_TO_PRODUCTS[proj_name]
#         }
#         sorted_products = sorted(valid_products.items(), key=lambda x: x[1], reverse=True)

#         first_product = True
#         for prod_name, prod_count in sorted_products:
#             if first_product:
#                 rows.append({
#                     "Project": proj_name,
#                     "Count": proj_count,
#                     "Product": prod_name,
#                     "Product Count": prod_count
#                 })
#                 first_product = False
#             else:
#                 rows.append({
#                     "Project": "",
#                     "Count": "",
#                     "Product": prod_name,
#                     "Product Count": prod_count
#                 })

#     return rows

# def display_total_counts(df: pd.DataFrame):
#     count_cols = [col for col in df.columns if "count" in col.lower()]
#     if not count_cols:
#         return
#     totals = {}
#     for col in count_cols:
#         if pd.api.types.is_numeric_dtype(df[col]):
#             totals[col] = df[col].sum()
#     if totals:
#         total_display = ", ".join(f"**{col}:** {val}" for col, val in totals.items())
#         st.markdown(f"### Total Counts: {total_display}")

# def process_query(user_question):
#     reset_flags()

#     product_project_keywords = ["product", "project", "sale", "lead", "conversion", "funnel", "source", "geography"]
#     is_special_query = any(k in user_question.lower() for k in product_project_keywords)
#     show_filters = st.checkbox("FILTER", value=False, key="show_filters_toggle")
#     filters = {}

#     if show_filters and is_special_query:
#         st.markdown("### Filters")
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col1:
#             financial_year = st.selectbox("Financial Year", ["Current FY", "Last FY"], key="financial_year")

#         with col2:
#             selected_project = st.selectbox("Select Project(s)", PROJECT_OPTIONS, index=3, key="selected_project")
#         with col3:
#             subprojects = WAVE_CITY_PRODUCTS if selected_project == "WAVE CITY" else \
#                           WAVE_ESTATE_PRODUCTS if selected_project == "WAVE ESTATE" else \
#                           WMCC_PRODUCTS if selected_project == "WMCC" else \
#                           WAVE_CITY_PRODUCTS + WAVE_ESTATE_PRODUCTS + WMCC_PRODUCTS
#             selected_subprojects = st.multiselect("Select Product(s)", ["Select All"] + subprojects, default=["Select All"], key="selected_subprojects")
#             if "Select All" in selected_subprojects:
#                 selected_subprojects = subprojects

#         fy_start, fy_end = get_financial_year_dates(financial_year)
#         if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}
#         if selected_project != "SELECT ALL":
#             filters["Project__c"] = selected_project
#         if selected_subprojects:
#             filters["Project_Category__c"] = selected_subprojects
#     else:
#         fy_start, fy_end = get_financial_year_dates("Current FY")
#         if fy_start and fy_end and 'CreatedDate' in leads_df.columns:
#             filters["CreatedDate"] = {"$gte": fy_start.isoformat(), "$lte": fy_end.isoformat()}

#     try:
#         analysis_plan = query_watsonx_ai(user_question, data_context, leads_df, cases_df, events_df, users_df, opportunities_df, task_df)
#     except Exception as e:
#         st.error(f"WatsonX AI error: {e}")
#         return

#     analysis_plan.setdefault("filters", {})

#     if not show_filters:
#         for key in ["Project__c", "Project_Category__c"]:
#             analysis_plan["filters"].pop(key, None)

#     analysis_plan["filters"].update(filters)

#     backend_result = execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)
#     ai_summary_text, ai_structured_data = summarize_analysis_result_with_ai(
#         backend_result,
#         user_question,
#         WATSONX_URL,
#         WATSONX_PROJECT_ID,
#         WATSONX_MODEL_ID,
#         get_watsonx_token
#     )

#     st.session_state.last_backend_result = backend_result
#     st.session_state.ai_summary_text = ai_summary_text
#     st.session_state.ai_graph_data = ai_structured_data.get("graph_data", {})
#     st.session_state.ai_details_data = ai_structured_data.get("details", [])
#     st.session_state.ai_funnel_metrics = ai_structured_data.get("funnel_metrics", None)
#     st.session_state.ai_funnel_ratios = ai_structured_data.get("funnel_ratios", None)

#     st.session_state.conversation.append({"role": "user", "content": user_question})
#     st.session_state.conversation.append({"role": "assistant", "content": ai_summary_text})

#     st.markdown(f"""<p style="margin-top:20px;"><b>AI Summary:</b> {ai_summary_text}</p>""", unsafe_allow_html=True)

#     if st.button("Show Graph"):
#         st.session_state.show_graph = True
#     if st.button("Show Details"):
#         st.session_state.show_details = True

#     query_lower = user_question.lower()

#     if st.session_state.show_graph:
#         if "funnel" in query_lower:
#             if st.session_state.ai_funnel_metrics:
#                 plot_funnel_chart(st.session_state.ai_funnel_metrics)
#             else:
#                 st.info("No funnel metrics data available to plot funnel chart.")
#             if st.session_state.ai_funnel_ratios:
#                 plot_funnel_ratios_chart(st.session_state.ai_funnel_ratios)
#             else:
#                 st.info("No funnel ratios data available to plot ratio chart.")
#         else:
#             plot_graph(st.session_state.ai_graph_data)

#     if st.session_state.show_details:
#         if "funnel" in query_lower:
#             if st.session_state.ai_funnel_metrics:
#                 st.subheader("Funnel Metrics Table")
#                 st.dataframe(pd.DataFrame(st.session_state.ai_funnel_metrics), use_container_width=True)
#             else:
#                 st.info("No Funnel Metrics data available.")

#             if st.session_state.ai_funnel_ratios:
#                 st.subheader("Funnel Ratios Table")
#                 st.dataframe(pd.DataFrame(st.session_state.ai_funnel_ratios), use_container_width=True)
#             else:
#                 st.info("No Funnel Ratios data available.")
#         else:
#             if not st.session_state.ai_details_data:
#                 st.info("No detailed data available.")
#             else:
#                 query_lower_words = set(user_question.lower().split())
#                 if "project" in query_lower_words and "product" in query_lower_words:
#                     merged_table = build_merged_project_product_table(st.session_state.ai_graph_data)
#                     df = pd.DataFrame(merged_table)
#                     st.subheader("📊 Project-wise Product Distribution")
#                     st.dataframe(df, use_container_width=True)
#                     display_total_counts(df)
#                 else:
#                     df = pd.DataFrame(st.session_state.ai_details_data)
#                     if df.empty or (df.isnull().all(axis=1).all()):
#                         st.info("No detailed data available for this query.")
#                         return
#                     st.dataframe(df, use_container_width=True)
#                     display_total_counts(df)

# user_question = st.text_input("Enter your query:", key="user_input")

# if user_question:
#     process_query(user_question)
