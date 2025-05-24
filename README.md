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

-   `index.py` - Core search engine functionality
-   `app.py` - FastAPI interface
-   `schema.py` - request and response schema
-   `qac.py` - query autocomplete funtionality

## API Reference

### Search (`/api/search`)

```
GET /api/search?query=<query>&num_results=<limit>

Query params:
  {
    "query": "python programming",
    "num_results": 10
  }

Returns:
  {
    "results" : [
      {
        "job_id": "1079021951564169",
        "job_title": "Front-End Developer",
        "company": "Dixons Carphone",
        "location": "New Delhi",
        "salary_range": "$58K-$80K"
      },
      {...},
      ...
    ]
  }
```


### Get Jobs (`/api/jobs`)

```
GET /api/jobs

Returns:
{
    "results" : [
      {
        "job_id": "1079021951564169",
        "job_title": "Front-End Developer",
        "company": "Dixons Carphone",
        "location": "New Delhi",
        "salary_range": "$58K-$80K"
      },
      {...},
      ...
    ]
  }
```

### Get Job Detail (`/api/jobs/{doc_id}`)

```
GET /api/jobs/{doc_id}

Returns:
{
  "job_id": "1041276767356708",
  "experience": "2 to 10 Years",
  "qualifications": "B.Tech",
  "salary_range": "$60K-$89K",
  "location": "Dushanbe",
  "country": "Tajikistan",
  "latitude": 38.861,
  "longitude": 71.2761,
  "work_type": "Contract",
  "company_size": 53817,
  "job_posting_date": "2021-10-24",
  "preference": "Female",
  "contact_person": "Jeff Sharp",
  "contact": "763-546-3525x210",
  "job_title": "Structural Engineer",
  "role": "Design Engineer",
  "job_portal": "Snagajob",
  "job_description": "A Design Engineer creates and develops product designs and specifications, using engineering principles and design software to bring innovative products to market.",
  "benefits": [
    "'Employee Referral Programs", 
    "Financial Counseling", 
    "Health and Wellness Facilities"
  ],
  "skills": "Engineering design CAD software proficiency Problem-solving Technical knowledge Communication skills",
  "responsibilities": [
    "Design structural systems and components for buildings and infrastructure projects.",
    "Perform structural analysis and calculations",
    "Create detailed design plans and specifications."
  ],
  "company": "Microsoft",
  "company_profile": {
    "CEO": "Satya Nadella",
    "Zip": "98052",
    "City": "Redmond",
    "State": "Washington",
    "Sector": "Technology",
    "Ticker": "MSFT",
    "Website": "www.microsoft.com",
    "Industry": "Computer Software"
  }
```


### Get Query Suggestions (`/api/suggest`)

```
GET /api/jobs?query=<query>

Returns:
{
  "results" : [
    "rec1",
    "req2"
  ]
}
```