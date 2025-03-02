from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import json
from langchain.prompts import PromptTemplate
from collections import deque

with open("config.json", "r") as file:
    config = json.load(file)
    
URI = config["NEO4J_URI"]
USER = config["NEO4J_USER"]
PASSWORD = config["NEO4J_PASSWORD"]
GROQ_API = config["GROQ_API"]

graph = Neo4jGraph(url=URI, username=USER, password=PASSWORD)

llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API,
    model_name="llama3-70b-8192",
    timeout=None
    )

cypher_llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API,
    model_name="llama-3.3-70b-versatile",
    timeout=None
    )

custom_cypher_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a Cypher query generator for our graph database. When converting a natural language question into a Cypher query, ensure that any properties or nodes returned are assigned meaningful aliases. For instance, when returning a director's name, do not use the raw property name (e.g., 'p.name') in the output; instead, alias it as 'director'.

if it is only a greeting, please respond with "Hello! How can I assist you today?"

Question: {question}

Cypher Query:
"""
)

custom_qa_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are a knowledgeable assistant tasked with providing a concise answer based on the information retrieved from our graph database.
Below are some examples to illustrate the expected format:

Example 1:
Question: Who directed the movie "Inception"?
Retrieved Information: "Inception" was directed by Christopher Nolan.
Answer: "Inception" was directed by Christopher Nolan.

Example 2:
Question: What is "The Matrix" about?
Retrieved Information: "The Matrix" is a science fiction action film that depicts a dystopian future.
Answer: "The Matrix" is a science fiction action film that depicts a dystopian future.

Now, based on the following, provide your answer. Be friendly and concise.

if it is only a greeting, please respond with "Hello! How can I assist you today?"

Question: {question}

Retrieved Information: {context}

Answer:
"""
)

chain = GraphCypherQAChain.from_llm(
    qa_llm=llm,
    cypher_llm=cypher_llm,
    graph=graph,
    qa_prompt=custom_qa_prompt,
    # cypher_prompt=custom_cypher_prompt,  
    verbose=True,
    allow_dangerous_requests=True,
    return_intermediate_results=True
)

chat_history = deque(maxlen=5)  

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        break

    greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up"}
    if user_input.lower() in greetings:
        print("Bot: Hello! How can I assist you today?")
        continue  

    history_text = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in chat_history])

    modified_query = f"Conversation history:\n{history_text}\nCurrent question: {user_input}"

    result = chain.invoke({"query": modified_query})
    bot_response = result["result"]

    chat_history.append({"user": user_input, "bot": bot_response})

    print("Bot:", bot_response)
    print("\n")
