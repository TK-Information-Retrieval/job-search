# PyTerrier Search Engine

A simple yet powerful search engine built using PyTerrier with a FastAPI interface. This project demonstrates how to build a search engine that allows indexing documents and retrieving them with relevance ranking.

## Features

-   Document indexing and retrieval using PyTerrier
-   Multiple retrieval models (BM25, TF-IDF, Dirichlet LM)
-   RESTful API with FastAPI
-   Interactive web interface
-   Command-line client
-   Summarization of search results

## Installation

### Prerequisites

-   Python 3.7+
-   Java 11+ (required by PyTerrier)

### Setup

1. Clone the repository

2. Install the required packages:

    ```
    pip install -r requirements.txt
    ```

## Usage

### Starting the Server

Run the FastAPI server:

```
python app.py
```

This will start the server at http://localhost:8000

### Web Interface

Visit http://localhost:8000 in your web browser to use the search engine through the web interface. The interface allows you to:

-   Enter search queries
-   Enable/disable query expansion
-   Select the retrieval model
-   Choose the number of results to display

### API Documentation

FastAPI automatically generates interactive API documentation. Visit:

-   http://localhost:8000/docs - Swagger UI
-   http://localhost:8000/redoc - ReDoc

### Command-line Client

You can use the command-line client to interact with the search engine:

```
# Search for documents
python client.py search "python programming" --results 5

# Set the retrieval model
python client.py model BM25

# Get information about the search engine
python client.py info

# Add a new document to the index
python client.py add "doc11" "This is a new document about search engines."
```

## Code Structure

-   `search.py` - Core search engine functionality
-   `app.py` - FastAPI interface
-   `client.py` - Command-line client
-   `templates/index.html` - Web interface template
-   `llm.py` - LLM integration for summarization

## API Reference

### Search (`/api/search`)

```
POST /api/search
{
  "query": "python programming",
  "use_expansion": false,
  "num_results": 10
}
```

### Set Model (`/api/set_model`)

```
POST /api/set_model
{
  "model": "BM25" | "TF_IDF" | "DirichletLM"
}
```

### Get Info (`/api/info`)

```
GET /api/info
```

### Add Document (`/api/add_document`)

```
POST /api/add_document
{
  "docno": "doc11",
  "text": "This is a new document about search engines."
}
```
