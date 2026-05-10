import pandas as pd
import sqlite3
import os


def clean_patients(df):
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["patient_id"], keep="first")
    df["city"] = df["city"].str.title()
    df["city"] = df["city"].fillna("Unknown")
    df["registration_date"] = pd.to_datetime(
        df["registration_date"], format="mixed", errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["patient_id"])
    return df


def clean_psychologists(df):
    df = df.drop_duplicates()
    df = df.dropna(subset=["psychologist_id"])
    return df


def clean_appointments(df):
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["appointment_id"], keep="first")

    datetime_cols = [
        "appointment_datetime",
        "check_in_time",
        "service_start_time",
        "completion_time",
    ]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce").dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    df.loc[df["cancelled"] == True, "cancellation_reason"] = df.loc[
        df["cancelled"] == True, "cancellation_reason"
    ].fillna("Unknown")
    df.loc[df["cancelled"] == False, "cancellation_reason"] = None

    df.loc[(df["status"] == "Completed") & (df["wait_time"].isna()), "wait_time"] = 0
    df["wait_time"] = df["wait_time"].fillna(0)

    df = df.dropna(subset=["appointment_id", "patient_id", "psychologist_id"])
    return df


def clean_surveys(df):
    df = df.drop_duplicates()
    df["comments"] = df["comments"].fillna("No comment")
    df = df.dropna(subset=["patient_id"])
    return df


def main():
    if not os.path.exists("data/raw"):
        return

    patients = pd.read_csv("data/raw/patients.csv")
    psychologists = pd.read_csv("data/raw/psychologists.csv")
    appointments = pd.read_csv("data/raw/appointments.csv")
    surveys = pd.read_csv("data/raw/surveys.csv")

    clean_p = clean_patients(patients)
    clean_psych = clean_psychologists(psychologists)
    clean_appts = clean_appointments(appointments)
    clean_surv = clean_surveys(surveys)

    conn = sqlite3.connect("data/clinic.db")

    clean_p.to_sql("patients", conn, if_exists="replace", index=False)
    clean_psych.to_sql("psychologists", conn, if_exists="replace", index=False)
    clean_appts.to_sql("appointments", conn, if_exists="replace", index=False)
    clean_surv.to_sql("surveys", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_appt_datetime ON appointments(appointment_datetime)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appt_status ON appointments(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pat_id ON patients(patient_id)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_psych_id ON psychologists(psychologist_id)"
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
