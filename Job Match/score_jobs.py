from openai import AzureOpenAI
from dotenv import dotenv_values

# Initial declaration for client that's used to get
secrets = dotenv_values("../.env")

client = AzureOpenAI(azure_endpoint=secrets["AZURE_OPENAI_ENDPOINT"],  # type: ignore
					 api_version=secrets["AZURE_OPENAI_API_VERSION"],
					 api_key=secrets["AZURE_OPENAI_API_KEY"],
					 azure_deployment="gpt4o")


def score_job(jobSet, userResume:str):
	instructionPrompt = [{"role":"system", "content": f"""You will be given a job and it's description along with a candidate's resume for the job. Your purpose is to score the candidate's compatibiility with the job and give out a score for the Education, Skills, and Experience categories. 
						Here is a grading scale that you can go off of for the scoring(keep in mind this is only something to go off of. Scoring requirements should not be the same for every job. Use your own judgement capabilities to score with this grading scale as a simple reference. For example, applying for a software tester job won't have as much educational requirements as applying for a data analyst job): 
						Grading Scale
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
						Here is the job to analyze: {jobSet}\nHere is the candidate's resume: {userResume}"""
						+ "Your return format should STRICTLY be in the format that will be shown. There should be no other text or reply except in this format for the scoring: {'Education': 5, 'Skills': 10, 'Experience': 9}"}]
	
	global scoreDict
	scoreDict = client.chat.completions.create(model="gpt-4o", messages=instructionPrompt).choices[0].message.content # type: ignore
	exec(f"scoreDict = {scoreDict}", globals())
	# Http code 200 - content successfully retrieved
	return {"status": 200, "message": f"Score evaluation with job({jobSet['Title']}) and resume was successful", "content": scoreDict}