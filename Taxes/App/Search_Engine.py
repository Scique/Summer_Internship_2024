import streamlit as sl

# Make this file's own required instances
from utils.dataManager import DataManager
datamanager = DataManager("./assets/dataset/taxdata.jsonl", "./assets/embeddings/embedtaxdata.jsonl")

# Calls this function when the user searches from the search query
def search():
    # Returns the results for the userInput
    # Change the amount number depending on how it is(might add user functionality for this later)
    results = datamanager.searchData(userInput, 20)

    # Results container
    with resultsContainer:
        # Only show the results if the results have been fetched
        if results != None:
            sl.header("Results: ")
            # Iterate through te results given and show to the user
            for i in range(len(results)):
                link = results[i]["link"]
                content = results[i]["content"]
                with sl.container(border=True):
                    # Format the title of the markdown
                    sl.write(f"{i+1}. [**เรื่อง:** {content['เรื่อง']}]({link})")
                    for category in list(content.keys()):
                        with sl.container(border=True):
                            if category != "เรื่อง":
                                sl.markdown(f"**{category}**: {content[category]}")


sl.title("Search From Tax Data")
# Searchbox container
searchContainer = sl.container()
# Results container
resultsContainer = sl.container()
# Search box input element
userInput = searchContainer.text_input(label="Tax Database Search", key="search-input", on_change=search)