# app.py
import streamlit as st
from crud import fetch_jobs, post_job, apply_job
from database import get_connection

st.title("Job Vacancy Portal")

menu = st.sidebar.selectbox("Menu", ["View Jobs", "Post Job", "Apply"])

if menu == "View Jobs":
    jobs = get_all_jobs()
    st.table(jobs)

elif menu == "Post Job":
    # Placeholder for job posting form
    st.header("Post a New Job")
    st.write("Form to post a job will go here.")
    pass  # remove once form is implemented

elif menu == "Apply":
    st.header("Apply to a Job")
    st.write("Form to apply for a job will go here.")
    pass  # remove once apply form is implemented

