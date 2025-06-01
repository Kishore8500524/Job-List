# app.py
import streamlit as st
from crud import get_all_jobs, apply_to_job
from database import get_connection

st.title("Job Vacancy Portal")

menu = st.sidebar.selectbox("Menu", ["View Jobs", "Post Job", "Apply"])

if menu == "View Jobs":
    jobs = get_all_jobs()
    st.table(jobs)

elif menu == "Post Job":
    # form to enter job details and submit

elif menu == "Apply":
    # list jobs and apply form
