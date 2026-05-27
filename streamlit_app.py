# Import python packages
import streamlit as st
import os
import pandas as pd

# 1. App Title & Subtitle
st.set_page_config(page_title="EduPulse Analytics", layout="wide")
st.title("📊 EduPulse: K-12 Attendance Analytics")
st.markdown("### Executive Leadership Dashboard | Data Source: Snowflake Data Mart")
st.write("---")

# 2. Grab the Snowflake Session
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

# 3. Pull Data from our View
# We use session.sql() to query our freshly minted Snowflake view
sql_query = "SELECT * FROM EDUPULSE_DW.ANALYTICS.VW_STUDENT_ATTENDANCE_METRICS"
df = session.sql(sql_query).to_pandas()

# 4. Calculate High-Level Metrics for KPIs
total_students = int(df['STUDENT_ID'].count())
avg_attendance = float(df['ATTENDANCE_RATE'].mean())
chronic_absent_count = int(df['IS_CHRONICALLY_ABSENT'].sum())
chronic_rate = (chronic_absent_count / total_students) * 100

# 5. Display KPI Cards side-by-side
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Enrolled Students", value=f"{total_students:,}")
with col2:
    st.metric(label="Average District Attendance Rate", value=f"{avg_attendance:.2f}%")
with col3:
    st.metric(label="Chronically Absent Students", value=f"{chronic_absent_count:,}", delta=f"{chronic_rate:.1f}% Rate", delta_color="inverse")

st.write("---")

# 6. School Comparison Chart
st.subheader("🏫 Average Attendance Rate by School")
# Group data by school using pandas
school_df = df.groupby('SCHOOL')['ATTENDANCE_RATE'].mean().reset_index()
st.bar_chart(data=school_df, x="SCHOOL", y="ATTENDANCE_RATE")

st.write("---")

# 7. Student Roster Search
st.subheader("📋 Student Attendance Roster")
st.markdown("Use this table to filter and identify students needing immediate intervention.")

# Add a text search box to filter by last name
search_query = st.text_input("Search student by last name:", "")
if search_query:
    filtered_df = df[df['LAST_NAME'].str.contains(search_query, case=False, na=False)]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True)