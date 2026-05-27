import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

num_students = 5000
schools = ['Lincoln Elementary', 'Washington Middle School', 'Kennedy High School']
grades = list(range(1, 13))

# 1. Generate Base Student Demographics
student_ids = [100000 + i for i in range(num_students)]

data_students = {
    'STUDENT_ID': student_ids,
    'FIRST_NAME': [f"Student_{i}" for i in range(num_students)],
    'LAST_NAME': [f"LastName_{i}" for i in range(num_students)],
    'SCHOOL': [random.choice(schools) for _ in range(num_students)],
    'GRADE': [random.choice(grades) for _ in range(num_students)],
    'IEP_STATUS': [np.random.choice([0, 1], p=[0.85, 0.15]) for _ in range(num_students)] # 15% IEP rate
}

df_students = pd.DataFrame(data_students)

# Introduce Messy Data Anomalies to show cleaning skills
# Add a few completely duplicate rows
duplicates = df_students.sample(n=15, random_state=42)
df_students = pd.concat([df_students, duplicates], ignore_index=True)

# 2. Generate 180 Days of Attendance Records (Fact Table)
start_date = datetime(2025, 9, 2)
date_list = [start_date + timedelta(days=x) for x in range(180)]
# Filter out weekends
academic_dates = [d for d in date_list if d.weekday() < 5]

attendance_records = []

print("Generating 180 days of attendance for 5000 students... (This may take a moment)")
for dt in academic_dates:
    date_str = dt.strftime('%Y-%m-%d')
    
    # Generate daily attendance status
    # Base probability: 94% present. We introduce risk profiles here.
    for stu_id in student_ids:
        # Give roughly 10% of students a higher risk profile (chronic absence)
        if stu_id % 10 == 0:
            status = np.random.choice(['Present', 'Absent'], p=[0.82, 0.18])
        else:
            status = np.random.choice(['Present', 'Absent'], p=[0.96, 0.04])
            
        attendance_records.append([f"{date_str}_{stu_id}", stu_id, date_str, status])

df_attendance = pd.DataFrame(attendance_records, columns=['ATTENDANCE_KEY', 'STUDENT_ID', 'CALENDAR_DATE', 'STATUS'])

# Introduce some missing status fields to clean later
df_attendance.loc[df_attendance.sample(frac=0.001).index, 'STATUS'] = np.nan

# 3. Export to CSV (Ready to upload to Snowflake or local staging)
df_students.to_csv('raw_students.csv', index=False)
df_attendance.to_csv('raw_attendance.csv', index=False)
print("Data Generation Complete! 'raw_students.csv' and 'raw_attendance.csv' have been created.")