import streamlit as st
import pandas as pd
import oracledb

# ---------------- Oracle Database Connection ----------------
def create_connection():
    try:
        connection = oracledb.connect(
            user="SYSTEM",
            password="SYSTEM",
            dsn="localhost:1521/XEPDB1"
        )
        return connection
    except Exception as e:
        st.error(f"Oracle Connection Error: {e}")
        return None

# ---------------- Fetch Data ----------------
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            return df
        finally:
            connection.close()
    return pd.DataFrame()


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="SecureCheck Police Dashboard", layout="wide")
st.title("🚔 SecureCheck: Police Check Post Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement ⚖️")

# ---------------- Show All Logs ----------------
st.header("📑 Police Logs Overview")
query = "SELECT * FROM TRAFFIC_POLICE"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

# ---------------- Metrics ----------------
st.header("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)

with col2:
    arrests = data[data['STOP_OUTCOME'].str.contains("arrest", case=False, na=False)].shape[0]
    st.metric("Total Arrests", arrests)

with col3:
    warnings = data[data['STOP_OUTCOME'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)

with col4:
    drug_related = data[data['DRUGS_RELATED_STOP'] == "1"].shape[0]
    st.metric("Drug Related Stops", drug_related)


# ---------------- QUERIES ----------------
st.header("🧠 QUERIES")

selected_query = st.selectbox("Select a Query to Run", [
    "1. Total Number of Police Stops",
    "2. Count of Stops by Violation Type",
    "3. Number of Arrests vs. Warnings",
    "4. Average Age of Drivers Stopped",
    "5. Count of Stops by Gender",
    "6. Stops by Race",
    "7. Most Frequent Stop Duration",
    "8. Stops by Year"
])


query_map = {
    "1. Total Number of Police Stops": "SELECT COUNT(*) AS TOTAL_STOPS FROM TRAFFIC_POLICE",
    "2. Count of Stops by Violation Type": "SELECT VIOLATION, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY VIOLATION",
    "3. Number of Arrests vs. Warnings": "SELECT STOP_OUTCOME, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY STOP_OUTCOME",
    "4. Average Age of Drivers Stopped": "SELECT AVG(TO_NUMBER(DRIVER_AGE)) AS AVERAGE_AGE FROM TRAFFIC_POLICE",
    "5. Count of Stops by Gender": "SELECT DRIVER_GENDER, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY DRIVER_GENDER",
    "6. Stops by Race": "SELECT DRIVER_RACE, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY DRIVER_RACE",
    "7. Most Frequent Stop Duration": "SELECT STOP_DURATION, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY STOP_DURATION ORDER BY COUNT DESC FETCH FIRST 1 ROWS ONLY",
    "8. Stops by Year": "SELECT SUBSTR(STOP_DATE,1,4) AS YEAR, COUNT(*) AS COUNT FROM TRAFFIC_POLICE GROUP BY SUBSTR(STOP_DATE,1,4)"
}

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    st.write(result)


# ------------------------------  
# POLICE LOG FORM + PREDICTION  
# ------------------------------
st.markdown("---")
st.header("🚓 Add Police Log & Predict Outcome")

with st.form("new_log_form"):

    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.selectbox("Driver Race", ["White", "Black", "Asian", "Hispanic", "Other"])
    violation = st.text_input("Violation")
    stop_outcome = st.text_input("Stop Outcome")
    search_conducted = st.selectbox("Search Conducted?", ["0", "1"])
    drugs_related_stop = st.selectbox("Drug Related Stop?", ["0", "1"])
    stop_duration = st.text_input("Stop Duration")
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")


if submitted:

    # simple rule engine
    if drugs_related_stop == "1":
        predicted_violation = "Drug Possession"
        predicted_outcome = "Arrest"
    elif search_conducted == "1":
        predicted_violation = "Suspicious Activity"
        predicted_outcome = "Citation"
    else:
        predicted_violation = "Speeding"
        predicted_outcome = "Warning"

    st.markdown(f"""
    ### 📝 Prediction Summary

    - **Predicted Violation:** {predicted_violation}  
    - **Predicted Outcome:** {predicted_outcome}  

    🚓 A **{driver_age}-year-old {driver_gender}** in **{country_name}**  
    was stopped at **{stop_time.strftime("%I:%M %p")} on {stop_date}**.

    - Search Conducted: {"Yes" if search_conducted=='1' else "No"}  
    - Drug Related Stop: {"Yes" if drugs_related_stop=='1' else "No"}  
    - Stop Duration: {stop_duration}  
    - Vehicle Number: {vehicle_number}  
    """)

