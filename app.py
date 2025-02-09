import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from itertools import combinations

# ===================== DATA SETUP =====================

# Define file paths
automation_file_path = "automation_data.csv"  # Ensure this file exists in the working directory
activity_file_path = "automation_activity_data.csv"  # Ensure this file exists in the working directory

# Define date columns for parsing
automation_date_columns = [
    "AutomationInstanceStartTime_UTC", 
    "AutomationInstanceEndTime_UTC", 
    "AutomationInstanceScheduledTime_UTC"
]

activity_date_columns = [
    "ActivityInstanceStartTime_UTC", 
    "ActivityInstanceEndTime_UTC"
]

# Load Automation Data
df_automation = pd.read_csv(automation_file_path)

for col in automation_date_columns:
    df_automation[col] = pd.to_datetime(df_automation[col], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")  # Correct format

# Rename columns for consistency
rename_map_automation = {
    "AutomationName": "name",
    "AutomationInstanceStartTime_UTC": "start_time",
    "AutomationInstanceScheduledTime_UTC": "scheduled_time",
    "AutomationInstanceEndTime_UTC": "end_time",
    "AutomationInstanceStatus": "status",
    "AutomationInstanceActivityErrorDetails": "error"
}
df_automation.rename(columns=rename_map_automation, inplace=True)

# Ensure MemberID is treated as a string if the column exists
if "MemberID" in df_automation.columns:
    df_automation["MemberID"] = df_automation["MemberID"].astype(str)

# Calculate duration in minutes
df_automation["duration"] = (df_automation["end_time"] - df_automation["start_time"]).dt.total_seconds() / 60

# Load Automation Activity Data
df_activity = pd.read_csv(activity_file_path)

for col in activity_date_columns:
    df_activity[col] = pd.to_datetime(df_activity[col], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")  # Correct format

rename_map_activity = {
    "AutomationName": "automation_name",
    "ActivityType": "activity_type",
    "ActivityName": "activity_name",
    "ActivityInstanceStartTime_UTC": "activity_start_time",
    "ActivityInstanceEndTime_UTC": "activity_end_time",
    "ActivityInstanceStatus": "activity_status",
    "ActivityInstanceStatusDetails": "activity_status_details"
}

df_activity.rename(columns=rename_map_activity, inplace=True)

# Calculate duration in minutes for activities
df_activity["duration"] = (df_activity["activity_end_time"] - df_activity["activity_start_time"]).dt.total_seconds() / 60

# ===================== PAGE CONFIGURATION =====================

# Page styling
st.set_page_config(page_title="Automation Status Dashboard", page_icon="✅", layout="wide")
st.markdown("""
    <style>
        .stTitle {text-align: left; font-size: 32px !important; font-weight: bold;}
        .stDescription {text-align: left; font-size: 18px; color: #666;}
        .stPlotlyChart {margin: auto; text-align: center;}
        .calendar-container {text-align: left; margin: auto;}
        .chart-title {text-align: center; font-size: 22px; font-weight: bold; padding-bottom: 10px;}
        .status-section {padding: 20px 0px;}
        .stDataFrame {margin: auto; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================

# Sidebar - Business Unit Selection
st.sidebar.title("Business Unit Selection")

# Initialize mID check variable
multiple_mIDs_selected = False  

# Check if 'MemberID' column exists and find unique Business Units
if "MemberID" in df_automation.columns:
    unique_mIDs = df_automation["MemberID"].dropna().unique()

    if len(unique_mIDs) > 1:  # More than one Business Unit, show dropdown
        selected_mIDs = st.sidebar.multiselect(
            "Select Business Units (mID)", unique_mIDs, default=unique_mIDs
        )

        # Ensure at least one mID is selected
        if not selected_mIDs:
            st.sidebar.error("⚠️ No Business Unit (mID) selected. Displaying full dataset.")
            selected_mIDs = unique_mIDs  # Reset to default

        # Update the variable if more than one mID is selected
        multiple_mIDs_selected = len(selected_mIDs) > 1

        # Filter the dataset based on selected mIDs
        df_automation = df_automation[df_automation["MemberID"].isin(selected_mIDs)]

    else:
        st.sidebar.markdown("### 📌 Single Business Unit Detected")
        st.sidebar.markdown(f"Data is only from **BU `{unique_mIDs[0]}`**.")

else:
    st.sidebar.markdown("### 📌 No Business Unit Column Found")
    st.sidebar.markdown("Proceeding without Business Unit filtering.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page:", ["Automations", "Automation Activities"])

# ====================== PAGE 1: AUTOMATIONS =======================
if page == "Automations":

    # --------- STATUS SECTION ---------

    # Layout setup
    st.markdown("<h2 class='stTitle'>✅ Automation Status</h2>", unsafe_allow_html=True)
    st.markdown("<p class='stDescription'>Here you can view the statuses of your automation by selecting a timeframe.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.35, 0.65])

    with col1:
        st.markdown("### Select Timeframe")
        start_date = pd.to_datetime(st.date_input("Start date", df_automation["start_time"].min().date()))
        end_date = pd.to_datetime(st.date_input("End date", df_automation["start_time"].max().date()))
        df_filtered = df_automation[(df_automation["start_time"] >= start_date) & (df_automation["start_time"] <= end_date)]

    with col2:
        status_counts = df_filtered["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.markdown("<h3 class='chart-title' style='text-align: center;'>Automation Status Distribution</h3>", unsafe_allow_html=True)
        fig = px.pie(status_counts, names="Status", values="Count")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([0.35, 0.65])

    with col1:
        st.markdown("<div style='padding-top: 30px;'></div>", unsafe_allow_html=True)  # Adjust padding as needed
        selected_status = st.selectbox(
            "View Automation Details for:", 
            status_counts["Status"].unique()
        )

    with col2:
        if selected_status:
            # Define columns to display based on selection
            columns_to_display = ["name", "start_time", "end_time", "status"]
            
            if multiple_mIDs_selected:  
                columns_to_display.append("MemberID")  # Add mID column when multiple BUs are selected
            
            if selected_status == "Error":  
                columns_to_display.append("error")  # Add error column only if "Error" is selected
            
            error_data = df_filtered[df_filtered["status"] == selected_status][columns_to_display]
            
            st.markdown(f"<h3 class='chart-title' style='text-align: center;'>Automations with Status: {selected_status}</h3>", unsafe_allow_html=True)
            st.dataframe(error_data, hide_index=True, use_container_width=True)

    # --------- PERFORMANCE ANALYSIS SECTION ---------

    st.markdown("## 🏎️ Performance Analysis")
    st.markdown("<p class='stDescription'>Compare automation performance over different timeframes.</p>", unsafe_allow_html=True)

    # Select automation for trend analysis
    selected_automation = st.selectbox("Select an Automation to Analyze Performance Over Time", df_automation["name"].unique())

    # Precompute "week" column for the entire DataFrame (avoiding redundant computation)
    df_automation["week"] = df_automation["start_time"].dt.to_period("W").astype(str)

    # Filter only once
    df_perf_trend = df_automation[df_automation["name"] == selected_automation]

    # Compute the weekly average duration
    weekly_avg_duration = df_perf_trend.groupby("week")["duration"].mean().reset_index()


    fig = px.line(weekly_avg_duration, x="week", y="duration", title=f"📈 Performance Trend Over Time: {selected_automation}")
    st.plotly_chart(fig)

    col1, col2 = st.columns(2)

    # Define default timeframes
    end_of_last_month = datetime.today().replace(day=1) - timedelta(days=1)
    start_of_last_month = end_of_last_month.replace(day=1)
    one_week_last_month_start = start_of_last_month
    one_week_last_month_end = start_of_last_month + timedelta(days=6)

    last_week_start = datetime.today() - timedelta(days=7)
    last_week_end = datetime.today()

    with col2:
        st.markdown("### 📊 Compare Performance Across Timeframes")
        timeframe_1 = st.date_input("Select First Timeframe Start", one_week_last_month_start.date())
        timeframe_1_end = st.date_input("Select First Timeframe End", one_week_last_month_end.date())

        timeframe_2 = st.date_input("Select Second Timeframe Start", last_week_start.date())
        timeframe_2_end = st.date_input("Select Second Timeframe End", last_week_end.date())

        # Ensure the first timeframe is earlier than the second
        if timeframe_1_end >= timeframe_2:
            st.error("The first timeframe must be earlier than the second timeframe. Please adjust your selection.")
            df1, df2 = pd.DataFrame(), pd.DataFrame()  # Set empty DataFrames to avoid further processing
        else:
            # Convert to datetime
            timeframe_1, timeframe_1_end = pd.to_datetime(timeframe_1), pd.to_datetime(timeframe_1_end)
            timeframe_2, timeframe_2_end = pd.to_datetime(timeframe_2), pd.to_datetime(timeframe_2_end)

            # Filter Data Based on Selected Timeframes
            df1 = df_automation[(df_automation["start_time"] >= timeframe_1) & (df_automation["start_time"] <= timeframe_1_end)]
            df2 = df_automation[(df_automation["start_time"] >= timeframe_2) & (df_automation["start_time"] <= timeframe_2_end)]

    with col1:
        st.markdown("### 📋 Individual Automation Comparison")
        st.markdown("<p class='stDescription'>Compare avg automation duration between two timeframes. The second must be more recent.</p>", unsafe_allow_html=True)

        if not df1.empty and not df2.empty:
            # Define base columns
            columns_to_display = ["name"]

            if multiple_mIDs_selected:
                columns_to_display.append("MemberID")  # Include mID if multiple BUs are selected

            # Compute average durations for each timeframe
            df1_avg = df1.groupby(columns_to_display)["duration"].mean().reset_index().rename(columns={"duration": "Avg Duration (First)"})
            df2_avg = df2.groupby(columns_to_display)["duration"].mean().reset_index().rename(columns={"duration": "Avg Duration (Second)"})

            # Merge both timeframes
            comparison_df = pd.merge(df1_avg, df2_avg, on=columns_to_display, how="outer").fillna(0)
            
            # Remove automations with zero average duration
            comparison_df = comparison_df[(comparison_df["Avg Duration (First)"] > 0) | (comparison_df["Avg Duration (Second)"] > 0)]
            
            # Apply styling to highlight increased durations
            def highlight_increase(row):
                if row["Avg Duration (Second)"] > row["Avg Duration (First)"]:
                    return ["background-color: lightcoral"] * len(row)
                return [""] * len(row)

            if not comparison_df.empty:
                st.dataframe(comparison_df.style.apply(highlight_increase, axis=1), height=280)
            else:
                st.write("No significant data available for selected timeframes.")
        else:
            st.write("No data available for selected timeframes.")

    # Processes for Risky Hourly Automations
    # Step 1: Identify two distinct one-day timeframes from last week's data
    last_week_start = df_automation["start_time"].max() - pd.Timedelta(days=7)
    df_last_week = df_automation[df_automation["start_time"] >= last_week_start]

    unique_dates = df_last_week["start_time"].dt.date.unique()
    selected_dates = unique_dates[-2:] if len(unique_dates) >= 2 else unique_dates

    # Step 2: Find hourly automations (48+ occurrences in 2 selected days)
    hourly_automations = (
        df_last_week[df_last_week["start_time"].dt.date.isin(selected_dates)]
        .groupby("name")["start_time"]
        .count()
        .reset_index()
    )
    hourly_automations = hourly_automations[hourly_automations["start_time"] >= 48]["name"]

    # Step 3: Check if their last X occurrences meet the conditions
    REQUIRED_OCCURRENCES = 2  # You can adjust the threshold for # of times ≥ 51 min
    TOTAL_INSTANCES = 30  # You can adjust the threshold for # of times to check 

    automation_summary = []
    for automation in hourly_automations:
        last_30_durations = (
            df_automation[df_automation["name"] == automation]
            .sort_values(by="start_time", ascending=False)
            .head(TOTAL_INSTANCES)["duration"]
        )

        avg_duration = last_30_durations.mean()
        count_over_51 = (last_30_durations >= 51).sum()

        if avg_duration > 51:
            reason = "Avg duration is above 51 min"
        elif count_over_51 >= REQUIRED_OCCURRENCES:
            reason = f"There have been {count_over_51} occurrences over 51 min"
        else:
            continue  # Skip if neither condition is met

        automation_summary.append({"Automation Name": automation, "Reason": reason})

    # Convert to DataFrame
    df_valid_automations = pd.DataFrame(automation_summary)

    # Calculate average delay while handling missing values
    df_automation["delay_minutes"] = ((df_automation["start_time"] - df_automation["scheduled_time"]).dt.total_seconds() / 60).fillna(0)

    # Compute average delay per automation and exclude duplicates
    df_avg_delay = df_automation.dropna(subset=["scheduled_time"]).groupby("name")["delay_minutes"].mean().reset_index()
    df_avg_delay.rename(columns={"name": "Automation Name", "delay_minutes": "Avg Delay (minutes)"}, inplace=True)

    # Step 4: Display Results in Two Columns
    col1, col2 = st.columns([0.5, 0.5])

    with col1:
        st.markdown("### ⏳ Risky Hourly Automations (~1 Hour)")
        st.markdown("<p class='stDescription'>These automations run hourly and have durations close to 1 hour.</p>", unsafe_allow_html=True)

        if df_valid_automations.empty:
            st.write("No automation found for this criteria.")
        else:
            st.dataframe(df_valid_automations, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("### ⏳ Delayed Automations (Avg Delay)")
        st.markdown("<p class='stDescription'>Average delay duration for all automations.</p>", unsafe_allow_html=True)
        st.dataframe(df_avg_delay, hide_index=True, use_container_width=True)

    # --------- SCHEDULE SECTION ---------

    # Determine the start and end of the previous month
    selected_month_start = (df_automation["scheduled_time"].max() - pd.DateOffset(months=1)).replace(day=1)
    selected_month_end = selected_month_start + pd.DateOffset(months=1) - pd.Timedelta(days=1)  # Last day of the month

    # Filter data for the selected month (by both YEAR and MONTH)
    df_last_month = df_automation[
        (df_automation["scheduled_time"] >= selected_month_start) &
        (df_automation["scheduled_time"] <= selected_month_end)
    ]

    # Schedule Title
    st.markdown(f"## 📅 Schedule ({selected_month_start.strftime('%B %d, %Y')} - {selected_month_end.strftime('%B %d, %Y')})")

    # Find rush hours: count automations for each hour slot within the selected month
    df_last_month = df_last_month.copy()  # Ensures we are working with a separate DataFrame
    df_last_month["hour_slot"] = df_last_month["scheduled_time"].dt.strftime("%Y-%m-%d %H:00")
    rush_hours = df_last_month.groupby("hour_slot")["name"].agg(["count", list]).reset_index()
    rush_hours.columns = ["Hour Slot", "Automation_Count", "Automation_Names"]
    rush_hours = rush_hours[rush_hours["Automation_Count"] >= 3]

    # Find overlapping automations
    overlaps = []

    # Perform a self-join to compare all automations
    overlaps_df = df_automation.merge(df_automation, how="cross", suffixes=("_1", "_2"))

    # Remove self-comparisons (same automation instance)
    overlaps_df = overlaps_df[overlaps_df["start_time_1"] != overlaps_df["start_time_2"]]

    # Identify overlapping automations
    overlaps_df = overlaps_df[
        (overlaps_df["end_time_1"] > overlaps_df["start_time_2"]) &  # End of one overlaps with start of another
        (overlaps_df["start_time_1"] < overlaps_df["end_time_2"])    # Start of one overlaps with end of another
    ]

    # Compute overlap duration in minutes
    overlaps_df["Overlap_Minutes"] = (
        (overlaps_df[["end_time_1", "end_time_2"]].min(axis=1) - 
         overlaps_df[["start_time_1", "start_time_2"]].max(axis=1))
        .dt.total_seconds() / 60
    )

    # Sort automation names to ensure consistent ordering
    overlaps_df["Automation_Pair"] = overlaps_df.apply(
        lambda row: frozenset([row["name_1"], row["name_2"]]), axis=1
    )

    # Group by Automation_Pair to ensure only one row per pair
    overlaps_df = overlaps_df.sort_values("Overlap_Minutes", ascending=False).groupby("Automation_Pair").first().reset_index()

    # Extract automation names again from the frozenset
    overlaps_df["Automation_1"], overlaps_df["Automation_2"] = zip(*overlaps_df["Automation_Pair"])

    # Select relevant columns
    overlaps_df = overlaps_df[[
        "Automation_1", "start_time_1", "end_time_1", 
        "Automation_2", "start_time_2", "end_time_2", 
        "Overlap_Minutes"
    ]]

    # Rename columns for clarity
    overlaps_df.rename(columns={
        "start_time_1": "Automation 1 Start",
        "end_time_1": "Automation 1 End",
        "start_time_2": "Automation 2 Start",
        "end_time_2": "Automation 2 End"
    }, inplace=True)

    # Display Results in Full Width
    st.markdown("### ⏳ Rush Hours")
    st.markdown("<p class='stDescription'>Displays time slots with the highest automation activity.</p>", unsafe_allow_html=True)
    st.dataframe(rush_hours, hide_index=True, use_container_width=True)

    st.markdown("""
        <style>
            .stDescription { font-size: 16px; color: #666; }
            .overlap-container { padding-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='overlap-container'>", unsafe_allow_html=True)
    st.markdown("### 🔄 Overlapping Automations")
    st.markdown("<p class='stDescription'>Displays pairs of automations that run simultaneously, potentially causing conflicts or delays.</p>", unsafe_allow_html=True)

    # Ensure dataframe is not empty before displaying
    if not overlaps_df.empty:
        # Format table with better timestamp readability
        formatted_df = overlaps_df.style.format({
            "Automation 1 Start": lambda x: x.strftime("%Y-%m-%d %H:%M"),
            "Automation 1 End": lambda x: x.strftime("%Y-%m-%d %H:%M"),
            "Automation 2 Start": lambda x: x.strftime("%Y-%m-%d %H:%M"),
            "Automation 2 End": lambda x: x.strftime("%Y-%m-%d %H:%M"),
            "Overlap_Minutes": "{:.1f} min"
        })
        
        st.dataframe(formatted_df, hide_index=True, use_container_width=True)
    else:
        st.info("✅ No overlapping automations detected.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Prepare Data for Gantt Chart
    df_timeline = df_automation[["name", "start_time", "end_time", "MemberID"]].copy()
    df_timeline["duration_minutes"] = (df_timeline["end_time"] - df_timeline["start_time"]).dt.total_seconds() / 60

    # Check if multiple mIDs are selected
    multiple_mIDs_selected = df_automation["MemberID"].nunique() > 1

    # Modify names only if multiple mIDs exist
    if multiple_mIDs_selected:
        df_timeline["display_name"] = df_timeline["MemberID"].astype(str) + " | " + df_timeline["name"]
    else:
        df_timeline["display_name"] = df_timeline["name"]  # Keep normal names when only one mID

    # Plot the Timeline (Gantt Chart)
    fig = px.timeline(
        df_timeline, 
        x_start="start_time", 
        x_end="end_time", 
        y="display_name",  # Show modified names with mID prefixes only if needed
        color="name",  # Keep automations colored by name
        title="",
        labels={"display_name": "Automation Name", "name": "Automation Name"},
        hover_data=["duration_minutes", "MemberID"]
    )

    fig.update_yaxes(categoryorder="total ascending")  # Order by start time
    fig.update_layout(
        xaxis=dict(title="Time", tickformat="%Y-%m-%d %H:%M"), 
        showlegend=True  # Keep legend for automation names
    )

    # Show in Streamlit
    st.markdown("### 🕒 Full Automation Timeline")
    st.plotly_chart(fig, use_container_width=True)

# ====================== PAGE 2: AUTOMATION ACTIVITIES =======================
if page == "Automation Activities":
    # --------- PERFORMANCE SECTION ---------

    st.markdown("## ⚡ Performance")
    st.markdown("<p class='stDescription'>Monitor long-running activities that may be at risk of time-out.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.5, 0.5])

    # Queries at risk of time-out (activity_type = 300, Avg Duration > 20 min)
    query_risk = (
        df_activity[df_activity["activity_type"] == 300]
        .groupby(["activity_name", "AutomationCustomerKey"])["duration"]
        .mean()
        .reset_index()
    )
    query_risk = query_risk[query_risk["duration"] > 20]

    # Merge with Automation data using AutomationCustomerKey to get MemberID & Automation Name
    query_risk = query_risk.merge(df_automation[["AutomationCustomerKey", "MemberID", "name"]], 
                                  on="AutomationCustomerKey", how="left")

    query_risk.rename(columns={
        "activity_name": "Activity Name",
        "name": "Automation Name",
        "duration": "Avg Duration (minutes)"
    }, inplace=True)

    # Remove duplicates (each Activity Name should appear only once per Automation & MemberID)
    query_risk = query_risk.drop_duplicates(subset=["Activity Name", "Automation Name", "MemberID"])

    with col1:
        st.markdown("### 🛑 Queries at Risk of Time-out")
        if query_risk.empty:
            st.write("✅ No risky queries found.")
        else:
            st.dataframe(query_risk[["Activity Name", "Automation Name", "MemberID", "Avg Duration (minutes)"]],
                         hide_index=True, use_container_width=True)

    # Scripts at risk of time-out (activity_type = 423, Avg Duration > 20 min)
    script_risk = (
        df_activity[df_activity["activity_type"] == 423]
        .groupby(["activity_name", "AutomationCustomerKey"])["duration"]
        .mean()
        .reset_index()
    )
    script_risk = script_risk[script_risk["duration"] > 20]

    # Merge with Automation data using AutomationCustomerKey to get MemberID & Automation Name
    script_risk = script_risk.merge(df_automation[["AutomationCustomerKey", "MemberID", "name"]], 
                                    on="AutomationCustomerKey", how="left")

    script_risk.rename(columns={
        "activity_name": "Activity Name",
        "name": "Automation Name",
        "duration": "Avg Duration (minutes)"
    }, inplace=True)

    # Remove duplicates (each Activity Name should appear only once per Automation & MemberID)
    script_risk = script_risk.drop_duplicates(subset=["Activity Name", "Automation Name", "MemberID"])

    with col2:
        st.markdown("### ⚠️ Scripts at Risk of Time-out")
        if script_risk.empty:
            st.write("✅ No risky scripts found.")
        else:
            st.dataframe(script_risk[["Activity Name", "Automation Name", "MemberID", "Avg Duration (minutes)"]],
                         hide_index=True, use_container_width=True)
