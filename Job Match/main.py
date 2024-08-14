import add_job as add
import data_manager as data
import search_jobs as search
import score_jobs as score
import urllib.parse
import io

from fastapi import FastAPI, File, UploadFile

jobDatabasePath = "./assets/data/raw_job_data.csv"

# Get the jobs data
jobsData = data.unpackRawJobData(jobDatabasePath)

# Get the job categories data(for optimization)
jobCategories = data.getSortedJobs()


app = FastAPI()

# Test function - echos what you say back
@app.post("/test/", status_code=201)
async def test(echoTest:str = "None inputted"):
    return {"Echo test": echoTest}


# Define the add_job function for the API
@app.post("/add_job/")
async def add_job(job_id: str, job_title: str, job_description: str):
    return add.add_job(jobDatabasePath=jobDatabasePath, job_id=job_id, job_title=job_title, job_description=job_description)


# Define the search job function for the API
# Takes in a resume and an optional limit for max jobs returned
# Resume text can either be the path to the pdf or simply just the resume text - if both, defaults to the pdf
@app.post("/search_job/")
async def search_job(resumePdfFile: UploadFile | None = None, resume_text:str | None = None, limit: int = 5):
    # Conv the pdf to text(if they submitted a pdf)
    if resumePdfFile != None:        
        resume_text = data.convPDFtoText(resumePdfFile.file.read())
    return search.searchJobs(resume_text, limit, jobCategories, jobsData) # type: ignore



"""
Reference grading scale:
Education Score (0-10)
						10: Candidate possesses an advanced degree (e.g., PhD, MD) directly relevant to the position.
						5: Candidate holds a bachelor's degree in a related field.
						0: Candidate lacks any formal education or equivalent qualifications.
						Skill Score (0-10)
						10: Candidate possesses an exceptional level of proficiency in all required skills.
						5: Candidate has basic proficiency in required skills, but may need additional training or development.
						0: Candidate possesses few or no relevant skills.
						Experience Score (0-10)
						10: Candidate has extensive, directly relevant experience in a similar role, demonstrating exceptional performance and achievements.
						5: Candidate has some experience in related fields, but may require additional on-the-job training.
						0: Candidate has no identifiable work experience.
"""
# Define the score_jobs function
# Returns the scoring of the resume's compatibility with the particular job with 3 different scoring cateogries: education, skills, experience
# Resume can either be the path to the pdf or simply just the resume text - if both, defaults to the resume_text
@app.post("/score_job/")
async def score_job(job_id: str, resumePdfFile: UploadFile | None = None, resume_text:str | None = None):
    if resumePdfFile != None:
        resume_text = data.convPDFtoText(resumePdfFile.file.read())
    jobSet = jobsData[job_id]
    return score.score_job(jobSet=jobSet, userResume=resume_text) # type: ignore
