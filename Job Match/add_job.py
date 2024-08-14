import csv
from data_manager import sortJobIntoCategories

def add_job(jobDatabasePath:str, job_id:str, job_title:str, job_description:str) -> dict:
	jobDatabase = {}
	# Get the jobs
	with open(jobDatabasePath, "r", encoding="UTF-8") as file:
		reader = csv.DictReader(file)
		for row in reader:
			# Remove the unecessary job data - only need ID, title, description
			jobDatabase[row["Job ID"]] = {"Title": row["Title"], "Description": row["Description"]}
		
    # check if the job already exists in the database(based off of job_id and job name)
	jobTitles = [value["Title"] for value in jobDatabase.values()]
	if (job_id in jobDatabase) or (job_title in jobTitles):
		# Http status code 409 - conflict since the job position already exists
		return {"status": 409, "message": "Conflict since the job position already exists"}
	
	# Add the new job into the database
	with open(jobDatabasePath, "a", encoding="UTF-8") as file:
		writer = csv.DictWriter(file, fieldnames=["Job ID", "Title", "Description"])
		writer.writerow({"Job ID": job_id, "Title": job_title, "Description": job_description})

	# DO NOT run this for test cases
	# Re-optimize the database to incorporate new data(splits the database into groups)
	# More efficient way to do this would just be to add it into the correct place in the same json file, but this is just a demo so to save coding time, we will just re-generate the optimizer file
	sortJobIntoCategories(jobs=jobDatabase)

	# Return indicating a successful adding of the jobs
	# Http code 201 - created successfully
	return {"status": 409, "message": "New job added successfully"}