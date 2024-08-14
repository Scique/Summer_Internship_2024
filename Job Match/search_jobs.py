from openai import AzureOpenAI
from dotenv import dotenv_values

# Initial declaration for client that's used to get
secrets = dotenv_values("../.env")

client = AzureOpenAI(azure_endpoint=secrets["AZURE_OPENAI_ENDPOINT"],  # type: ignore
					 api_version=secrets["AZURE_OPENAI_API_VERSION"],
					 api_key=secrets["AZURE_OPENAI_API_KEY"],
					 azure_deployment="gpt4o")


# Search jobs - receives parameters: resume of the user you would like to search, the maximum number of results you would like to receive, sortedJobs(used for optimization since it's essentially the jobs sorted into different categories), dictionary of jobs
def searchJobs(userResume: str, maxResults: int, sortedJobs, jobs) -> dict:
	# Get the resume, and find the appropriate job categories from the list of job categories
	instructionPrompt = [{"role": "system", "content": "You will be given job categories and a resume. Find the job categories which are most compatible for the resume given. Under no circumstances should you return no job categories or categories which are not in the job cateogories provided. Return ONLY the suitable job categories in this example format: ['Engineering', 'System Informations', 'Psychology']. Do not return any other text except that. " +
						  f"""Here is the resume: \n{userResume}Here are the job categories: \n{list(sortedJobs.keys())}"""}]
	global chosenCategories
	chosenCategories = client.chat.completions.create(
		# type: ignore
		model="gpt-4o", messages=instructionPrompt).choices[0].message.content # type: ignore
	exec(f"chosenCategories = {chosenCategories}", globals())
	# Return all the jobs in the requested categories
	# sortedJobs.values = all {job title: job ID} values
	# Make a dictionary of all the jobs that are part of the chosen categories(combined)
	chosenJobs = {}
	for category in chosenCategories: # type: ignore
		for jobTitle in sortedJobs[category]:
			jobID = sortedJobs[category][jobTitle]
			chosenJobs[jobID] = {"Title": jobTitle,
								 "Description": jobs[jobID]["Description"]}
			
	print("\n\n", chosenCategories)

	instructionPrompt = [{"role": "system", "content": f"""Your job is to choose the most compatible jobs inside a provided list of jobs(and job descriptions for that job) based on a candidate's resume that is given.
											Keep in mind that the 'Special assignment' descriptor inside the job descriptions indicate that it is a high level job. You should only recommend high level positions if the candidate is qualified and has a lot of experience.
											Here is the candidate's resume: \n{userResume}
											\nPlease return the top {maxResults} jobs which suit the candidate the best. \n"""+"Here is a dictionary of jobs inside the categories that suits the user's resume(Each set in the dictionary is in this format - Job ID: {'Title': Job title, 'Description': Job Description): \n" + f"{chosenJobs}\n" + "Your return message to the user should follow EXACTLY in format that will be described. It will be in the form of Python dictionaries nested in the Python list datatype in which you only need to return the Job ID and the Job Title inside each of the dictionaries. Your return should NOT be in Python code. It should strictly be in the text format. Here is an example for the return format. [{'Job ID': Job ID, 'Job Title': Job Title} , {'Job ID': Job ID, 'Job Title': Job Title}]"}]

	global selectedJobs
	selectedJobs = client.chat.completions.create(
		# type: ignore
		model="gpt-4o", messages=instructionPrompt).choices[0].message.content # type: ignore
	print(f"\n\n{selectedJobs}")
	exec(f"selectedJobs = {selectedJobs}", globals())

	if len(selectedJobs) != 0: # type: ignore
		return {"status": 200, "message": "Matching jobs successfully found", "content": selectedJobs}
	else:
		return {"status": 204, "message": "No matching jobs found", "content": selectedJobs}

