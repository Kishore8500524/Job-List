import pandas as pd
from sqlalchemy import text

def get_all_jobs(engine):
    """Fetch all job listings from the Jobs table."""
    return pd.read_sql("SELECT * FROM Jobs", engine)

def post_job(engine, title, company, location, description):
    """Insert a new job into the Jobs table."""
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO Jobs (Title, Company, Location, Description) VALUES (:title, :company, :location, :desc)"),
            {"title": title, "company": company, "location": location, "desc": description}
        )

def apply_to_job(engine, job_id, applicant_name, email, resume):
    """Insert an application into the Applications table."""
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO Applications (JobID, ApplicantName, Email, ResumeText) VALUES (:job_id, :name, :email, :resume)"),
            {"job_id": job_id, "name": applicant_name, "email": email, "resume": resume}
        )
