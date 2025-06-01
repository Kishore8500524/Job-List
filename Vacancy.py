import streamlit as st
from database import create_connection
from crud import fetch_jobs, post_job, apply_job

st.title("Job Vacancy Portal")

with st.sidebar:
    st.header("DB Connection")
    server = st.text_input("Server")
    database = st.text_input("Database")
    if st.button("Connect"):
        try:
            st.session_state.engine = create_connection(server, database)
            st.success("Connected successfully!")
        except Exception as e:
            st.error(f"Connection failed: {e}")

menu = st.sidebar.selectbox("Menu", ["View Jobs", "Post Job", "Apply"])

if 'engine' not in st.session_state:
    st.warning("Please connect to the database first.")
else:
    engine = st.session_state.engine

    if menu == "View Jobs":
        st.subheader("Available Jobs")
        jobs_df = fetch_jobs(engine)
        st.dataframe(jobs_df)

    elif menu == "Post Job":
        st.subheader("Post a New Job")
        title = st.text_input("Job Title")
        company = st.text_input("Company")
        location = st.text_input("Location")
        description = st.text_area("Job Description")
        if st.button("Submit Job"):
            post_job(engine, title, company, location, description)
            st.success("Job posted successfully!")

    elif menu == "Apply":
        st.subheader("Apply for a Job")
        jobs_df = fetch_jobs(engine)
        job_id = st.selectbox("Select Job", jobs_df['JobID'])
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        resume = st.text_area("Paste Resume")
        if st.button("Apply"):
            apply_job(engine, job_id, name, email, resume)
            st.success("Application submitted!")