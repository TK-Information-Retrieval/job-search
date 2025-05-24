"""
FastAPI Interface for PyTerrier Search Engine
This script provides a RESTful API using FastAPI for the search engine.
"""

import os
import pandas as pd
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pyterrier as pt
import uvicorn

# Initialize PyTerrier
if not pt.started():
    pt.init()

# Import our search engine
# Assuming the previous code is saved in a file called advanced_search_engine.py
from index import SearchEngine
from qac import QueryAutoCompletion

# FastAPI models
class SearchQuery(BaseModel):
    query: str
    num_results: int = 10

class ModelConfig(BaseModel):
    model: str

class SearchResult(BaseModel):
    docno: str
    score: float
    url: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    # summary: str

class QuerySuggestionResponse(BaseModel):
    results: List[str]

# Initialize FastAPI app
app = FastAPI(
    title="PyTerrier Search API",
    description="A RESTful API for searching documents using PyTerrier",
    version="1.0.0",
)

# Create directories for templates and static files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Create templates
templates = Jinja2Templates(directory="templates")

# Global search engine instance
search_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize the search engine when the app starts."""
    global search_engine
    global qac
    search_engine = SearchEngine()
    search_engine.load_index()
    search_engine.set_retrieval_model("BM25")
    
    qac = QueryAutoCompletion()
    qac.load_model("qac.pkl")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the search engine homepage."""
    with open("templates/index.html", "r") as f:
        return f.read()

@app.post("/api/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """
    Search API endpoint
    
    Args:
        query (SearchQuery): Search parameters
        
    Returns:
        SearchResponse: Search results
    """
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    # Perform search
    results = search_engine.search(
        query.query, 
        num_results=query.num_results, 
    )
    # summary = search_engine.summarize_results(results)
    
    # Convert to response model
    response = {
        "results": [], 
        # "summary": summary
    }
    for _, row in results.iterrows():
        result = {
            "docno": row['docno'],
            "score": float(row['score']),  # Convert numpy float to Python float
        }
        
        # Add URL if available
        if 'url' in row:
            result['url'] = row['url']
            
        response["results"].append(result)
    print(f">>>>> Response: {response}")    
    return response

@app.post("/api/set_model")
async def set_model(config: ModelConfig):
    """
    Set the retrieval model
    
    Args:
        config (ModelConfig): Model configuration
    """
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    valid_models = ["BM25", "TF_IDF", "DirichletLM"]
    if config.model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {', '.join(valid_models)}")
    
    search_engine.set_retrieval_model(config.model)
    
    return {"status": "success", "message": f"Model changed to {config.model}"}

@app.get("/api/info")
async def get_info():
    """
    Get information about the search engine
    """
    if not search_engine or not search_engine.index:
        return {"status": "not_initialized"}
    
    stats = search_engine.index.getCollectionStatistics()
    return {
        "status": "ready",
        "documents": stats.numberOfDocuments,
        "tokens": stats.numberOfTokens,
        "unique_terms": stats.numberOfUniqueTerms,
        "available_models": ["BM25", "TF_IDF", "DirichletLM"]
    }

@app.post("/api/add_document")
async def add_document(document: Dict[str, Any]):
    """
    Add a new document to the index
    
    Args:
        document: Document data with 'docno' and 'text' fields
    """
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    if 'docno' not in document or 'text' not in document:
        raise HTTPException(status_code=400, detail="Document must contain 'docno' and 'text' fields")
    
    # Ensure raw_text exists for highlighting
    if 'raw_text' not in document:
        document['raw_text'] = document['text']
    
    # Add to index (this is a simplified approach - in a real app you might want to
    # rebuild or update the index more efficiently)
    search_engine.create_index([document])
    
    return {"status": "success", "message": "Document added successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Job Search API is running"}

@app.get("/api/suggest", response_model=QuerySuggestionResponse)
async def get_suggestions(query: SearchQuery = Query(None)):
    """
    Get query suggestions while typing
    
    Args:
        query: string -> as query params
    """
    results = qac.get_suggestions(query.query)
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)