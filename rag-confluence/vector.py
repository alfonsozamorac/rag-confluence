from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from parser import get_chunks
from utils import get_property
from constants import questions, model
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains import RetrievalQA
import time
from math import trunc


def question_vector(docs):
    vector_index = Neo4jVector.from_documents(
        docs,
        VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=get_property("project_gcp"),
            location="europe-west4"
        ),
        url=get_property("neo4j_host"),
        username=get_property("neo4j_user"),
        password=get_property("neo4j_psswd"),
        database=get_property("neo4j_database")
    )
    vector_qa = RetrievalQA.from_chain_type(
        llm=ChatVertexAI(
            model_name=model,
            temperature=0,
            convert_system_message_to_human=True),
        chain_type="stuff",
        retriever=vector_index.as_retriever())

    for question in questions:
        response = vector_qa.invoke(question)
        print(response["query"])
        print(response["result"])


def main():
    start_time = time.time()
    docs = get_chunks()
    question_vector(docs)
    end_time = time.time()
    runtime = (end_time - start_time) / 60
    print("RUNTIME:", trunc(runtime), "minutes")


if __name__ == "__main__":
    main()
