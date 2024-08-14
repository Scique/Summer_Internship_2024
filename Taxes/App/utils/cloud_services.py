from langchain_openai import AzureOpenAIEmbeddings
from dotenv import dotenv_values
import json
from openai import AzureOpenAI
import csv
import datetime

class cloudServices:
    def __init__(self) -> None:
        # Configuration for Azure OpenAI
        self.secrets = dotenv_values("../../.env")
        # Initialize embedder
        self.embedder = AzureOpenAIEmbeddings(azure_deployment=self.secrets["OPENAI_EMBEDDINGS_DEPLOYMENT"],
                                            api_key=self.secrets["AZURE_OPENAI_API_KEY"], # type: ignore
                                            azure_endpoint=self.secrets["AZURE_OPENAI_ENDPOINT"])
        # Initialize Azure OpenAI client
        # Not using api ver and deployment from secrets since diff. one from the embeddings
        self.azureopenai_client = AzureOpenAI(azure_endpoint=self.secrets["AZURE_OPENAI_ENDPOINT"],  # type: ignore
            api_version="2024-02-01", 
            api_key=self.secrets["AZURE_OPENAI_API_KEY"],
            azure_deployment="gpt4o")


    # Plain embed text function from the embedder
    def embed_text(self, text:str) -> list:
        # Call the embed_query function from the obj
        return self.embedder.embed_query(text)
    

    # Made specifically for our use as it will tokenize each line from the data dict given(presumably will be the dataset of info we give)
    def embed_data(self, dataset:dict) -> None:
        # Embed the data
        embedData = {}
        for key in dataset.keys():
            embedData[key] = self.embed_text(dataset[key]["ข้อหารือ"].replace("\n", ""))
            
        print("Embedding finished - saving")

        # Save the embedded tax data
        with open("/mnt/c/Users/iqlin/OneDrive/Documents/IQ_internship-MFEC/Taxes/App/Assets/embeddings/embedtaxdata.jsonl", "w", encoding = "UTF-8") as file:
            json.dump(embedData, file, ensure_ascii=False)

        print("Embedded file saved")


    # Function to find the number of times that a letter appears in a word
    def findLetters(self, word:str, letter:str) -> str:
        # Make a list of the positions of the letters in the list
        letterPosition = []
        # Check for the appearances of that specific letter in the list
        for i in range(len(word)):
            if word[i] == letter:
                letterPosition.append(i)
        # Return the # of times the letter appears in the word in a pleasing format
        if len(letterPosition) > 1:
            newPos = ""
            for pos in letterPosition:
                newPos += (str(pos) + ", ")
            return f"The letter '{letter}' appears in the word '{word} {len(letterPosition)}' times at these index positions: {newPos[:-2]}."
        elif len(letterPosition) == 1:
            return f"The letter '{letter}' appears in the word '{word}' once at this index position: {letterPosition[0]}."
        else:
            return f"The letter '{letter}' does not appear in the word '{word}' at all. "
        

    # Function to save user feedback to the .csv feedback file. 
    def userFeedback(self, feedback:str):
        with open("./assets/userfeedback.csv", "a") as file:
            # Make the csv writer object and reader object w/ the csv module
            csvDictWriter = csv.DictWriter(file, fieldnames = ["date", "time", "feedback"])
            # Get the date and time of today to log into the user feedback module
            currentDT = datetime.datetime.now()
            # Write the dict containing the information about the feedback to the row. 
            csvDictWriter.writerow({"date": currentDT.date(), "time": currentDT.time(), "feedback": feedback})
        # Return the message to the user indicating that the feedback has been processed and saved
        return "Thank you for your feedback. It has been processed and saved. "


    # Gets the result for the user query with the RAG technique
    def rag_result(self, query:str, searchResults:list, chatHistory:list) -> list:
        # System messages to the AI so it knows what to do and to inform it of what functions to call. 
        systemQuery = [{"role": "system", "content": "You are a lawyer that accepts a query from the user along with some data which contains anwers for similar queries and answers to those queries to the one that the user inputted. The queries will be in an array with each entry being in the form of query:[answer, citation]. You will use that data given and make an educated guess on the correct answer to the user's query in one paragraph. Don't tell the user that you are making an educated guess. Provide an answer or recommendation for user to user query, along with some citations for information that you believe is relavant to the user's query and support your answer with evidence. "},
                        {"role": "system", "content": "If the user asks how many times a letter appears in a word, you do not need to use the data given to answer this question. Your answer back should ONLY be this function call in this format: CODEself.findLetters('word', 'letter')"}, 
                        {"role": "system", "content": "If the user seems like they are displeased with your answer or mad about it, ask the user if they would like to give feedback. If the user replies that they would like to give feedback on the next message, tell the user to type out the user feedback in their next response. After the user types out the feedback, your response back should ONLY be this function call in this format: CODEself.userFeedback('The feedback given by the user')"}]
        # Make sure the system message is inside the dataset for the AI to understand
        if len(chatHistory) == 0:
            chatHistory += systemQuery
        elif chatHistory[0]["role"] != "system":
            chatHistory = systemQuery + chatHistory
            chatHistory.insert(0, systemQuery)
        # Add the user's new message(in the right format) to the chat history
        chatHistory += [{"role": "user", "content": f"User query: {query}\n\nSimilar queries and answers: { {result['content']['ข้อหารือ']:[result['content']['แนววินิจฉัย'], 'เลขที่หนังสือ: ' + result['content']['เลขที่หนังสือ']] for result in searchResults} }"}]
        # After the chat history w/ user's message, add it to the logs
        with open("./assets/chatLog.csv", "a") as file:
            # Create the object
            csvDictWriter = csv.DictWriter(file, fieldnames = ["date", "time"] + list(chatHistory[0].keys()))
            # Write the last two messages to the log - don't need to include the long message that will be sent to the model, only the user query
            message = {"role": "user", "content": query}
            message.update({"date": str(datetime.datetime.now().date()), "time": str(datetime.datetime.now().time())})
            csvDictWriter.writerow(message)
        # Generate the model's response to the user's prompt and save it to the chat history
        chatHistory += [{"role":"assistant", "content": self.azureopenai_client.chat.completions.create(model="gpt-4o", messages = chatHistory).choices[0].message.content}]

        # Check if the answer is a call to another function
        # GPT was instructed to put CODE in front of the function call if it wished to call a function
        if chatHistory[-1]["content"][:4] == "CODE":
            # Will run the content that is returned by GPT - should be a call to a function which will return the right answer. 
            # Will change the content of GPT's latest message to the function's return value
            exec(f"chatHistory[-1]['content'] = {chatHistory[-1]['content'][4:]}", locals())

        # After the chat history of the model is finally updated to what it should be, add it to the logs
        with open("./assets/chatLog.csv", "a") as file:
            # Create the object
            csvDictWriter = csv.DictWriter(file, fieldnames = ["date", "time"] + list(chatHistory[0].keys()))
            # Write the last two messages to the log
            message = chatHistory[-1]
            message.update({"date": str(datetime.datetime.now().date()), "time": str(datetime.datetime.now().time())})
            csvDictWriter.writerow(message)


        # Return the updated chatHistory - answer will be in the latest index of chatHistory
        return chatHistory

