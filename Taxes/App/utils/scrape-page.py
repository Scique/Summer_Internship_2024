import urllib.request
from bs4 import BeautifulSoup
from time import sleep

# Make a global variable weburl in case we want to use it elsewhere
global weburl
weburl = "https://www.rd.go.th/"

def removeSpecialChar(text):
    return text.replace(" &nbsp;", "").replace("\xa0", "").replace(":", "").replace("\t", "").replace("\r", "").strip()


# Scrape off the directory on the left side of the page to get each page off of the website
# Url can be any URL on the tax page
# Get year
def directoryScrape(url):
    # Get the website data and decode
    web = urllib.request.urlopen(url)
    data = web.read()
    decoded_data = data.decode("utf-8")

    # Use beautiful soup to analyze/scrape
    soup = BeautifulSoup(decoded_data, "html.parser")   

    # Get the table element that contains the data we want - get the children into a separate variable
    div = soup.find("div", {"class": "list-menu xs-toggle-content"})

    # Last one is not a link to the tax data
    yearLinks = [weburl + list(child.children)[0]["href"].replace("http://www.rd.go.th/", "") for child in div.contents[1].children][:-1]
    return yearLinks

# Get month
def subDirectory(yearLink):
    # Get the website data and decode
    web = urllib.request.urlopen(yearLink)
    data = web.read()
    decoded_data = data.decode("utf-8")

    # Use beautiful soup to analyze/scrape
    soup = BeautifulSoup(decoded_data, "html.parser")

    # Month table
    div = soup.find("div", {"class": "submenu"})
    # monthsList = [list(element.children)[0]["href"] for element in child.contents for child in div.children]
    monthsList = []
    for child in div.children:
        for element in child.contents:
            monthsList.append(weburl + list(element.children)[0]["href"].replace("http://www.rd.go.th/", ""))
            sleep(1)
    
    return monthsList

# Get article
def articleDirectory(monthLink):
    # Get the website data and decode
    web = urllib.request.urlopen(monthLink)
    data = web.read()
    decoded_data = data.decode("utf-8")

    # Use beautiful soup to analyze/scrape
    soup = BeautifulSoup(decoded_data, "html.parser")

    # Get the articles table - skip to tbody
    # Some articles can't find tbody forsome reason so instead of that find them by using the a attributes of them
    try:
        tbody = soup.find("tbody")
        articles = [weburl + child.contents[1].contents[1]["href"].replace("http://www.rd.go.th/", "") for child in list(tbody.contents)[1::2]]
    except:
        links = soup.find_all("a", {"target":"_self", "class":"style9"})
        # Fix issue where some sites contain just the ./ link while some contain the entire link
        articles = [weburl + link["href"].replace("http://www.rd.go.th/", "") for link in links if not "".join(link.contents[0]).isnumeric()]
    
    return articles



# Will scrape the article fed in and return the data fed in as a list
def scrapePage(page):
    # Get the website data and decode
    web = urllib.request.urlopen(page)
    data = web.read()
    decoded_data = data.decode("utf-8")

    # Use beautiful soup to analyze/scrape
    soup = BeautifulSoup(decoded_data, "html.parser")   

    # Get the table element that contains the data we want - get the children into a separate variable
    taxInfoTable = soup.find("table")
    # Solving problem with different formatting - later articles format with tbody as the container, some older don't contain tbody
    tbody = taxInfoTable.tbody
    if taxInfoTable.tbody == None:
        tbody = taxInfoTable

    # Put content/string of the children all into a list
    # Clean the data too
    data = []
    for tr in tbody:
        tr = tr.contents
        # Removing any line breaks
        tr = [tr[i] for i in range(len(tr)) if tr[i].name != "br"] 
        # If the length is > 1, that means that tr1 contains a string that is split into multiple elements but should be one
        # Combine these strings to get the appropriate function of the text
        if len(tr) > 1 and type(tr[0]) == str:
            paragraph = ""
            for text in tr:
                paragraph += text.get_text()
            data.append(removeSpecialChar(paragraph))
        else:
            for child in tr:
                # If it's a comment it will appear as a string and we don't want comments in the dataset - comments will appear as a 1 character string
                if type(child) != str:
                    # Some times the text comes in separate elements
                    # If not then that means it's a table so it goes into the exception
                    try:
                        data.append(removeSpecialChar(child.get_text()))
                    except AttributeError:
                        # Format the table into a format that can be exported to json properly and can be used to train a model
                        part = []
                        for element in child:
                            if element.name == None:
                                part.append(removeSpecialChar(element))
                            elif element.name == "table":
                                # The first TR will be the tags so put the tags into a variable
                                tags = [category.get_text() for category in element.tbody.contents[0]]
                                table = []
                                # Loop through elements 1 to 4 in the list and get the text for them
                                for i in range(1, len(element.tbody)):
                                    tr = element.tbody.contents[i]
                                    # Don't need the summary of it inside the dataset since that value can simply be calculated with the data
                                    if tr.contents[0].get_text() != "รวม":
                                        # Build the dictionary that contains the tag as the key and the contents is the tr element of the table inside it
                                        content = {tag:removeSpecialChar(tr.contents[tags.index(tag)].get_text()) for tag in tags}
                                        table.append(content)
                                part.append(table)
                        # Append it to the list
                        data.append(part)

    # Format that list into a dictionary with value and key
    dataDict = {}
    for i in range(0, len(data)-1, 2):
        # Don't add it if it has the "เลขตู้" tag since the newer ones don't have it 
        if data[i] != "เลขตู้": 
            dataDict[data[i]] = data[i+1]
    
    # Scrapped idea for format the ข้อกฎหมาย into a list - does not work consistently
    """
    # Properly format the ข้อกฎหมาย into a list if it contains the numeric characters
    citations = dataDict["ข้อกฎหมาย"]
    onlyChar = True
    for char in citations:
        if char.isnumeric():
            onlyChar = False
    if not onlyChar:
        # If the ascii is greater than 57, it is neither an integer nor a "(", ")", or "/" so therefore it is a Thai character and we can remove it
        citations = [part for part in "".join([citations[i] for i in range(len(citations)) if (not ord(citations[i]) > 57)]).strip().split(" ") if len(part) != 0]
        print(citations)
        toRemove = [citations[i-1]+citations[i] for i in range(len(citations)) if "(" in citations[i] or "(" in citations[i] and citations[i + 1] == ")"]
        print(toRemove)
        dataDict["ข้อกฎหมาย"] = [citation for citation in citations if citation not in toRemove]
    """
    # Return the dictionary
    return(dataDict)


test = scrapePage("https://www.rd.go.th//66911.html")
print(len(test.keys()))

for part in test.keys():
    print(f"{part}:\n{test[part]}\n\n\n")

# URL here can be any page that on the tax that has the directory on the left side fo the years and month


from tqdm import tqdm
import json

# Declare all the variables needed
yearPages = directoryScrape("https://www.rd.go.th/66091.html")
# Adjust yearPages to compensate for any years already done:
yearPages = yearPages[22:]

totalData = {}
# check to see if any of the articles we are about to process is already inside the data
with open("./taxdata.jsonl", "r", encoding="UTF-8") as file:
    try:
        totalData = json.load(file)
    except:
        pass


# Start the scraping loop from where we last left off
for year in tqdm(yearPages):
    print(f"Year: {year}")
    monthsList = subDirectory(year)
    for month in monthsList:
        print(f"Month: {month}")
        articleList = articleDirectory(month)
        # Update the article list for already used keys
        articleList = [article for article in articleList if article not in list(totalData.keys())]
        sleep(1)
        for article in articleList:
            print(f"Article: {article}")
            try:
                data = scrapePage(article)
                if len(data.keys()) == 6:
                    print(data)
                    totalData[article] = data
                    # Add the new data to the end
                    with open("./taxdata.jsonl", "w", encoding="UTF-8") as file:
                        json.dump(totalData, file, ensure_ascii=False)
                else:
                    print("Article format invalid - will not add")
            except Exception as e:
                print(f"Article unable to be scraped - {e}")
            finally:
                sleep(2)