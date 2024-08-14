import json
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
import plotly.express as plot
import numpy
from utils.cloud_services import cloudServices
from pymilvus import MilvusClient


embed_text = cloudServices().embed_text


class DataManager():
    # Get the data jsonl file path from the user
    def __init__(self, normalDataPath:str, embedDataPath:str) -> None:
        self.normalDataPath = normalDataPath
        self.dataset = json.load(open(normalDataPath, "r", encoding="UTF-8"))
        self.embedDataPath = embedDataPath
        self.embedData = json.load(open(embedDataPath, "r", encoding="UTF-8"))

        # Milvus database - setup
        self.collectionName = "tax"
        # Get the database(if it exists)
        try:
            self.mil = MilvusClient("./assets/milvus_database/taxinfo.db")
        # If the database doesn't exist:
        except:
            vectorData = numpy.array(list(self.embedData.values()))

            # Create/get the database
            mil = MilvusClient("./assets/milvus_database/taxinfo.db")
            collectionName = "tax"

            # If the collection already exists, drop it
            if mil.has_collection(collectionName):
                mil.drop_collection(collectionName)

            # Create the new collection
            # Dimensions = the dimensions in one embedding for a particular sample; for azure embedding 3 small dimensions = 1536
            mil.create_collection(collection_name=collectionName, dimension=vectorData.shape[1])

            # Milvus database entry format: #{id:id, vector: vector, text:text} - for the ID number just use the of the value in the normal list 
            # Reformat out stuff to line up with that
            # Not putting in the text - id is enough to identify
            milDict = [{"id": i, "vector":vectorData[i]} for i in range(len(vectorData))]
            mil.insert(collectionName, milDict)
            # Integrate the milvus database into the class
            self.mil = mil



    # Show the data after fit transforming to t-SNE
    def visualizeData(self):
        data = self.embedData
        vectorData = numpy.array(list(data.values()))

        # Do dimensionality reduction first w/ Truncated SVD
        tsvd = TruncatedSVD(n_components=2)
        vectorData_tsvd = tsvd.fit_transform(vectorData)

        figtsvd = plot.scatter(x = vectorData_tsvd[:, 0], y = vectorData_tsvd[:, 1])
        
        
        # Initialize tsne and fit the data to tsne
        tsne = TSNE(n_components=2)
        vectorData_tsne = tsne.fit_transform(vectorData_tsvd)

        # Lower divergence means the data has more patterns that can be trained for more efficiency
        print(tsne.kl_divergence_)

        # Visualize it into a figure
        figtsne = plot.scatter(x = vectorData_tsne[:, 0], y = vectorData_tsne[:, 1])
        
        return figtsvd, figtsne
    

    def searchData(self, query:str, amount:int) -> list:
        mil = self.mil
        collectionName = self.collectionName

        # Embed_text function was declared way above, might need to rerun that cell in order to have it be effective here
        milResults = mil.search(collection_name=collectionName, data=[embed_text(query)], limit=amount)

        # Get the results in the database for the ones given by Milvus
        results = [list(self.dataset.keys())[dataDict["id"]] for dataDict in milResults[0]]

        # Reformat the results for easier use when showing to user
        results = [{"link":result, "content":self.dataset[result]} for result in results]

        return results
    

