
questions = [
    "What is about?",
    "What is the name of the company that belongs this documentation?",
]

prompt_cypher = """
    I need to retrieve specific information from a Neo4j graph database using Cypher queries. The IDs in the database are normalized to be singular and in lowercase.
    When using Cypher queries, apply the normalization to the ID parameters. For example, if a node ID is provided as "TALKS," convert it to "talk" and use this normalized ID in the query.
"""

system_prompt = (
    "# Knowledge Graph Instructions for LLM"
    "## 1. Overview"
    "You are a top-tier algorithm designed to extract information in structured formats to build a knowledge graph."
    "Capture as much information from the text as possible without sacrificing accuracy."
    "Do not add any information that is not explicitly mentioned in the text."
    "- **Nodes** represent entities and concepts."
    "- Aim for simplicity and clarity in the knowledge graph, making it accessible to a wide audience."
    "## 2. Labeling Nodes"
    "- **Consistency**: Use available types for node labels consistently."
    "  - Use basic or elementary types for node labels."
    "  - For example, label a person as **'person'** rather than specific terms like 'mathematician' or 'scientist'."
    "- **Node IDs**: Avoid using integers as node IDs. Node IDs should be names or human-readable identifiers found in the text and should always be non-null."
    "- **Relationships** represent connections between entities or concepts."
    "  - Ensure consistency and generality in relationship types when constructing the knowledge graph."
    "Use general and timeless relationship types like 'PROFESSOR' instead of specific ones like 'BECAME_PROFESSOR'."
    "## 3. Coreference Resolution"
    "- **Maintain Entity Consistency**: Ensure consistency when extracting entities."
    "  - If an entity, such as 'John Doe', is mentioned multiple times with different names or pronouns (e.g., 'Joe', 'he'),"
    "use the most complete identifier for that entity throughout the knowledge graph. In this example, use 'John Doe' as the entity ID."
    "- The knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial."
    "## 4. Strict Compliance"
    "Adhere strictly to these rules. Non-compliance will result in termination. Nodes and relationships cannot be null."
    "If you don’t know something, it's preferred to discard the information.")

human_prompt = (
    "Tip: Make sure to answer in the correct format and do not include any explanations."
    "Ensure all fields have valid and non-null values (end_node_type, end_node_id, start_node_type, "
    "start_node_id, type). You have to provide accurate"
    "information about the nodes so you can later check what information it provides."
    "You must obtain this information from the text and enter it so that it is later readable in Neo4j."
    "The start_node_text and end_node_text field in each node is the most important, indicating the text source used to create the node."
    "If a field contains a null value or None and it is not informed, remove the entire ConfluenceRelationship"
    "record or entry containing that null value. Use the given format to extract information "
    "from the following input: {input}")

model = "gemini-pro"
