import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_PATIENTS = 10000
NUM_PSYCHOLOGISTS = 50
NUM_APPOINTMENTS = 20000
NUM_SURVEYS = 15000

CITIES = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "Philadelphia",
    "San Antonio",
    "San Diego",
]
SPECIALTIES = [
    "Clinical",
    "Cognitive",
    "Developmental",
    "Educational",
    "Forensic",
    "Health",
    "Occupational",
]
SERVICE_TYPES = ["Initial Consultation", "Follow-up", "Therapy Session", "Assessment"]
STATUSES = ["Completed", "Cancelled", "No Show", "Rescheduled"]
CANCELLATION_REASONS = [
    "Sick",
    "Schedule Conflict",
    "Forgot",
    "Transportation Issue",
    "Financial",
    "Other",
]


def introduce_dirty_data(df, column, null_prob=0.05, duplicate_prob=0.02):
    mask = np.random.rand(len(df)) < null_prob
    df.loc[mask, column] = np.nan
    num_duplicates = int(len(df) * duplicate_prob)
    if num_duplicates > 0:
        duplicates = df.sample(n=num_duplicates)
        df = pd.concat([df, duplicates], ignore_index=True)
    return df


def generate_patients():
    data = []
    for _ in range(NUM_PATIENTS):
        city = random.choice(CITIES)
        if random.random() < 0.1:
            city = city.lower()
        elif random.random() < 0.1:
            city = city.upper()

        if random.random() < 0.2:
            reg_date = fake.date_between(start_date="-5y", end_date="today").strftime(
                "%m/%d/%Y"
            )
        else:
            reg_date = fake.date_between(start_date="-5y", end_date="today").strftime(
                "%Y-%m-%d"
            )

        data.append(
            {
                "patient_id": fake.uuid4(),
                "age": random.randint(18, 85),
                "gender": random.choice(["M", "F", "Other"]),
                "city": city,
                "registration_date": reg_date,
            }
        )
    df = pd.DataFrame(data)
    df = introduce_dirty_data(df, "city", null_prob=0.05, duplicate_prob=0.03)
    return df


def generate_psychologists():
    data = []
    for _ in range(NUM_PSYCHOLOGISTS):
        data.append(
            {
                "psychologist_id": fake.uuid4(),
                "specialty": random.choice(SPECIALTIES),
                "patients_per_day": random.randint(3, 8),
                "satisfaction_score": round(random.uniform(3.5, 5.0), 1),
            }
        )
    df = pd.DataFrame(data)
    return df


def generate_appointments(patient_ids, psych_ids):
    data = []
    for _ in range(NUM_APPOINTMENTS):
        appt_dt = fake.date_time_between(start_date="-2y", end_date="now")
        hour = random.randint(8, 17)
        minute = random.choice([0, 15, 30, 45])
        appt_dt = appt_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

        status = random.choices(STATUSES, weights=[0.75, 0.1, 0.05, 0.1])[0]

        attended = status == "Completed"
        cancelled = status in ["Cancelled", "Rescheduled"]

        cancellation_reason = np.nan
        if cancelled and random.random() < 0.8:
            cancellation_reason = random.choice(CANCELLATION_REASONS)

        check_in_time = np.nan
        service_start_time = np.nan
        completion_time = np.nan
        wait_time = np.nan

        if attended:
            check_in_offset = random.randint(-15, 5)
            check_in_time = appt_dt + timedelta(minutes=check_in_offset)

            start_offset = random.randint(0, 30)
            service_start_time = (
                check_in_time + timedelta(minutes=start_offset)
                if check_in_offset < 0
                else appt_dt + timedelta(minutes=start_offset)
            )

            wait_time = int((service_start_time - check_in_time).total_seconds() / 60)

            duration = random.randint(45, 60)
            completion_time = service_start_time + timedelta(minutes=duration)

            check_in_time = check_in_time.strftime("%Y-%m-%d %H:%M:%S")
            service_start_time = service_start_time.strftime("%Y-%m-%d %H:%M:%S")
            completion_time = completion_time.strftime("%Y-%m-%d %H:%M:%S")

        if random.random() < 0.1:
            appt_dt_str = appt_dt.strftime("%d-%m-%Y %H:%M")
        else:
            appt_dt_str = appt_dt.strftime("%Y-%m-%d %H:%M:%S")

        data.append(
            {
                "appointment_id": fake.uuid4(),
                "patient_id": random.choice(patient_ids),
                "psychologist_id": random.choice(psych_ids),
                "appointment_datetime": appt_dt_str,
                "status": status,
                "attended": attended,
                "cancelled": cancelled,
                "cancellation_reason": cancellation_reason,
                "check_in_time": check_in_time,
                "service_start_time": service_start_time,
                "completion_time": completion_time,
                "wait_time": wait_time,
                "service_type": random.choice(SERVICE_TYPES),
            }
        )
    df = pd.DataFrame(data)
    df = introduce_dirty_data(df, "wait_time", null_prob=0.02, duplicate_prob=0.01)
    return df


def generate_surveys(patient_ids):
    data = []
    for _ in range(NUM_SURVEYS):
        satisfaction = random.randint(1, 5)
        has_comment = random.random() < (0.8 if satisfaction in [1, 5] else 0.3)
        comment = fake.sentence() if has_comment else np.nan

        data.append(
            {
                "patient_id": random.choice(patient_ids),
                "satisfaction_level": satisfaction,
                "comments": comment,
                "service_rating": random.randint(1, 10),
            }
        )
    df = pd.DataFrame(data)
    df = introduce_dirty_data(df, "comments", null_prob=0.1, duplicate_prob=0.0)
    return df


def main():
    os.makedirs("data/raw", exist_ok=True)
    df_patients = generate_patients()
    df_psych = generate_psychologists()
    patient_ids = df_patients["patient_id"].dropna().unique()
    psych_ids = df_psych["psychologist_id"].dropna().unique()

    df_appts = generate_appointments(patient_ids, psych_ids)
    df_surveys = generate_surveys(patient_ids)

    df_patients.to_csv("data/raw/patients.csv", index=False)
    df_psych.to_csv("data/raw/psychologists.csv", index=False)
    df_appts.to_csv("data/raw/appointments.csv", index=False)
    df_surveys.to_csv("data/raw/surveys.csv", index=False)


if __name__ == "__main__":
    main()
