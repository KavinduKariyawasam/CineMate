from langchain_neo4j import Neo4jGraph
import json
import os
from langchain_community.vectorstores import Neo4jVector
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm

with open('config.json') as f:
    config = json.load(f)

URI = config['NEO4J_URI']
USER = config['NEO4J_USER']
PASSWORD = config['NEO4J_PASSWORD']

graph = Neo4jGraph(url=URI, username=USER, password=PASSWORD)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

labels = {"Movie": ["title", "description", "released"], "Person": ["name"], "Genre": ["name"]}
# labels = {"Genre": ["name"]}

for label, properties in tqdm(labels.items()):
    vector_index = Neo4jVector.from_existing_graph(
        embeddings,
        url=URI,
        username=USER,
        password=PASSWORD,
        index_name=f"{label.lower()}_index",
        node_label=label,
        text_node_properties=properties,
        embedding_node_property='embedding',
    )