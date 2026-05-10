import sqlite3
import pandas as pd

DB_PATH = "data/clinic.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def fetch_patient_trends():
    query = """
    SELECT strftime('%Y-%m', registration_date) AS month, COUNT(patient_id) as new_patients
    FROM patients
    GROUP BY month
    ORDER BY month;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_appointment_trends():
    query = """
    SELECT strftime('%Y-%m', appointment_datetime) AS month, COUNT(appointment_id) as total_appointments
    FROM appointments
    GROUP BY month
    ORDER BY month;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_services_usage():
    query = """
    SELECT service_type, COUNT(appointment_id) as count
    FROM appointments
    GROUP BY service_type
    ORDER BY count DESC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_operational_efficiency():
    query = """
    SELECT 
        AVG(wait_time) as avg_wait_time,
        SUM(CASE WHEN cancelled = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cancellation_rate,
        AVG(
            (julianday(completion_time) - julianday(service_start_time)) * 24 * 60
        ) as avg_service_duration_mins
    FROM appointments;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_psychologist_load():
    query = """
    SELECT 
        p.specialty,
        COUNT(a.appointment_id) as total_appointments,
        AVG(p.satisfaction_score) as avg_satisfaction
    FROM psychologists p
    LEFT JOIN appointments a ON p.psychologist_id = a.psychologist_id
    GROUP BY p.specialty
    ORDER BY total_appointments DESC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_appointment_status():
    query = """
    SELECT status, COUNT(*) as count
    FROM appointments
    GROUP BY status;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_heatmap_data():
    query = """
    SELECT 
        strftime('%w', appointment_datetime) as day_of_week_num,
        CASE CAST(strftime('%w', appointment_datetime) AS INTEGER)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END as day_of_week,
        strftime('%H', appointment_datetime) as hour_of_day,
        COUNT(appointment_id) as appointment_count
    FROM appointments
    WHERE appointment_datetime IS NOT NULL
    GROUP BY day_of_week_num, day_of_week, hour_of_day
    ORDER BY day_of_week_num, hour_of_day;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def fetch_kpis():
    query_patients = "SELECT COUNT(*) as total FROM patients;"
    query_appts = "SELECT COUNT(*) as total FROM appointments WHERE attended = 1;"
    query_satisfaction = "SELECT AVG(satisfaction_level) as avg_sat FROM surveys;"

    with get_connection() as conn:
        total_p = pd.read_sql_query(query_patients, conn).iloc[0]["total"]
        total_a = pd.read_sql_query(query_appts, conn).iloc[0]["total"]
        avg_s = pd.read_sql_query(query_satisfaction, conn).iloc[0]["avg_sat"]

    return total_p, total_a, avg_s


def fetch_monthly_growth():
    query = """
    WITH MonthlyCounts AS (
        SELECT strftime('%Y-%m', registration_date) AS month, COUNT(patient_id) as new_patients
        FROM patients
        GROUP BY month
        ORDER BY month DESC
        LIMIT 2
    )
    SELECT * FROM MonthlyCounts ORDER BY month ASC;
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
        if len(df) == 2:
            prev = df.iloc[0]["new_patients"]
            curr = df.iloc[1]["new_patients"]
            growth = ((curr - prev) / prev) * 100 if prev > 0 else 0
            return growth
        return 0.0
