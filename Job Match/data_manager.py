import csv
import json
from openai import AzureOpenAI
import pymupdf
from dotenv import dotenv_values
# Initial declaration for client that's used to get
secrets = dotenv_values("../.env")

client = AzureOpenAI(azure_endpoint=secrets["AZURE_OPENAI_ENDPOINT"],  # type: ignore
					 api_version=secrets["AZURE_OPENAI_API_VERSION"],
					 api_key=secrets["AZURE_OPENAI_API_KEY"],
					 azure_deployment="gpt4o")


global categorizedDataPath
categorizedDataPath = "./assets/data/categorized_job_titles.jsonl"


# Turns the data in the csv file into the data that will be used inside our code
def unpackRawJobData(csvFilePath: str):
	# Put all the jobs into an array
	jobs = {}
	with open(csvFilePath, "r", encoding="UTF-8") as file:
		reader = csv.DictReader(file)
		for row in reader:
			# Remove the unecessary job data - only need ID, title, description
			jobs[row["Job ID"]] = {"Title": row["Title"],
								"Description": row["Description"]}
			
	return jobs


# Sorts job into categories for optimization for the code(should implement this as a database in the future for real optimization)
def sortJobIntoCategories(jobs) -> dict:
	# Generate the job categories to optimize search times
	instructionPrompt = [{"role": "system", "content": f"""You will be given a list of jobs - sort them into different job categories which you deem fit for the job. Do not sort the jobs into more than 8 categories
									   Under no circumstances should you make a separate category purely for Internships. DO NOT MAKE A SEPARATE CATEGORY FOR INTERNSHIPS.
									   Here are the jobs that you should sort: {jobs}""" + "\nYour return format for the sorted jobs inside their categories should be python dictionaries nested inside the main python dictionary(but return it in pure text and only in the format shown - you do not need to show it as code in python or anything - just give the dictionary in it's pure form). Under no circumstances should you add any other text other than the answer you should give. It should be in the format exacty like this: {'Job Category': {'Job Title': 'Job ID', 'Job Title': 'Job ID'}, 'Job Category': {'Job Title': 'Job ID', 'Job Title': 'Job ID'} }"}]

	global sortedJobs
	sortedJobs = client.chat.completions.create(
		# type: ignore
		model="gpt-4o", messages=instructionPrompt).choices[0].message.content #type: ignore
	# Convert the dictionary returned into an usable format(not string)
	exec(f"sortedJobs = {sortedJobs}", globals())

	# Save the sorted jobs
	with open(categorizedDataPath, "w", encoding="UTF-8") as file:
		json.dump(sortedJobs, file, ensure_ascii=False)

	return sortedJobs #type: ignore


# Function to just get the sorted data
def getSortedJobs():
	jobs_sorted = None

	with open(categorizedDataPath, "r", encoding="UTF-8") as file:
		jobs_sorted = json.load(file)
		
	return jobs_sorted


# Uses pymuPDF to convert text pdfs into text in python (will use to convert the candidate's resumes into text)
# Use .open since it's in binary, need to convert from binary data
def convPDFtoText(pdfFile):
	text = ""
	with pymupdf.open(stream=pdfFile, filetype="pdf") as doc:
		for pg in doc:
			text += pg.get_text() # type: ignore

	return text


