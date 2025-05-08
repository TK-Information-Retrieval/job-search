"""
Client for PyTerrier Search Engine API
This script provides a simple command-line client for interacting with the FastAPI search engine.
"""

import argparse
import json
import requests
from typing import Dict, Any, Optional, List, Union
import sys
import os

class SearchEngineClient:
    """Client for interacting with the PyTerrier Search Engine API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client with the API base URL.
        
        Args:
            base_url: Base URL of the search engine API
        """
        self.base_url = base_url
        
    def search(self, query: str, use_expansion: bool = False, num_results: int = 10) -> Dict[str, Any]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            use_expansion: Whether to use query expansion
            num_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        url = f"{self.base_url}/api/search"
        data = {
            "query": query,
            "use_expansion": use_expansion,
            "num_results": num_results
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during search: {e}")
            return {"results": []}
            
    def set_model(self, model: str) -> Dict[str, Any]:
        """
        Set the retrieval model for the search engine.
        
        Args:
            model: Model name ('BM25', 'TF_IDF', or 'DirichletLM')
            
        Returns:
            Response from the API
        """
        url = f"{self.base_url}/api/set_model"
        data = {"model": model}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting model: {e}")
            return {"status": "error", "message": str(e)}
            
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the search engine.
        
        Returns:
            Dictionary containing information about the search engine
        """
        url = f"{self.base_url}/api/info"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting info: {e}")
            return {"status": "error", "message": str(e)}
            
    def add_document(self, docno: str, text: str) -> Dict[str, Any]:
        """
        Add a new document to the index.
        
        Args:
            docno: Document ID
            text: Document text content
            
        Returns:
            Response from the API
        """
        url = f"{self.base_url}/api/add_document"
        data = {
            "docno": docno,
            "text": text,
            "raw_text": text
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding document: {e}")
            return {"status": "error", "message": str(e)}

def print_results(results: Dict[str, Any]) -> None:
    """
    Print search results in a formatted way.
    
    Args:
        results: Search results dictionary
    """
    if not results.get("results", []):
        print("No results found.")
        return
        
    print(f"\nFound {len(results['results'])} results:\n")
    
    for i, result in enumerate(results["results"], 1):
        print(f"{i}. {result['docno']} (Score: {result['score']:.4f})")
        if "url" in result and result["url"]:
            print(f"   URL: {result['url']}")
        print()

def main() -> None:
    """Main function to parse command line arguments and run client."""
    parser = argparse.ArgumentParser(description="PyTerrier Search Engine Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--expansion", "-e", action="store_true", help="Use query expansion")
    search_parser.add_argument("--results", "-r", type=int, default=10, help="Number of results to display")
    
    # Set model command
    model_parser = subparsers.add_parser("model", help="Set retrieval model")
    model_parser.add_argument("name", choices=["BM25", "TF_IDF", "DirichletLM"], help="Model name")
    
    # Info command
    subparsers.add_parser("info", help="Get search engine information")
    
    # Add document command
    add_parser = subparsers.add_parser("add", help="Add a document to the index")
    add_parser.add_argument("docno", help="Document ID")
    add_parser.add_argument("text", help="Document text content")
    
    # Add base URL option to all commands
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the search engine API")
    
    args = parser.parse_args()
    
    # Create client
    client = SearchEngineClient(args.url)
    
    if args.command == "search":
        results = client.search(args.query, args.expansion, args.results)
        print_results(results)
    elif args.command == "model":
        response = client.set_model(args.name)
        print(f"Model set to {args.name}: {response['status']}")
    elif args.command == "info":
        info = client.get_info()
        print(json.dumps(info, indent=2))
    elif args.command == "add":
        response = client.add_document(args.docno, args.text)
        print(f"Document added: {response['status']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()