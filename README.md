# 📊 EduPulse: K-12 Cloud Data Pipeline & Analytics App

An end-to-end data engineering project that generates synthetic K-12 student behavior data, ingests it into an AWS-hosted Snowflake Data Warehouse, processes metrics via analytical SQL views, and exposes insights through a native Streamlit data application.

## 🚀 Project Architecture
1. **Data Generation:** Python script simulating realistic school attendance behavior for 5,000 students across 180 school days.
2. **Data Warehousing:** Schema design and configuration of a star schema (`DIM_STUDENTS` and `FACT_ATTENDANCE`) inside **Snowflake on AWS**.
3. **Analytics Layer:** Optimized SQL Views to aggregate daily logs into high-level student performance metrics (e.g., Chronic Absenteeism).
4. **Data Application:** A **Streamlit** dashboard built natively in Snowflake to provide school administrators with interactive, real-time analytics.

---

## 🛠️ Tech Stack & Skills Demonstrated
* **Languages:** Python (Pandas, Faker), SQL
* **Cloud Platform:** Snowflake (Data Warehouse Layer)
* **BI & Apps:** Streamlit in Snowflake (SiS)
* **Core Competencies:** ETL/ELT pipelines, dimensional modeling, cloud architecture, performance optimization (NULLIF safety handling), data validation.

---

## 📊 SQL Analytics Highlight
The core logic for defining "Chronic Absenteeism" (missing 10% or more of enrolled school days) was pushed down to the warehouse layer using this optimized view:

```sql
CREATE OR REPLACE VIEW EDUPULSE_DW.ANALYTICS.VW_STUDENT_ATTENDANCE_METRICS AS
SELECT 
    s.STUDENT_ID, s.FIRST_NAME, s.LAST_NAME, s.SCHOOL,
    COUNT(a.CALENDAR_DATE) AS TOTAL_DAYS_ENROLLED,
    SUM(CASE WHEN a.STATUS = 'Absent' THEN 1 ELSE 0 END) AS TOTAL_ABSENCES,
    ROUND((SUM(CASE WHEN a.STATUS = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(a.CALENDAR_DATE), 0)) * 100, 2) AS ATTENDANCE_RATE
FROM DIM_STUDENTS s
INNER JOIN FACT_ATTENDANCE a ON s.STUDENT_ID = a.STUDENT_ID
GROUP BY 1, 2, 3, 4;