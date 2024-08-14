import streamlit as sl

# Make this file's own required instances
from utils.dataManager import DataManager
datamanager = DataManager("./assets/dataset/taxdata.jsonl", "./assets/embeddings/embedtaxdata.jsonl")

# Get the chart Figure objects
tsvd, tsne = datamanager.visualizeData()

# Show them up on the site
sl.title("Data Visualization")

tsnetab, tsvdtab = sl.tabs(["t-SNE Data Fitting", "t-SVD Data Dimension Reduction"])

with tsnetab:
    sl.header("t-SNE Data Fitting")
    sl.text("Patterns inside the tax data used")
    sl.plotly_chart(tsne)

with tsvdtab:
    sl.header("t-SVD Data Dimension Reduction")
    sl.text("Done before fitting data with t-SNE as per documentation")
    sl.plotly_chart(tsvd)
