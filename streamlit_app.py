import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit_authenticator as stauth
import yaml
import os
from io import StringIO
import base64

# Load secrets
signing_key = st.secrets["COOKIE_SIGNING_KEY"]
config = yaml.safe_load(st.secrets["CONFIG_YAML"])

authenticator = stauth.Authenticate(
    config['credentials'],
    "exotel_cookie",
    signing_key,
    cookie_expiry_days=1
)

authenticator.login(location='main')

if st.session_state.get("authentication_status"):
    st.sidebar.success(f"Welcome {st.session_state['name']} 👋")
    authenticator.logout(location='sidebar')
    st.title("📞 Exotel Status Dashboard")

    upload_dir = "uploaded_data"
    os.makedirs(upload_dir, exist_ok=True)

    uploaded_files = st.file_uploader("Upload multiple CSV files", type="csv", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success("Files uploaded and saved.")
        st.rerun()

    saved_files = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith(".csv")]
    df_list = []
    for file_path in saved_files:
        try:
            df_list.append(pd.read_csv(file_path))
        except pd.errors.EmptyDataError:
            st.warning(f"Skipped empty file: {file_path}")

    if df_list:
        df = pd.concat(df_list, ignore_index=True)

        if "StartTime" in df.columns:
            df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
            df["Date"] = df["StartTime"].dt.date
            df["DayOfWeek"] = df["StartTime"].dt.day_name()
        if "DisconnectedBy" in df.columns:
            df["DisconnectedBy"] = df["DisconnectedBy"].fillna("Unspecified")

        view_option = st.radio("Choose View Mode:", ["All Data (Weekly)", "Filter by Date"])

        if "Date" in df.columns:
            df["Year"] = pd.to_datetime(df["Date"]).dt.isocalendar().year
            df["Week"] = pd.to_datetime(df["Date"]).dt.isocalendar().week
            df["YearWeek"] = df["Year"].astype(str) + "-W" + df["Week"].astype(str).str.zfill(2)

            if view_option == "Filter by Date":
                selected_date = st.date_input("Select a date", df["Date"].min())
                filtered_df = df[df["Date"] == selected_date]
            else:
                week_options = sorted(df["YearWeek"].unique(), reverse=True)
                selected_week = st.selectbox("Select a week", week_options)
                filtered_df = df[df["YearWeek"] == selected_week]
        else:
            st.warning("No 'Date' column found.")
            filtered_df = df

        # Export option
        csv_data = filtered_df.to_csv(index=False)
        b64 = base64.b64encode(csv_data.encode()).decode()
        st.download_button(
            label="🔍 Export filtered data to CSV",
            data=csv_data,
            file_name="filtered_exotel_data.csv",
            mime="text/csv"
        )

        # Summary Metrics
        st.subheader("📈 Call Summary")
        total_calls = len(filtered_df)
        answered = (filtered_df["Leg1Status"] == "completed").sum() if "Leg1Status" in filtered_df.columns else 0
        missed = (filtered_df["Leg1Status"] != "completed").sum() if "Leg1Status" in filtered_df.columns else 0
        total_duration = filtered_df["ConversationDuration"].sum() if "ConversationDuration" in filtered_df.columns else 0
        avg_duration = filtered_df["ConversationDuration"].mean() if "ConversationDuration" in filtered_df.columns else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Calls", total_calls)
        col2.metric("Answered by Volunteer", answered)
        col3.metric("Missed Calls", missed)

        col4, col5 = st.columns(2)
        col4.metric("Total Duration (s)", f"{total_duration:.0f}")
        col5.metric("Avg Duration (s)", f"{avg_duration:.1f}")

        # Call Status Distribution
        st.subheader("📊 Call Status Distribution")
        if "Status" in filtered_df.columns:
            status_counts = filtered_df["Status"].value_counts()
            st.bar_chart(status_counts)

            fig, ax = plt.subplots()
            ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        # Stacked Bar Chart
        st.subheader("📊 Volunteer-wise Call Status (Stacked Bar)")
        if "ToName" in filtered_df.columns and "Status" in filtered_df.columns:
            status_by_vol = filtered_df.groupby(["ToName", "Status"]).size().unstack(fill_value=0)
            st.bar_chart(status_by_vol)

        # Heatmap
        st.subheader("🌡️ Call Heatmap by Day")
        if "DayOfWeek" in filtered_df.columns and "Status" in filtered_df.columns:
            heatmap_data = filtered_df.groupby(["DayOfWeek", "Status"]).size().unstack(fill_value=0)
            heatmap_data = heatmap_data.reindex([
                "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
            st.pyplot(fig)

        # Completed Leaderboard
        st.subheader("🏆 Completed Calls Leaderboard")
        if "Status" in filtered_df.columns and "ToName" in filtered_df.columns:
            leaderboard = (
                filtered_df[filtered_df["Status"] == "completed"]
                .groupby("ToName").size()
                .sort_values(ascending=False).reset_index(name="Completed Calls")
            )
            query = st.text_input("Search volunteer name", placeholder="Enter a name")
            if query:
                leaderboard = leaderboard[leaderboard["ToName"].str.contains(query, case=False, na=False)]
            leaderboard.index += 1
            st.dataframe(leaderboard, use_container_width=True)

        # Missed Leaderboard
        st.subheader("📉 Missed Calls Leaderboard")
        if "Status" in filtered_df.columns and "ToName" in filtered_df.columns:
            missed = (
                filtered_df[filtered_df["Status"] == "missed-call"]
                .groupby("ToName").size()
                .sort_values(ascending=False).reset_index(name="Missed Calls")
            )
            missed.index += 1
            st.dataframe(missed, use_container_width=True)

    else:
        st.warning("No valid data found in uploaded CSVs.")

    # Clear Uploaded Files
    if st.button("❌ Clear All Uploaded Files"):
        for f in saved_files:
            os.remove(f)
        st.success("All uploaded files removed.")
        st.rerun()

else:
    st.error("Please login to access the dashboard.")
