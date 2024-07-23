# RAG System with LLM Gemini, Confluence, and Neo4j Integration

## Overview

This application uses the LLM Gemini model to create a Retrieval-Augmented Generation (RAG) system with Confluence and stores the data in a Neo4j graph database. The dependencies are managed using Poetry. Docker is used to run a Neo4j container, and Chrome is required to scrape content from Confluence. Additionally, you will need a Google Cloud Platform (GCP) account for certain integrations.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.12+
- Poetry
- Docker
- Google Cloud SDK
- Chrome
- Ollama

## Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/alfonsozamorac/rag-confluence.git
   cd rag-confluence
   ```

2. **Install Dependencies**

   ```sh
   poetry install
   ```

3. **Setup Docker for Neo4j**

    Create a new Neo4j Docker Container named 'neo4j' and set new properties to use Awesome Procedures On Cypher (APOC):

   ```sh
   docker pull neo4j:latest
   docker run \
    --publish=7475:7474 --publish=7688:7687 \
    --volume=$HOME/neo4j/data:/data \
    --name neo4j \
    -d \
    -e NEO4J_AUTH=neo4j/${NEO4J_PASS} \
    neo4j
    docker exec -it neo4j /bin/bash
    cp $NEO4J_HOME/labs/apoc-5.21.2-core.jar $NEO4J_HOME/plugins
    echo "dbms.security.procedures.unrestricted=apoc.*" >> $NEO4J_HOME/conf/neo4j.conf
    echo "dbms.security.procedures.allowlist=apoc.*" >> $NEO4J_HOME/conf/neo4j.conf
    echo "dbms.security.procedures.whitelist=apoc.meta.data,apoc.load.*" >> $NEO4J_HOME/conf/neo4j.conf
    docker restart neo4j
   ```

4. **Set up GCP Credentials**
    Set credentials for GCP, set the correct path to your JSON_CREDENTIALS:

   ```sh
    export GOOGLE_APPLICATION_CREDENTIALS=${JSON_CREDENTIALS}
   ```

## Configuration

1. **Environment Variables**

    Create a `.secret` file in the rag-confluence directory of your project and add the following replacing by your own values:

   ```sh
    confluence=${URL_CONFLUENCE}
    user=${USER_CONFLUENCE}
    psswd=${PASS_CONFLUENCE}
    ollama_host=${OLLAMA_HOST} # example http://localhost:11434
    neo4j_host=${NEO4J_HOST} # example bolt://localhost:7687
    neo4j_uri=${NEO4J_URI} # example neo4j://localhost:7687
    neo4j_user=${NEO4J_USER}
    neo4j_psswd=${NEO4J_PASS}
    neo4j_database=${NEO4J_DATABASE}
    project_gcp=${PROJECT_GCP}
   ```

## Usage

1. **Confluence Information**

    Get the information of a given page id and their childs. This generates a new folder named output with the content:

   ```sh
    python3 confluence.py ${PAGE_ID}
   ```
2. **Vector Questions**

    Run vector generator and run the questions:

   ```sh
    python3 kgraph.py
   ```

3. **Graph Questions**

    Run KGRAPH generator and run the questions:

   ```sh
    python3 vector.py
   ```