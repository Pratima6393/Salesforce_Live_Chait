
#===================================new code for the funnel graph===============
import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px
import plotly.graph_objects as go
from config import logger, FIELD_TYPES, FIELD_DISPLAY_NAMES
from pytz import timezone

def execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question=""):
    """
    Execute the analysis based on the provided plan and dataframes.
    """
    try:
        # Extract analysis parameters
        analysis_type = analysis_plan.get("analysis_type", "filter")
        object_type = analysis_plan.get("object_type", "lead")
        fields = analysis_plan.get("fields", [])
        if "field" in analysis_plan and analysis_plan["field"]:
            if analysis_plan["field"] not in fields:
                fields.append(analysis_plan["field"])
        filters = analysis_plan.get("filters", {})
        selected_quarter = analysis_plan.get("quarter", None)

        logger.info(f"Executing analysis for query '{user_question}': {analysis_plan}")

        # Select the appropriate dataframe based on object_type
        if object_type == "lead":
            df = leads_df
        elif object_type == "case":
            df = cases_df
        elif object_type == "event":
            df = events_df
        elif object_type == "opportunity":
            df = opportunities_df
        elif object_type == "task":
            df = task_df
        else:
            logger.error(f"Unsupported object_type: {object_type}")
            return {"type": "error", "message": f"Unsupported object type: {object_type}"}

        if df.empty:
            logger.error(f"No {object_type} data available")
            return {"type": "error", "message": f"No {object_type} data available"}
        
        #=================================new code for the lead_versus_opportunity=========
        # Validate fields for opportunity_vs_lead analysis
        if analysis_type in ["opportunity_vs_lead", "opportunity_vs_lead_percentage"]:
            required_fields = ["Lead_Converted__c", "Id"]
            missing_fields = [f for f in required_fields if f not in df.columns]
            if missing_fields:
                logger.error(f"Missing fields for {analysis_type}: {missing_fields}")
                return {"type": "error", "message": f"Missing fields: {missing_fields}"}
        #=================================end for the the versus_opportunity==============

        if analysis_type in ["distribution", "top", "percentage", "quarterly_distribution", "source_wise_funnel", "conversion_funnel"] and not fields:
            fields = list(filters.keys()) if filters else []
            if not fields:
                logger.error(f"No fields specified for {analysis_type} analysis")
                return {"type": "error", "message": f"No fields specified for {analysis_type} analysis"}

        # Detect specific query types
        product_keywords = ["product sale", "product split", "sale"]
        sales_keywords = ["sale", "sales"]
        is_product_related = any(keyword in user_question.lower() for keyword in product_keywords)
        is_sales_related = any(keyword in user_question.lower() for keyword in sales_keywords)
        is_disqualification_reason = "disqualification reason" in user_question.lower()

        # Adjust fields for product-related and sales-related queries
        if is_product_related and object_type == "lead":
            logger.info(f"Detected product-related question: '{user_question}'. Using Project_Category__c and Status.")
            required_fields = ["Project_Category__c", "Status"]
            missing_fields = [f for f in required_fields if f not in df.columns]
            if missing_fields:
                logger.error(f"Missing fields for product analysis: {missing_fields}")
                return {"type": "error", "message": f"Missing fields for product analysis: {missing_fields}"}
            if "Project_Category__c" not in fields:
                fields.append("Project_Category__c")
            if "Status" not in fields:
                fields.append("Status")
            if analysis_type not in ["source_wise_funnel", "distribution", "quarterly_distribution"]:
                analysis_type = "distribution"
                analysis_plan["analysis_type"] = "distribution"
            analysis_plan["fields"] = fields

        if is_sales_related and object_type == "lead":
            logger.info(f"Detected sales-related question: '{user_question}'. Including Lead_Converted__c.")
            if "Lead_Converted__c" not in df.columns:
                logger.error("Lead_Converted__c column not found")
                return {"type": "error", "message": "Lead_Converted__c column not found"}
            if "Lead_Converted__c" not in fields:
                fields.append("Lead_Converted__c")
            analysis_plan["fields"] = fields

        # Copy the dataframe to avoid modifying the original
        filtered_df = df.copy()

        # Parse CreatedDate if present
        if 'CreatedDate' in filtered_df.columns:
            logger.info(f"Raw CreatedDate sample (first 5):\n{filtered_df['CreatedDate'].head().to_string()}")
            logger.info(f"Raw CreatedDate dtype: {filtered_df['CreatedDate'].dtype}")
            try:
                def parse_date(date_str):
                    if pd.isna(date_str):
                        return pd.NaT
                    try:
                        return pd.to_datetime(date_str, utc=True, errors='coerce')
                    except:
                        pass
                    try:
                        parsed_date = pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S', errors='coerce')
                        if pd.notna(parsed_date):
                            ist = timezone('Asia/Kolkata')
                            parsed_date = ist.localize(parsed_date).astimezone(timezone('UTC'))
                        return parsed_date
                    except:
                        pass
                    try:
                        parsed_date = pd.to_datetime(date_str, format='%m/%d/%Y', errors='coerce')
                        if pd.notna(parsed_date):
                            ist = timezone('Asia/Kolkata')
                            parsed_date = ist.localize(parsed_date).astimezone(timezone('UTC'))
                        return parsed_date
                    except:
                        pass
                    try:
                        parsed_date = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
                        if pd.notna(parsed_date):
                            ist = timezone('Asia/Kolkata')
                            parsed_date = ist.localize(parsed_date).astimezone(timezone('UTC'))
                        return parsed_date
                    except:
                        return pd.NaT

                filtered_df['CreatedDate'] = filtered_df['CreatedDate'].apply(parse_date)
                invalid_dates = filtered_df[filtered_df['CreatedDate'].isna()]
                if not invalid_dates.empty:
                    logger.warning(f"Found {len(invalid_dates)} rows with invalid CreatedDate values:\n{invalid_dates['CreatedDate'].head().to_string()}")
                filtered_df = filtered_df[filtered_df['CreatedDate'].notna()]
                if filtered_df.empty:
                    logger.error("No valid CreatedDate entries after conversion")
                    return {"type": "error", "message": "No valid CreatedDate entries found in the data"}
                min_date = filtered_df['CreatedDate'].min()
                max_date = filtered_df['CreatedDate'].max()
                logger.info(f"Date range in dataset after conversion (UTC): {min_date} to {max_date}")
            except Exception as e:
                logger.error(f"Error while converting CreatedDate: {str(e)}")
                return {"type": "error", "message": f"Error while converting CreatedDate: {str(e)}"}

        # Apply filters
        for field, value in filters.items():
            if field not in filtered_df.columns:
                logger.error(f"Filter field {field} not in columns: {list(df.columns)}")
                return {"type": "error", "message": f"Field {field} not found"}
            if isinstance(value, str):
                if field in ["Status", "Rating", "Customer_Feedback__c", "LeadSource", "Lead_Source_Sub_Category__c", "Appointment_Status__c", "StageName"]:
                    filtered_df = filtered_df[filtered_df[field] == value]
                else:
                    filtered_df = filtered_df[filtered_df[field].str.contains(value, case=False, na=False)]
            elif isinstance(value, list):
                filtered_df = filtered_df[filtered_df[field].isin(value) & filtered_df[field].notna()]
            elif isinstance(value, dict):
                if field in FIELD_TYPES and FIELD_TYPES[field] == 'datetime':
                    if "$gte" in value:
                        gte_value = pd.to_datetime(value["$gte"], utc=True)
                        filtered_df = filtered_df[filtered_df[field] >= gte_value]
                    if "$lte" in value:
                        lte_value = pd.to_datetime(value["$lte"], utc=True)
                        filtered_df = filtered_df[filtered_df[field] <= lte_value]
                elif "$in" in value:
                    filtered_df = filtered_df[filtered_df[field].isin(value["$in"]) & filtered_df[field].notna()]
                elif "$ne" in value:
                    filtered_df = filtered_df[filtered_df[field] != value["$ne"] if value["$ne"] is not None else filtered_df[field].notna()]
                else:
                    logger.error(f"Unsupported dict filter on {field}: {value}")
                    return {"type": "error", "message": f"Unsupported dict filter on {field}"}
            elif isinstance(value, bool):
                filtered_df = filtered_df[filtered_df[field] == value]
            else:
                filtered_df = filtered_df[filtered_df[field] == value]
            logger.info(f"After filter on {field}: {filtered_df.shape}")

        # Define quarters for 2024-25 financial year
        quarters = {
            "Q1 2024-25": {"start": pd.to_datetime("2024-04-01T00:00:00Z", utc=True), "end": pd.to_datetime("2024-06-30T23:59:59Z", utc=True)},
            "Q2 2024-25": {"start": pd.to_datetime("2024-07-01T00:00:00Z", utc=True), "end": pd.to_datetime("2024-09-30T23:59:59Z", utc=True)},
            "Q3 2024-25": {"start": pd.to_datetime("2024-10-01T00:00:00Z", utc=True), "end": pd.to_datetime("2024-12-31T23:59:59Z", utc=True)},
            "Q4 2024-25": {"start": pd.to_datetime("2025-01-01T00:00:00Z", utc=True), "end": pd.to_datetime("2025-03-31T23:59:59Z", utc=True)},
        }

        # Apply quarter filter if specified
        if selected_quarter and 'CreatedDate' in filtered_df.columns:
            quarter = quarters.get(selected_quarter)
            if not quarter:
                logger.error(f"Invalid quarter specified: {selected_quarter}")
                return {"type": "error", "message": f"Invalid quarter specified: {selected_quarter}"}
            filtered_df['CreatedDate'] = filtered_df['CreatedDate'].dt.tz_convert('UTC')
            logger.info(f"Filtering for {selected_quarter}: {quarter['start']} to {quarter['end']}")
            logger.info(f"Sample CreatedDate before quarter filter (first 5, UTC):\n{filtered_df['CreatedDate'].head().to_string()}")
            filtered_df = filtered_df[
                (filtered_df['CreatedDate'] >= quarter["start"]) &
                (filtered_df['CreatedDate'] <= quarter["end"])
            ]
            logger.info(f"Records after applying quarter filter {selected_quarter}: {len(filtered_df)} rows")
            if not filtered_df.empty:
                logger.info(f"Sample CreatedDate after quarter filter (first 5, UTC):\n{filtered_df['CreatedDate'].head().to_string()}")
            else:
                logger.warning(f"No records found for {selected_quarter}")

        logger.info(f"Final filtered {object_type} DataFrame shape: {filtered_df.shape}")
        if filtered_df.empty:
            return {"type": "info", "message": f"No {object_type} records found matching the criteria for {selected_quarter if selected_quarter else 'the specified period'}"}

        # Prepare graph_data for all analysis types
        graph_data = {}
        graph_fields = fields + list(filters.keys())
        valid_graph_fields = [f for f in graph_fields if f in filtered_df.columns]
        for field in valid_graph_fields:
            if filtered_df[field].dtype in ['object', 'bool', 'category']:
                counts = filtered_df[field].dropna().value_counts().to_dict()
                graph_data[field] = {str(k): v for k, v in counts.items()}
                logger.info(f"Graph data for {field}: {graph_data[field]}")

        # Handle different analysis types
        
        if analysis_type == "opportunity_vs_lead":
            if object_type == "lead":
                # Calculate total leads before applying filters
                total_leads = len(df)  # Use the unfiltered DataFrame
                # Apply filters (including quarter) for opportunities
                filtered_df = df.copy()
                for field, value in filters.items():
                    if field not in filtered_df.columns:
                        return {"type": "error", "message": f"Field {field} not found"}
                    if isinstance(value, str):
                        filtered_df = filtered_df[filtered_df[field] == value]
                    elif isinstance(value, dict):
                        if "$in" in value:
                            filtered_df = filtered_df[filtered_df[field].isin(value["$in"]) & filtered_df[field].notna()]
                        elif "$ne" in value:
                            filtered_df = filtered_df[filtered_df[field] != value["$ne"]]
                    elif isinstance(value, bool):
                        filtered_df = filtered_df[filtered_df[field] == value]
                if selected_quarter and 'CreatedDate' in filtered_df.columns:
                    quarter = quarters.get(selected_quarter)
                    filtered_df['CreatedDate'] = filtered_df['CreatedDate'].dt.tz_convert('UTC')
                    filtered_df = filtered_df[
                        (filtered_df['CreatedDate'] >= quarter["start"]) &
                        (filtered_df['CreatedDate'] <= quarter["end"])
                    ]
                opportunities = len(filtered_df[filtered_df["Lead_Converted__c"] == True])
                data = [
                    {"Category": "Total Leads", "Count": total_leads},
                    {"Category": "Opportunities", "Count": opportunities}
                ]
                graph_data["Opportunity vs Lead"] = {
                    "Total Leads": total_leads,
                    "Opportunities": opportunities
                }
                return {
                    "type": "opportunity_vs_lead",
                    "data": data,
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "selected_quarter": selected_quarter
                }

        # Handle opportunity_vs_lead_percentage analysis
        elif analysis_type == "opportunity_vs_lead_percentage":
            if object_type == "lead":
                total_leads = len(filtered_df)
                opportunities = len(filtered_df[filtered_df["Lead_Converted__c"] == True])
                percentage = (opportunities / total_leads * 100) if total_leads > 0 else 0
                graph_data["Opportunity vs Lead"] = {
                    "Opportunities": percentage,
                    "Non-Opportunities": 100 - percentage
                }
                return {
                    "type": "percentage",
                    "value": round(percentage, 1),
                    "label": "Percentage of Leads Converted to Opportunities",
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": f"Opportunity vs Lead percentage analysis not supported for {object_type}"}
        
        elif analysis_type == "count":
            return {
                "type": "metric",
                "value": len(filtered_df),
                "label": f"Total {object_type.capitalize()} Count",
                "graph_data": graph_data,
                "filtered_data": filtered_df,
                "selected_quarter": selected_quarter
            }

        elif analysis_type == "disqualification_summary":
            df = leads_df if object_type == "lead" else opportunities_df
            field = analysis_plan.get("field", "Disqualification_Reason__c")
            if df is None or df.empty:
                return {"type": "error", "message": f"No data available for {object_type}"}
            if field not in df.columns:
                return {"type": "error", "message": f"Field {field} not found in {object_type} data"}
            # df = df[df[field].notna()]
            # disqual_counts = df[field].value_counts()
            # total = disqual_counts.sum()
            # ✅ Filter out None, NaN, empty strings, and "None" (as string)
            filtered_df = df[df[field].notna() & (df[field] != "") & (df[field].astype(str).str.lower() != "none")]

            # Generate counts and percentages
            disqual_counts = filtered_df[field].value_counts()
            total = disqual_counts.sum()
            summary = [
                {
                    "Disqualification Reason": str(reason),
                    "Count": count,
                    "Percentage": round((count / total) * 100, 2)
                }
                for reason, count in disqual_counts.items()
            ]
            graph_data[field] = {str(k): v for k, v in disqual_counts.items()}
            return {
                "type": "disqualification_summary",
                "data": summary,
                "field": field,
                "total": total,
                "graph_data": graph_data,
                "filtered_data": filtered_df,
                "selected_quarter": selected_quarter
            }

        elif analysis_type == "junk_reason_summary":
            df = leads_df if object_type == "lead" else opportunities_df
            field = analysis_plan.get("field", "Junk_Reason__c")
            if df is None or df.empty:
                return {"type": "error", "message": f"No data available for {object_type}"}
            if field not in df.columns:
                return {"type": "error", "message": f"Field {field} not found in {object_type} data"}
            filtered_df = df[df[field].notna() & (df[field] != "") & (df[field].astype(str).str.lower() != "none")]
            junk_counts = filtered_df[field].value_counts()
            total = junk_counts.sum()
            summary = [
                {
                    "Junk Reason": str(reason),
                    "Count": count,
                    "Percentage": round((count / total) * 100, 2)
                }
                for reason, count in junk_counts.items()
            ]
            graph_data[field] = {str(k): v for k, v in junk_counts.items()}
            return {
                "type": "junk_reason_summary",
                "data": summary,
                "field": field,
                "total": total,
                "graph_data": graph_data,
                "filtered_data": filtered_df,
                "selected_quarter": selected_quarter
            }

        elif analysis_type == "filter":
            selected_columns = [col for col in filtered_df.columns if col in [
                'Id', 'Name', 'Status', 'LeadSource', 'CreatedDate', 'Customer_Feedback__c',
                'Project_Category__c', 'Property_Type__c', "Property_Size__c", 'Rating',
                'Disqualification_Reason__c', 'Type', 'Feedback__c', 'Appointment_Status__c',
                'StageName', 'Amount', 'CloseDate', 'Opportunity_Type__c'
            ]]
            if not selected_columns:
                selected_columns = filtered_df.columns[:5].tolist()
            result_df = filtered_df[selected_columns]
            return {
                "type": "table",
                "data": result_df.to_dict(orient="records"),
                "columns": selected_columns,
                "graph_data": graph_data,
                "count": len(filtered_df),
                "filtered_data": filtered_df,
                "selected_quarter": selected_quarter
            }
            
        

        elif analysis_type == "recent":
            if 'CreatedDate' in filtered_df.columns:
                filtered_df['CreatedDate'] = pd.to_datetime(filtered_df['CreatedDate'], utc=True, errors='coerce')
                filtered_df = filtered_df.sort_values('CreatedDate', ascending=False)
                selected_columns = [col for col in filtered_df.columns if col in [
                    'Id', 'Name', 'Status', 'LeadSource', 'CreatedDate', 'Customer_Feedback__c',
                    'Project_Category__c', 'Property_Type__c', "Property_Size__c", 'Rating',
                    'Disqualification_Reason__c', 'Type', 'Feedback__c', 'Appointment_Status__c',
                    'StageName', 'Amount', 'CloseDate', 'Opportunity_Type__c'
                ]]
                if not selected_columns:
                    selected_columns = filtered_df.columns[:5].tolist()
                result_df = filtered_df[selected_columns]
                return {
                    "type": "table",
                    "data": result_df.to_dict(orient="records"),
                    "columns": selected_columns,
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": "CreatedDate field required for recent analysis"}

        elif analysis_type == "distribution":
            valid_fields = [f for f in fields if f in df.columns]
            if not valid_fields:
                return {"type": "error", "message": f"No valid fields for distribution: {fields}"}
            result_data = {}
            if is_product_related and object_type == "lead":
                if is_sales_related:
                    sales_data = filtered_df.groupby(["Project_Category__c", "Lead_Converted__c"]).size().reset_index(name="Count")
                    result_data["Project_Category__c_Lead_Converted__c"] = sales_data.to_dict(orient="records")
                    for field in ["Project_Category__c", "Lead_Converted__c"]:
                        graph_data[field] = filtered_df[field].dropna().value_counts().to_dict()
                else:
                    funnel_data = filtered_df.groupby(["Project_Category__c", "Status"]).size().reset_index(name="Count")
                    result_data["Project_Category__c_Status"] = funnel_data.to_dict(orient="records")
                    for field in ["Project_Category__c", "Status"]:
                        graph_data[field] = filtered_df[field].dropna().value_counts().to_dict()
            else:
                for field in valid_fields:
                    filtered_df = filtered_df[filtered_df[field].notna() & (filtered_df[field].astype(str).str.lower() != 'none')]
                    total = len(filtered_df)
                    value_counts = filtered_df[field].value_counts().head(10)
                    percentages = (value_counts / total * 100).round(2)
                    result_data[field] = {
                        "counts": value_counts.to_dict(),
                        "percentages": percentages.to_dict()
                    }
                    graph_data[field] = value_counts.to_dict()

            return {
                "type": "distribution",
                "fields": valid_fields,
                "data": result_data,
                "graph_data": graph_data,
                "filtered_data": filtered_df,
                "is_product_related": is_product_related,
                "is_sales_related": is_sales_related,
                "selected_quarter": selected_quarter
            }

        elif analysis_type == "quarterly_distribution":
            if object_type in ["lead", "event", "opportunity", "task"] and 'CreatedDate' in filtered_df.columns:
                quarterly_data = {}
                quarterly_graph_data = {}
                valid_fields = [f for f in fields if f in filtered_df.columns]
                if not valid_fields:
                    quarterly_data[selected_quarter] = {}
                    logger.info(f"No valid fields for {selected_quarter}, skipping")
                    return {
                        "type": "quarterly_distribution",
                        "fields": valid_fields,
                        "data": quarterly_data,
                        "graph_data": {selected_quarter: quarterly_graph_data},
                        "filtered_data": filtered_df,
                        "is_sales_related": is_sales_related,
                        "selected_quarter": selected_quarter
                    }
                field = valid_fields[0]
                logger.info(f"Field for distribution: {field}")
                logger.info(f"Filtered DataFrame before value_counts:\n{filtered_df[field].head().to_string()}")
                dist = filtered_df[field].value_counts().to_dict()
                dist = {str(k): v for k, v in dist.items()}
                logger.info(f"Distribution for {field} in {selected_quarter}: {dist}")
                if object_type == "lead" and field == "Lead_Converted__c":
                    if 'True' not in dist:
                        dist['True'] = 0
                    if 'False' not in dist:
                        dist['False'] = 0
                quarterly_data[selected_quarter] = dist
                quarterly_graph_data[field] = dist
                for filter_field in filters.keys():
                    if filter_field in filtered_df.columns:
                        quarterly_graph_data[filter_field] = filtered_df[filter_field].dropna().value_counts().to_dict()
                        logger.info(f"Graph data for filter field {filter_field}: {quarterly_graph_data[filter_field]}")
                graph_data = {selected_quarter: quarterly_graph_data}

                return {
                    "type": "quarterly_distribution",
                    "fields": valid_fields,
                    "data": quarterly_data,
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "is_sales_related": is_sales_related,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": f"Quarterly distribution requires {object_type} data with CreatedDate"}

        elif analysis_type == "source_wise_funnel":
            if object_type == "lead":
                required_fields = ["LeadSource"]
                missing_fields = [f for f in required_fields if f not in filtered_df.columns]
                if missing_fields:
                    return {"type": "error", "message": f"Missing fields: {missing_fields}"}
                funnel_data = filtered_df.groupby(required_fields).size().reset_index(name="Count")
                graph_data["LeadSource"] = funnel_data.set_index("LeadSource")["Count"].to_dict()
                return {
                    "type": "source_wise_funnel",
                    "fields": fields,
                    "funnel_data": funnel_data,
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "is_sales_related": is_sales_related,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": f"Source-wise funnel not supported for {object_type}"}

        
        #======================================new code=================
        elif analysis_type == "conversion_funnel":
            if object_type == "lead":
                required_fields = ["Customer_Feedback__c", "Status", "Is_Appointment_Booked__c"]
                missing_fields = [f for f in required_fields if f not in filtered_df.columns]
                if missing_fields:
                    logger.error(f"Missing fields for conversion_funnel: {missing_fields}")
                    return {"type": "error", "message": f"Missing fields: {missing_fields}"}
                
                filtered_events = events_df.copy()
                for field, value in filters.items():
                    if field in filtered_events.columns:
                        if isinstance(value, str):
                            filtered_events = filtered_events[filtered_events[field] == value]
                        elif isinstance(value, dict):
                            if field == "CreatedDate":
                                if "$gte" in value:
                                    gte_value = pd.to_datetime(value["$gte"], utc=True)
                                    filtered_events = filtered_events[filtered_events[field] >= gte_value]
                                if "$lte" in value:
                                    lte_value = pd.to_datetime(value["$lte"], utc=True)
                                    filtered_events = filtered_events[filtered_events[field] <= lte_value]
                
                total_leads = len(filtered_df)
                valid_leads = len(filtered_df[filtered_df["Customer_Feedback__c"] != 'Junk'])
                sol_leads = len(filtered_df[filtered_df["Status"] == "Qualified"])
                meeting_booked = len(filtered_df[
                    (filtered_df["Status"] == "Qualified") & (filtered_df["Is_Appointment_Booked__c"] == True)
                ])
                meeting_done = len(filtered_events[(filtered_events["Appointment_Status__c"] == "Completed")])
                disqualified_leads = len(filtered_df[filtered_df["Customer_Feedback__c"] == "Not Interested"])
                # Calculate percentage of disqualified leads
                disqualified_percentage = (disqualified_leads / total_leads * 100) if total_leads > 0 else 0
                open_leads = len(filtered_df[filtered_df["Status"].isin(["New", "Nurturing"])])
                junk_percentage = ((total_leads - valid_leads) / total_leads * 100) if total_leads > 0 else 0
                vl_sol_ratio = (valid_leads / sol_leads) if sol_leads > 0 else "N/A"
                tl_vl_ratio = (total_leads / valid_leads) if valid_leads > 0 else "N/A"
                sol_mb_ratio = (sol_leads / meeting_booked) if meeting_booked > 0 else "N/A"
                meeting_booked_meeting_done = (meeting_done / meeting_booked) if meeting_done > 0 else "N/A"
                funnel_metrics = {
                    "TL:VL Ratio": round(tl_vl_ratio, 2) if isinstance(tl_vl_ratio, (int, float)) else tl_vl_ratio,
                    "VL:SOL Ratio": round(vl_sol_ratio, 2) if isinstance(vl_sol_ratio, (int, float)) else vl_sol_ratio,
                    "SOL:MB Ratio": round(sol_mb_ratio, 2) if isinstance(sol_mb_ratio, (int, float)) else sol_mb_ratio,
                    "MB:MD Ratio": round(meeting_booked_meeting_done, 2) if isinstance(meeting_booked_meeting_done, (int, float)) else meeting_booked_meeting_done,
                }
                graph_data["Funnel Stages"] = {
                    "Total Leads": total_leads,
                    "Valid Leads": valid_leads,
                    "Sales Opportunity Leads (SOL)": sol_leads,
                    "Meeting Booked": meeting_booked,
                    "Meeting Done": meeting_done
                }
                return {
                    "type": "conversion_funnel",
                    "funnel_metrics": funnel_metrics,
                    "quarterly_data": {selected_quarter: {
                        "Total Leads": total_leads,
                        "Valid Leads": valid_leads,
                        "Sales Opportunity Leads (SOL)": sol_leads,
                        "Meeting Booked": meeting_booked,
                        "Disqualified Leads": disqualified_leads,
                        "Disqualified %": round(disqualified_percentage, 2),  # Add percentage
                        "Open Leads": open_leads,
                        "Junk %": round(junk_percentage, 2),
                        "VL:SOL Ratio": round(vl_sol_ratio, 2) if isinstance(vl_sol_ratio, (int, float)) else vl_sol_ratio,
                        "SOL:MB Ratio": round(sol_mb_ratio, 2) if isinstance(sol_mb_ratio, (int, float)) else sol_mb_ratio
                    }},
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "is_sales_related": is_sales_related,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": f"Conversion funnel not supported for {object_type}"}
        #===============================end of code===================
        elif analysis_type == "Total_Appointment":
            if object_type == "event":
                required_fields = ["Appointment_Status__c"]
                missing_fields = [f for f in required_fields if f not in filtered_df.columns]
                if missing_fields:
                    logger.error(f"Missing fields for conversion_funnel: {missing_fields}")
                    return {"type": "error", "message": f"Missing fields: {missing_fields}"}            
                
    
                # Calculate Appointment Status Counts
                if 'Appointment_Status__c' in filtered_events.columns:
                    appointment_status_counts = filtered_events['Appointment_Status__c'].value_counts().to_dict()
                    logger.info(f"Appointment Status counts: {appointment_status_counts}")
                else:
                    appointment_status_counts = {}
                    logger.warning("Status column not found in filtered_events")
                    
            return {"type": "error", "message": f" Total Appointments for {object_type}"}
        #====================================end new code ======================
        
        elif analysis_type == "percentage":
            if object_type in ["lead", "event", "opportunity", "task"]:
                total_records = len(df)
                percentage = (len(filtered_df) / total_records * 100) if total_records > 0 else 0
                # Custom label for disqualification percentage
                if "Customer_Feedback__c" in filters and filters["Customer_Feedback__c"] == "Not Interested":
                    label = "Percentage of Disqualified Leads"
                else:
                    label = "Percentage of " + " and ".join([f"{FIELD_DISPLAY_NAMES.get(f, f)} = {v}" for f, v in filters.items()])
                graph_data["Percentage"] = {"Matching Records": percentage, "Non-Matching Records": 100 - percentage}
                return {
                    "type": "percentage",
                    "value": round(percentage, 1),
                    "label": label,
                    "graph_data": graph_data,
                    "filtered_data": filtered_df,
                    "selected_quarter": selected_quarter
                }
            return {"type": "error", "message": f"Percentage analysis not supported for {object_type}"}

        elif analysis_type == "top":
            valid_fields = [f for f in fields if f in df.columns]
            if not valid_fields:
                return {"type": "error", "message": f"No valid fields for top values: {fields}"}
            result_data = {field: filtered_df[field].value_counts().head(5).to_dict() for field in valid_fields}
            for field in valid_fields:
                graph_data[field] = filtered_df[field].value_counts().head(5).to_dict()
            return {
                "type": "distribution",
                "fields": valid_fields,
                "data": result_data,
                "graph_data": graph_data,
                "filtered_data": filtered_df,
                "is_sales_related": is_sales_related,
                "selected_quarter": selected_quarter
            }

        return {"type": "info", "message": analysis_plan.get("explanation", "Analysis completed")}

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {"type": "error", "message": f"Analysis failed: {str(e)}"}

def render_graph(graph_data, relevant_fields, title_suffix="", quarterly_data=None):
    logger.info(f"Rendering graph with data: {graph_data}, relevant fields: {relevant_fields}")
    if not graph_data:
        st.info("No data available for graph.")
        return
    for field in relevant_fields:
        if field not in graph_data:
            logger.warning(f"No graph data for field: {field}")
            continue
        data = graph_data[field]
        if not data:
            logger.warning(f"Empty graph data for field: {field}")
            continue
        
        # Special handling for opportunity_vs_lead
        if field == "Opportunity vs Lead":
            try:
                plot_data = [{"Category": k, "Count": v} for k, v in data.items() if k is not None and not pd.isna(k)]
                if not plot_data:
                    st.info("No valid data for Opportunity vs Lead graph.")
                    continue
                plot_df = pd.DataFrame(plot_data)
                plot_df = plot_df.sort_values(by="Count", ascending=False)
                fig = px.bar(
                    plot_df,
                    x="Count",
                    y="Category",
                    orientation='h',
                    title=f"Opportunity vs Lead Distribution{title_suffix}",
                    color="Category",
                    color_discrete_map={
                        "Total Leads": "#1f77b4",
                        "Opportunities": "#ff7f0e"
                    }
                )
                fig.update_layout(xaxis_title="Count", yaxis_title="Category")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                logger.error(f"Error rendering Opportunity vs Lead graph: {e}")
                st.error(f"Failed to render Opportunity vs Lead graph: {str(e)}")
        elif field == "Funnel Stages":  # Special handling for conversion funnel
            # Filter funnel stages to match the fields in quarterly_data (used in the table)
            if quarterly_data is None:
                logger.warning("quarterly_data not provided for conversion funnel")
                st.info("Cannot render funnel graph: missing quarterly data.")
                continue
            # Get the stages from quarterly_data that match the table
            table_stages = list(quarterly_data.keys())
            # Only include stages that are both in graph_data and quarterly_data
            filtered_funnel_data = {stage: data[stage] for stage in data if stage in ["Total Leads", "Valid Leads", "Sales Opportunity Leads (SOL)", "Meeting Booked", "Meeting Done"]}
            if not filtered_funnel_data:
                logger.warning("No matching funnel stages found between graph_data and table data")
                st.info("No matching data for funnel graph.")
                continue
            plot_df = pd.DataFrame.from_dict(filtered_funnel_data, orient='index', columns=['Count']).reset_index()
            plot_df.columns = ["Stage", "Count"]
            try:
                fig = go.Figure(go.Funnel(
                    y=plot_df["Stage"],
                    x=plot_df["Count"],
                    textinfo="value+percent initial",
                    marker={"color": "#1f77b4"}
                ))
                fig.update_layout(title=f"Lead Conversion Funnel{title_suffix}")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                logger.error(f"Error rendering Plotly funnel chart: {e}")
                st.error(f"Failed to render graph: {str(e)}")
        else:
            plot_data = [{"Category": str(k), "Count": v} for k, v in data.items() if k is not None and not pd.isna(k)]
            if not plot_data:
                st.info(f"No valid data for graph for {FIELD_DISPLAY_NAMES.get(field, field)}.")
                continue
            plot_df = pd.DataFrame(plot_data)
            plot_df = plot_df.sort_values(by="Count", ascending=False)
            try:
                fig = px.bar(
                    plot_df,
                    x="Category",
                    y="Count",
                    title=f"Distribution of {FIELD_DISPLAY_NAMES.get(field, field)}{title_suffix}",
                    color="Category"
                )
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                logger.error(f"Error rendering Plotly chart: {e}")
                st.error(f"Failed to render graph: {str(e)}")

def display_analysis_result(result, analysis_plan=None, user_question=""):
    """
    Display the analysis result using Streamlit, including tables, metrics, and graphs.
    """
    result_type = result.get("type", "")
    object_type = analysis_plan.get("object_type", "lead") if analysis_plan else "lead"
    is_product_related = result.get("is_product_related", False)
    is_sales_related = result.get("is_sales_related", False)
    is_disqualification_reason = result.get("is_disqualification_reason", False)
    selected_quarter = result.get("selected_quarter", None)
    graph_data = result.get("graph_data", {})
    filtered_data = result.get("filtered_data", pd.DataFrame())

    logger.info(f"Displaying result for type: {result_type}, user question: {user_question}")

    if analysis_plan and analysis_plan.get("filters"):
        st.info(f"Filters applied: {analysis_plan['filters']}")

    def prepare_filtered_display_data(filtered_data, analysis_plan):
        if filtered_data.empty:
            logger.warning("Filtered data is empty for display")
            return pd.DataFrame(), []
        display_cols = []
        prioritized_cols = []
        if analysis_plan and analysis_plan.get("filters"):
            for field in analysis_plan["filters"]:
                if field in filtered_data.columns and field not in prioritized_cols:
                    prioritized_cols.append(field)
        if analysis_plan and analysis_plan.get("fields"):
            for field in analysis_plan["fields"]:
                if field in filtered_data.columns and field not in prioritized_cols:
                    prioritized_cols.append(field)
        display_cols.extend(prioritized_cols)
        preferred_cols = (
            ['Id', 'Name', 'Phone__c', 'LeadSource', 'Status', 'CreatedDate', 'Lead_Converted__c']
            if object_type == "lead"
            else ['Service_Request_Number__c', 'Type', 'Subject', 'CreatedDate']
            if object_type == "case"
            else ['Id', 'Subject', 'StartDateTime', 'EndDateTime', 'Appointment_Status__c', 'CreatedDate']
            if object_type == "event"
            else ['Id', 'Name', 'StageName', 'Amount', 'CloseDate', 'CreatedDate']
            if object_type == "opportunity"
            else ['Id', 'Subject', 'Transfer_Status__c', 'Customer_Feedback__c', 'Sales_Team_Feedback__c', 'Status', 'Follow_Up_Status__c']
            if object_type == "task"
            else []
        )
        max_columns = 10
        remaining_slots = max_columns - len(prioritized_cols)
        for col in preferred_cols:
            if col in filtered_data.columns and col not in display_cols and remaining_slots > 0:
                display_cols.append(col)
                remaining_slots -= 1
        display_data = filtered_data[display_cols].rename(columns=FIELD_DISPLAY_NAMES)
        return display_data, display_cols

    title_suffix = ""
    if result_type == "quarterly_distribution" and selected_quarter:
        normalized_quarter = selected_quarter.strip()
        title_suffix = f" in {normalized_quarter}"
        logger.info(f"Selected quarter for display: '{normalized_quarter}' (length: {len(normalized_quarter)})")
        logger.info(f"Selected quarter bytes: {list(normalized_quarter.encode('utf-8'))}")
    else:
        logger.info(f"No quarter selected or not applicable for result_type: {result_type}")
        normalized_quarter = selected_quarter

    logger.info(f"Graph data: {graph_data}")
    
    # Handle opportunity_vs_lead result type
    if result_type == "opportunity_vs_lead":
        logger.info("Rendering opportunity vs lead summary")
        st.subheader(f"Opportunity vs Lead Summary{title_suffix}")
        df = pd.DataFrame(result["data"])
        st.dataframe(df.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)
        #st.info(f"Found {len(filtered_data)} leads matching the criteria.")
    # Existing result types
    elif result_type == "metric":
        logger.info("Rendering metric result")
        st.metric(result.get("label", "Result"), f"{result.get('value', 0)}")

    elif result_type == "disqualification_summary":
        logger.info("Rendering disqualification summary")
        st.subheader(f"Disqualification Reasons Summary{title_suffix}")
        df = pd.DataFrame(result["data"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif result_type == "junk_reason_summary":
        logger.info("Rendering junk reason summary")
        st.subheader(f"Junk Reason Summary{title_suffix}")
        df = pd.DataFrame(result["data"])
        st.dataframe(df, use_container_width=True)

    elif result_type == "conversion_funnel":
        logger.info("Rendering conversion funnel")
        funnel_metrics = result.get("funnel_metrics", {})
        quarterly_data = result.get("quarterly_data", {}).get(selected_quarter, {})
        appointment_status_counts = result.get("appointment_status_counts", 0)
        st.subheader(f"Lead Conversion Funnel Analysis{title_suffix}")
        st.info(f"Found {len(filtered_data)} leads matching the criteria.")


        #======================new code==================
        # Display Appointment Status Counts as a table
        if appointment_status_counts:
            st.subheader("Appointment Status Counts")
            status_df = pd.DataFrame.from_dict(appointment_status_counts, orient='index', columns=['Count']).reset_index()
            status_df.columns = ["Appointment Status", "Count"]
            status_df = status_df.sort_values(by="Count", ascending=False)
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No appointment status data available.")
        #======================end of code=========================
        # Display the funnel metrics table (ratios)
        if funnel_metrics:
            st.subheader("Funnel Metrics")
            metrics_df = pd.DataFrame.from_dict(funnel_metrics, orient='index', columns=['Value']).reset_index()
            metrics_df.columns = ["Metric", "Value"]
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    elif result_type == "quarterly_distribution":
        logger.info("Rendering quarterly distribution")
        fields = result.get("fields", [])
        quarterly_data = result.get("data", {})
        logger.info(f"Quarterly data: {quarterly_data}")
        logger.info(f"Quarterly data keys: {list(quarterly_data.keys())}")
        for key in quarterly_data.keys():
            logger.info(f"Quarterly data key: '{key}' (length: {len(key)})")
            logger.info(f"Quarterly data key bytes: {list(key.encode('utf-8'))}")
        if not quarterly_data:
            st.info(f"No {object_type} data found.")
            return
        st.subheader(f"Quarterly {object_type.capitalize()} Results{title_suffix}")
        field = fields[0] if fields else None
        field_display = FIELD_DISPLAY_NAMES.get(field, field) if field else "Field"

        if not filtered_data.empty:
            st.info(f"Found {len(filtered_data)} rows.")
            show_data = st.button("Show Data", key=f"show_data_quarterly_{result_type}_{normalized_quarter}")
            if show_data:
                st.write(f"Filtered {object_type.capitalize()} Data")
                display_data, display_cols = prepare_filtered_display_data(filtered_data, analysis_plan)
                st.dataframe(display_data, use_container_width=True, hide_index=True)

        normalized_quarterly_data = {k.strip(): v for k, v in quarterly_data.items()}
        logger.info(f"Normalized quarterly data keys: {list(normalized_quarterly_data.keys())}")
        for key in normalized_quarterly_data.keys():
            logger.info(f"Normalized key: '{key}' (length: {len(key)})")
            logger.info(f"Normalized key bytes: {list(key.encode('utf-8'))}")

        dist = None
        if normalized_quarter in normalized_quarterly_data:
            dist = normalized_quarterly_data[normalized_quarter]
            logger.info(f"Found exact match for quarter: {normalized_quarter}")
        else:
            for key in normalized_quarterly_data.keys():
                if key == normalized_quarter:
                    dist = normalized_quarterly_data[key]
                    logger.info(f"Found matching key after strict comparison: '{key}'")
                    break
                if list(key.encode('utf-8')) == list(normalized_quarter.encode('utf-8')):
                    dist = normalized_quarterly_data[key]
                    logger.info(f"Found matching key after byte-level comparison: '{key}'")
                    break

        logger.info(f"Final distribution for {normalized_quarter}: {dist}")
        if not dist:
            if quarterly_data:
                for key, value in quarterly_data.items():
                    if "Q4" in key:
                        dist = value
                        logger.info(f"Forcing display using key: '{key}' with data: {dist}")
                        break
            if not dist:
                st.info(f"No data found for {normalized_quarter}.")
                return

        quarter_df = pd.DataFrame.from_dict(dist, orient='index', columns=['Count']).reset_index()
        if object_type == "lead" and field == "Lead_Converted__c":
            quarter_df['index'] = quarter_df['index'].map({
                'True': 'Converted (Sale)',
                'False': 'Not Converted (No Sale)'
            })
        quarter_df.columns = [f"{field_display}", "Count"]
        quarter_df = quarter_df.sort_values(by="Count", ascending=False)
        st.dataframe(quarter_df, use_container_width=True, hide_index=True)

    elif result_type == "source_wise_funnel":
        logger.info("Rendering source-wise funnel")
        funnel_data = result.get("funnel_data", pd.DataFrame())
        st.subheader(f"{object_type.capitalize()} Results{title_suffix}")
        st.info(f"Found {len(filtered_data)} rows.")

        if st.button("Show Data", key=f"source_funnel_data_{result_type}_{selected_quarter}"):
            st.write(f"Filtered {object_type.capitalize()} Data")
            display_data, display_cols = prepare_filtered_display_data(filtered_data, analysis_plan)
            st.dataframe(display_data, use_container_width=True, hide_index=True)

        if not funnel_data.empty:
            st.subheader("Source-Wise Lead")
            st.info("Counts grouped by Source")
            funnel_data = funnel_data.sort_values(by="Count", ascending=False)
            st.dataframe(funnel_data.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)

    elif result_type == "table":
        logger.info("Rendering table result")
        data = result.get("data", [])
        data_df = pd.DataFrame(data)
        if data_df.empty:
            st.info(f"No {object_type} data found.")
            return
        st.subheader(f"{object_type.capitalize()} Results{title_suffix}")
        st.info(f"Found {len(data_df)} rows.")

        if st.button("Show Data", key=f"table_data_{result_type}_{selected_quarter}"):
            st.write(f"Filtered {object_type.capitalize()} Data")
            display_data, display_cols = prepare_filtered_display_data(data_df, analysis_plan)
            st.dataframe(display_data, use_container_width=True, hide_index=True)

    elif result_type == "distribution":
        logger.info("Rendering distribution result")
        data = result.get("data", {})
        st.subheader(f"Distribution Results{title_suffix}")

        if not filtered_data.empty:
            st.info(f"Found {len(filtered_data)} rows.")
            if st.button("Show Data", key=f"dist_data_{result_type}_{selected_quarter}"):
                st.write(f"Filtered {object_type.capitalize()} Data")
                display_data, display_cols = prepare_filtered_display_data(filtered_data, analysis_plan)
                st.dataframe(display_data, use_container_width=True, hide_index=True)

        if is_product_related and object_type == "lead":
            if is_sales_related:
                st.write("Product-wise Sales")
                product_sales_data = pd.DataFrame(data.get("Project_Category__c_Lead_Converted__c", []))
                if not product_sales_data.empty:
                    product_sales_data = product_sales_data[product_sales_data["Lead_Converted__c"] == True]
                    if not product_sales_data.empty:
                        product_sales_data = product_sales_data.drop(columns=["Lead_Converted__c"])
                        product_sales_data = product_sales_data.sort_values(by="Count", ascending=False)
                        st.dataframe(product_sales_data.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No lead data found for the selected criteria.")
                else:
                    st.warning("No product lead data.")
            else:
                st.write("Product-wise Distribution")
                product_funnel_data = pd.DataFrame(data.get("Project_Category__c_Status", []))
                if not product_funnel_data.empty:
                    product_funnel_data = product_funnel_data.sort_values(by="Count", ascending=False)
                    st.dataframe(product_funnel_data.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)
                else:
                    st.warning("No product data.")
        elif is_disqualification_reason and object_type == "lead":
            st.write("Disqualification Reasons Distribution")
            dist_data = data.get("Disqualification_Reason__c", {})
            if dist_data:
                dist_df = pd.DataFrame.from_dict(dist_data["counts"], orient='index', columns=['Count']).reset_index()
                dist_df.columns = ["Disqualification_Reason__c", "Count"]
                dist_df = dist_df.sort_values(by="Count", ascending=False)
                st.dataframe(dist_df.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)
            else:
                st.warning("No disqualification reason data available.")
        else:
            is_geography_related = "geography" in user_question.lower() or "city" in user_question.lower()
            group_fields = result.get("fields", []) + [f for f in analysis_plan.get("filters", {}).keys() if f in filtered_data.columns]
            if group_fields and not is_geography_related:
                st.write(f"Distribution of {', '.join([FIELD_DISPLAY_NAMES.get(f, f) for f in group_fields])}")
                dist_df = filtered_data[group_fields].groupby(group_fields).size().reset_index(name="Count")
                dist_df = dist_df.sort_values(by="Count", ascending=False)
                st.dataframe(dist_df.rename(columns=FIELD_DISPLAY_NAMES), use_container_width=True, hide_index=True)
            else:
                if is_geography_related:
                    field = "City__c"
                    if field not in filtered_data.columns:
                        st.warning(f"No {FIELD_DISPLAY_NAMES.get(field, field)} data available in the filtered dataset.")
                        return
                    def clean_city_name(city):
                        if pd.isna(city) or not city or city == '':
                            return "Unknown"
                        city = str(city).strip().lower()
                        suffixes = [" city", " ncr", " metro", " urban", " rural"]
                        for suffix in suffixes:
                            city = city.replace(suffix, "")
                        return city.strip()
                    filtered_data['Cleaned_City__c'] = filtered_data[field].apply(clean_city_name)
                    dist = filtered_data['Cleaned_City__c'].value_counts().to_dict()
                    if not dist:
                        st.warning(f"No valid city data available for {FIELD_DISPLAY_NAMES.get(field, field)} after cleaning.")
                        return
                    st.write(f"Distribution of {FIELD_DISPLAY_NAMES.get(field, field)}")
                    dist_df = pd.DataFrame.from_dict(dist, orient='index', columns=['Count']).reset_index()
                    dist_df.columns = ["City", "Count"]
                    dist_df["City"] = dist_df["City"].str.title()
                    dist_df = dist_df.sort_values(by="Count", ascending=False)
                    st.dataframe(dist_df, use_container_width=True, height=len(dist_df) * 35 + 50, hide_index=True)
                else:
                    for field, dist in data.items():
                        if field in ["State__c", "Country__c"]:
                            continue
                        st.write(f"Distribution of {FIELD_DISPLAY_NAMES.get(field, field)}")
                        dist_df = pd.DataFrame.from_dict(dist["counts"], orient='index', columns=['Count']).reset_index()
                        dist_df.columns = [f"{FIELD_DISPLAY_NAMES.get(field, field)}", "Count"]
                        dist_df = dist_df.sort_values(by="Count", ascending=False)
                        st.dataframe(dist_df, use_container_width=True, hide_index=True)

    elif result_type == "percentage":
        logger.info("Rendering percentage result")
        st.subheader(f"Percentage Analysis{title_suffix}")
        st.metric(result.get("label", "Percentage"), f"{result.get('value', 0)}%")

    elif result_type == "info":
        logger.info("Rendering info message")
        st.info(result.get("message", "No specific message provided"))
        return

    elif result_type == "error":
        logger.error("Rendering error message")
        st.error(result.get("message", "An error occurred"))
        return

    # Show Graph button for all applicable result types
    if result_type not in ["info", "error"]:
        show_graph = st.button("Show Graph", key=f"show_graph_{result_type}_{selected_quarter}")
        if show_graph:
            st.subheader(f"Graph{title_suffix}")
            display_data, display_cols = prepare_filtered_display_data(filtered_data, analysis_plan)
            relevant_graph_fields = [f for f in display_cols if f in graph_data]
            if result_type == "quarterly_distribution":
                render_graph(graph_data.get(normalized_quarter, {}), relevant_graph_fields, title_suffix)
                
            # For opportunity_vs_lead, explicitly include "Opportunity vs Lead"
            elif result_type == "opportunity_vs_lead":
                relevant_graph_fields = ["Opportunity vs Lead"]
                render_graph(graph_data, relevant_graph_fields, title_suffix)
            elif result_type == "conversion_funnel":
                # For conversion funnel, we pass quarterly_data to align funnel stages with the table
                quarterly_data_for_graph = result.get("quarterly_data", {}).get(selected_quarter, {})
                render_graph(graph_data, ["Funnel Stages"], title_suffix, quarterly_data=quarterly_data_for_graph)
            else:
                render_graph(graph_data, relevant_graph_fields, title_suffix)

        # Add Export to CSV option for applicable result types
        if result_type in ["table", "distribution", "quarterly_distribution", "source_wise_funnel", "conversion_funnel"]:
            if not filtered_data.empty:
                export_key = f"export_data_{result_type}_{selected_quarter}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if st.button("Export Data to CSV", key=export_key):
                    file_name = f"{result_type}_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filtered_data.to_csv(file_name, index=False)
                    st.success(f"Data exported to {file_name}")

        # Add a separator for better UI separation
        st.markdown("---")

if __name__ == "__main__":
    st.title("Analysis Dashboard")
    # Add a button to clear Streamlit cache
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared successfully!")
    user_question = st.text_input("Enter your query:", "lead conversion funnel in Q4")
    if st.button("Analyze"):
        # Sample data for testing
        sample_data = {
            "CreatedDate": [
                "2024-05-15T10:00:00Z",
                "2024-08-20T12:00:00Z",
                "2024-11-10T08:00:00Z",
                "2025-02-15T09:00:00Z"
            ],
            "Project_Category__c": [
                "ARANYAM VALLEY",
                "HARMONY GREENS",
                "DREAM HOMES",
                "ARANYAM VALLEY"
            ],
            "Lead_Converted__c": [
                True,
                False,
                True,
                False
            ],
            "Disqualification_Reason__c": [
                "Budget Issue",
                "Not Interested",
                "Budget Issue",
                "Location Issue"
            ],
            "Status": [
                "Qualified",
                "Unqualified",
                "Qualified",
                "New"
            ],
            "Customer_Feedback__c": [
                "Interested",
                "Junk",
                "Interested",
                "Not Interested",
                "disqualification "
            ],
            "Is_Appointment_Booked__c": [
                True,
                False,
                True,
                False
            ],
            "LeadSource": [
                "Facebook",
                "Google",
                "Website",
                "Facebook"
            ]
        }
        leads_df = pd.DataFrame(sample_data)
        users_df = pd.DataFrame()
        cases_df = pd.DataFrame()
        events_df = pd.DataFrame({ "Status": ["Completed"],  # Added sample task data to test Meeting Done
            "CreatedDate": ["2025-02-15T10:00:00Z", "2025-02-15T11:00:00Z"]})
        opportunities_df = pd.DataFrame()
        task_df = pd.DataFrame({
            "Status": ["Completed", "Open"],  # Added sample task data to test Meeting Done
            "CreatedDate": ["2025-02-15T10:00:00Z", "2025-02-15T11:00:00Z"]
        })

        # Analysis plan for conversion funnel
        analysis_plan = {
            "analysis_type": "conversion_funnel",
            "object_type": "lead",
            "fields": [],
            "quarter": "Q4 2024-25",
            "filters": {}
        }
        result = execute_analysis(analysis_plan, leads_df, users_df, cases_df, events_df, opportunities_df, task_df, user_question)
        display_analysis_result(result, analysis_plan, user_question)