from typing import Any, List, Optional
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.pydantic_v1 import BaseModel
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from parser import get_chunks
from utils import get_property
from constants import questions, prompt_cypher, system_prompt, human_prompt, model
from neo4j import GraphDatabase
import time
import inflect
from math import trunc

default_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt,
        ),
        (
            "human", human_prompt,
        ),
    ]
)


def get_schema() -> Any:
    class CustomNode(BaseModel):
        id: str = Field(
            description="Name or human-readable unique identifier of the node.")
        type: str = Field(description="The type or label of the node.")
        text: Optional[str] = Field(
            description="The text source from the document entry used to create the node. This is the most important field for each node to generate context.",
            default=None)

    class CustomRelationship(BaseModel):
        start_node_id: str = Field(description="ID of the start node.")
        end_node_id: str = Field(description="ID of the end node.")
        type: str = Field(description="The type of the relationship.")

    class CustomGraph(BaseModel):
        nodes: Optional[List[CustomNode]] = Field(
            description="List of nodes that have to match with the id of the nodes in field relationships ", default=[])
        relationships: Optional[List[CustomRelationship]] = Field(
            description="List of relationships", default=[]
        )

    return CustomGraph


def normalize_id(node_id):
    p = inflect.engine()
    lower = node_id.lower()
    singular_id = p.singular_noun(lower)
    return singular_id if singular_id else lower


def convert_node(node: Any, metadata: Any) -> Node:
    metadata["text"] = node.text
    return Node(id=normalize_id(node.id.title()), properties=metadata)


def convert_relationship(rel: Any, nodes_map: dict) -> Relationship:
    """Map the SimpleRelationship to the base Relationship using a map of node IDs to nodes."""
    source_node = nodes_map.get(normalize_id(rel.start_node_id))
    target_node = nodes_map.get(normalize_id(rel.end_node_id))
    if not source_node or not target_node:
        raise ValueError("Start or end node not found in the node map")
    return Relationship(
        source=source_node,
        target=target_node,
        type=rel.type.replace(
            " ",
            "_").upper())


def process_document(chain, doc: Document):
    llm_output = chain.invoke(
        {"input": doc.page_content, "metadata": doc.metadata})

    nodes = (
        [convert_node(node, doc.metadata) for node in llm_output.nodes]
        if llm_output and llm_output.nodes
        else []
    )

    nodes_map = {node.id: node for node in nodes}

    relationships = (
        [convert_relationship(rel, nodes_map) for rel in llm_output.relationships]
        if llm_output and llm_output.relationships
        else []
    )

    return GraphDocument(nodes=nodes, relationships=relationships, source=doc)


def neo4j_graph():
    graph = Neo4jGraph(
        url=get_property("neo4j_host"),
        username=get_property("neo4j_user"),
        password=get_property("neo4j_psswd"),
        database=get_property("neo4j_database")
    )
    return graph


def create_graph_documents(docs):
    schema = get_schema()
    llm = ChatVertexAI(
        model_name=model,
        temperature=0,
        convert_system_message_to_human=True)
    llm_transformer = llm.with_structured_output(schema)
    chain = default_prompt | llm_transformer
    graph_docs = []
    for doc in docs:
        try:
            graph_docs.append(process_document(chain, doc))
        except BaseException:
            print("Doc exception", doc.metadata["source"])
    return graph_docs


def questions_graph(graph):
    cypher_chain = GraphCypherQAChain.from_llm(
        graph=graph,
        cypher_llm=ChatVertexAI(temperature=0, model=model, prompt=prompt_cypher),
        qa_llm=ChatVertexAI(temperature=0, model=model),
        validate_cypher=True,
        verbose=True,
        top_k=32
    )
    for question in questions:
        try:
            response = cypher_chain.invoke(question)
            print(response["query"])
            print(response["result"])
        except BaseException:
            print("Error processing query")


def add_nodes_and_relationships(documents):
    driver = GraphDatabase.driver(
        uri=get_property("neo4j_uri"),
        auth=(get_property("neo4j_user"),
              get_property("neo4j_psswd")))
    with driver.session() as session:
        for document in documents:
            for node in document.nodes:
                session.run(
                    """
                    MERGE (n:{type} {{id: $id}})
                    ON CREATE SET n.source = $source, n.page_id = $page_id, n.texts = $text
                    ON MATCH SET
                        n.source = apoc.text.join(
                            apoc.coll.toSet(
                                apoc.text.split(n.source + ', ' + $source, ', ')
                            ),
                            ', '
                        ),
                        n.page_id = apoc.text.join(
                            apoc.coll.toSet(
                                apoc.text.split(n.page_id + ', ' + $page_id, ', ')
                            ),
                            ', '
                        ),
                        n.texts = apoc.text.join(
                            apoc.coll.toSet(
                                apoc.text.split(n.texts + ', ' + $text, ', ')
                            ),
                            ', '
                        )
                    """.format(type=node.type),
                    id=node.id,
                    source=node.properties["source"],
                    page_id=node.properties["page_id"],
                    text=node.properties["text"]
                )

            for relationship in document.relationships:
                session.run(
                    """
                    MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
                    MERGE (a)-[r:{type}]->(b)
                    """.format(type=relationship.type),
                    source_id=relationship.source.id,
                    target_id=relationship.target.id
                )


def main():
    start_time = time.time()
    docs = get_chunks()
    graph_docs = create_graph_documents(docs)
    add_nodes_and_relationships(graph_docs)
    graph = neo4j_graph()
    graph.refresh_schema()
    questions_graph(graph)
    end_time = time.time()
    runtime = (end_time - start_time) / 60
    print("RUNTIME:", trunc(runtime), "minutes")


if __name__ == "__main__":
    main()
