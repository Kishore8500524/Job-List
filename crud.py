import pandas as pd
from sqlalchemy import text

# Correct function name to match import in Job_Portal.py
def get_all_jobs(engine):
    return pd.read_sql("SELECT * FROM Jobs", engine)

def post_job(engine, title, company, location, description):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO Jobs (Title, Company, Location, Description) VALUES (:title, :company, :location, :desc)"),
            {"title": title, "company": company, "location": location, "desc": description}
        )

# Correct name to match 'apply_to_job' import
def apply_to_job(engine, job_id, applicant_name, email, resume):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO Applications (JobID, ApplicantName, Email, ResumeText) VALUES (:job_id, :name, :email, :resume)"),
            {"job_id": job_id, "name": applicant_name, "email": email, "resume": resume}
        )
