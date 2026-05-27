-- ============================================================================
-- PROJECT: EduPulse K-12 Attendance Analytics Data Pipeline
-- DESCRIPTION: Sets up the cloud database environment, designs the Star Schema,
--              manages table staging, and builds the analytical business view.
-- ============================================================================

-- Create data warehouse environment
CREATE OR REPLACE DATABASE EDUPULSE_DW;
CREATE OR REPLACE SCHEMA EDUPULSE_DW.ANALYTICS;

-- 1. Create Dimension Table with full path
CREATE OR REPLACE TABLE EDUPULSE_DW.ANALYTICS.DIM_STUDENTS (
    STUDENT_ID INT PRIMARY KEY,
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    SCHOOL VARCHAR(100),
    GRADE INT,
    IEP_STATUS INT
);

-- 2. Create Fact Table with full path
CREATE OR REPLACE TABLE EDUPULSE_DW.ANALYTICS.FACT_ATTENDANCE (
    ATTENDANCE_KEY VARCHAR(50) PRIMARY KEY,
    STUDENT_ID INT,
    CALENDAR_DATE DATE,
    STATUS VARCHAR(20) DEFAULT 'Present'
);

-- ============================================================================
-- DATA MAINTENANCE & QUALITY ASSURANCE LAYER
-- ============================================================================

-- Data pipeline maintenance / reset commands used to clear stale staging environments
-- TRUNCATE TABLE EDUPULSE_DW.ANALYTICS.DIM_STUDENTS;
-- TRUNCATE TABLE EDUPULSE_DW.ANALYTICS.FACT_ATTENDANCE;

-- Verification check query to validate final file ingestion row counts
SELECT 'Students Count' as Table_Name, COUNT(*) FROM EDUPULSE_DW.ANALYTICS.DIM_STUDENTS
UNION ALL
SELECT 'Attendance Records Count' as Table_Name, COUNT(*) FROM EDUPULSE_DW.ANALYTICS.FACT_ATTENDANCE;

-- ============================================================================
-- ANALYTICS LAYER (BUSINESS DATA MART)
-- ============================================================================

-- Create View to calculate core behavioral metrics with zero-division protection
CREATE OR REPLACE VIEW EDUPULSE_DW.ANALYTICS.VW_STUDENT_ATTENDANCE_METRICS AS
SELECT 
    s.STUDENT_ID,
    s.FIRST_NAME,
    s.LAST_NAME,
    s.SCHOOL,
    s.GRADE,
    s.IEP_STATUS,
    COUNT(a.CALENDAR_DATE) AS TOTAL_DAYS_ENROLLED,
    SUM(CASE WHEN a.STATUS = 'Absent' THEN 1 ELSE 0 END) AS TOTAL_ABSENCES,
    ROUND(
        (SUM(CASE WHEN a.STATUS = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(a.CALENDAR_DATE), 0)) * 100, 
        2
    ) AS ATTENDANCE_RATE,
    CASE 
        WHEN (SUM(CASE WHEN a.STATUS = 'Absent' THEN 1 ELSE 0 END) / NULLIF(COUNT(a.CALENDAR_DATE), 0)) >= 0.10 THEN 1 
        ELSE 0 
    END AS IS_CHRONICALLY_ABSENT
FROM EDUPULSE_DW.ANALYTICS.DIM_STUDENTS s
INNER JOIN EDUPULSE_DW.ANALYTICS.FACT_ATTENDANCE a  
  ON s.STUDENT_ID = a.STUDENT_ID
GROUP BY s.STUDENT_ID, s.FIRST_NAME, s.LAST_NAME, s.SCHOOL, s.GRADE, s.IEP_STATUS;

-- Final App Validation: Query data mart to ensure proper schema output
SELECT * FROM EDUPULSE_DW.ANALYTICS.VW_STUDENT_ATTENDANCE_METRICS LIMIT 10;