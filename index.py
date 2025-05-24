"""
Advanced Search Engine using PyTerrier
This script extends the basic search engine with additional features:
- Web document crawling and indexing
- Query expansion
- Custom preprocessing
- Search results highlighting
"""
import os
import re
import json
import pandas as pd
import pyterrier as pt
from tqdm import tqdm
from sqlalchemy import text

# Initialize PyTerrier
if not pt.started():
    pt.init()

class SearchEngine:
    def __init__(self, index_path="./index"):
        """Initialize the search engine with a specified index path."""
        self.index_path = os.path.abspath(index_path)
        self.index = None
        self.indexer = None
        self.retrieval_model = None
    
    def create_index(self, df):
        """
        Create an index from a list of documents.
        
        Args:
            documents: List of dictionaries with 'docno' (document ID) and 'text' (document content) keys
        """
        index_df = df.copy()        
        index_df['docno'] = index_df['Job Id'].astype(str)
        
        # Concatenate all the text columns to index
        text_columns = list(index_df.columns)
        text_columns.remove('docno')
        
        index_df['text'] = index_df[text_columns].apply(
            lambda row: ' '.join(str(val) for val in row if pd.notna(val)), axis=1
        )
        index_df = index_df[['docno', 'text']]
        
        # Indexing Part
        os.makedirs(self.index_path, exist_ok=True)
        self.indexer = pt.IterDictIndexer(self.index_path, overwrite=True)
        
        docs = index_df.to_dict(orient='records')
        with tqdm(total=len(docs), desc="Indexing documents") as pbar:
            def index_with_progress(docs):
                for doc in docs:
                    yield doc
                    pbar.update(1)
            
            self.indexer.index(index_with_progress(docs))        
        self.documents_df = df
        self.index = pt.IndexFactory.of(self.index_path)
        
    def load_index(self):
        """Load an existing index."""
        if os.path.exists(self.index_path):
            self.index = pt.IndexFactory.of(self.index_path)
            print(f"Index loaded with {self.index.getCollectionStatistics().numberOfDocuments} documents")
            return False
        else:
            print("No index found at specified path.")
            return False
            
    def set_retrieval_model(self, model_name="BM25"):
        """
        Set the retrieval model for searching.
        
        Args:
            model_name: String representing the model name ('BM25', 'TF_IDF', 'DirichletLM')
        """
        if self.index is None:
            print("Please create or load an index first.")
            return
        
        if model_name == "TF_IDF":
            self.retrieval_model = pt.BatchRetrieve(self.index, wmodel="TF_IDF")
        elif model_name == "DirichletLM":
            self.retrieval_model = pt.BatchRetrieve(self.index, wmodel="DirichletLM")
        else:
            self.retrieval_model = pt.BatchRetrieve(self.index, wmodel="BM25")
            
        print(f"Retrieval model set to {model_name}")

    def parse_job_fields(self, row: dict) -> dict:
        row["benefits"] = json.loads(row["benefits"])
        row["responsibilities"] = re.findall(r'[^.]+(?:\.)?', row["responsibilities"])
        return row

    def fetch_documents(self, engine, doc_ids=None):
        """
        Fetch documents from the PostgreSQL database using a list of doc IDs.
        
        Args:
            engine: SQLAlchemy engine
            doc_ids: List of document IDs (as strings or ints)
            
        Returns:
            DataFrame with rows from the job_listings table
        """
        if doc_ids==None:
            # generic
            query = text(f"""
                SELECT job_id, job_title, company, location, salary_range FROM job_listings
                LIMIT 20
            """)

            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.mappings().all()
                return [dict(row) for row in rows]
        else:
            # specific
            param_names = [f"id{i}" for i in range(len(doc_ids))]
            placeholders = ", ".join([f":{name}" for name in param_names])
            query = text(f"""
                SELECT job_id, job_title, company, location, salary_range FROM job_listings
                WHERE "job_id" IN ({placeholders})
            """)

            params = {f"id{i}": doc_id for i, doc_id in enumerate(doc_ids)}

            with engine.connect() as conn:
                result = conn.execute(query, params)
                rows = result.mappings().all()
                return [dict(row) for row in rows]
        
    def fetch_details(self, engine, doc_id):
        """
        Fetch detail from 1 of the documents from the PostgreSQL database using a doc IDs.
        
        Args:
            engine: SQLAlchemy engine
            doc_id: List of document ID (as string)
            
        Returns:
            Dict
        """
        if not doc_id:
            return []

        query = text("""
        SELECT * FROM job_listings WHERE "job_id" = :doc_id
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"doc_id": doc_id})
            row = result.mappings().first() 
            return self.parse_job_fields(dict(row))
        
    def search(self, query, num_results=10, engine=None):
        """
        Search the index with a query.
        
        Args:
            query: String containing the search query
            num_results: Maximum number of search results to return
            
        Returns:
            DataFrame with search results and highlighted snippets
        """
        if self.retrieval_model is None:
            self.set_retrieval_model()
            
        query_df = pd.DataFrame([{"qid": "q1", "query": query}])        
        results = self.retrieval_model.transform(query_df)        
        print("Search result columns:", results.columns.tolist())
        
        # Limit results
        if len(results) > num_results:
            results = results.head(num_results)
        
        if engine is not None:
            if 'docno' not in results.columns and 'docid' in results.columns:
                results = results.rename(columns={'docid': 'docno'})
            
            doc_ids = results['docno'].tolist()
            results = self.fetch_documents(engine, doc_ids)

        return results
    
    def summarize_results(self, results):
        """
        Summarize the search results.
        
        Args:
            results: DataFrame containing search results
        
        Returns:
            String with summarized results
        """
        print("Summary input columns:", results.columns.tolist())        
        if 'docno' in results.columns:
            doc_ids = results['docno'].unique()
            join_col = 'docno'
        elif 'Job Id' in results.columns:
            doc_ids = results['Job Id'].unique()
            join_col = 'Job Id'
        else:
            print("Warning: Could not find document IDs in results")
            return "Could not summarize results: Missing document IDs"
        
        if 'text' in self.documents_df.columns:
            text_col = 'text'
        elif 'Job Description' in self.documents_df.columns:
            text_col = 'Job Description'
        else:
            # Fallback: Use multiple columns
            text_cols = ['Job Title', 'Job Description', 'Responsibilities']
            texts = []
            for _, row in self.documents_df[self.documents_df[join_col].isin(doc_ids)].iterrows():
                combined_text = ' '.join(str(row.get(col, '')) for col in text_cols if not pd.isna(row.get(col, '')))
                texts.append(combined_text)
            doc_contents = texts
        
        # If we're using a single text column
        if 'doc_contents' not in locals():
            doc_contents = self.documents_df[self.documents_df[join_col].isin(doc_ids)][text_col].tolist()        
        if not doc_contents:
            return "No content found to summarize"
        
        query = f"""Summarize the following documents in a single paragraph.
    {doc_contents}
    Summary:"""
        
        llm = LLMModel()
        response = llm.generate_response(query)        
        if "</think>" in response:
            response = response.split("</think>")[-1].strip()
        
        return response
    
def start_indexing():
    print("Initializing job search engine...")
    search_engine = SearchEngine()
    
    # Use local documents
    print("Creating index from local documents...")
    df = pd.read_csv('collection/job_descriptions_small.csv')

    columns = ['Job Id', 'Experience', 'Qualifications', 'Salary Range', 'location',
            'Country','Work Type', 'Company Size', 'Preference', 
            'Job Title', 'Role', 'Job Description', 'Benefits',
            'skills', 'Responsibilities', 'Company', 'Company Profile']
    df = df[columns]
    search_engine.create_index(df)

if __name__ == "__main__":
    print("Job Search Engine Indexing Process")
    print("-" * 50)
    start_indexing()