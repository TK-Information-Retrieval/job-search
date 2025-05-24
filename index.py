"""
Advanced Search Engine using PyTerrier
This script extends the basic search engine with additional features:
- Web document crawling and indexing
- Query expansion
- Custom preprocessing
- Search results highlighting
"""

import os
import pandas as pd
import pyterrier as pt
from tqdm import tqdm
import pandas as pd
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

    def fetch_documents_from_db(engine, doc_ids):
        """
        Fetch documents from the PostgreSQL database using a list of doc IDs.
        
        Args:
            engine: SQLAlchemy engine
            doc_ids: List of document IDs (as strings or ints)
            
        Returns:
            DataFrame with rows from the job_listings table
        """
        if not doc_ids:
            return pd.DataFrame()  # Return empty if no IDs
        
        placeholders = ','.join(['%s'] * len(doc_ids))
        query = f"""
            SELECT * FROM job_listings
            WHERE "Job Id" IN ({placeholders})
        """

        with engine.connect() as conn:
            result = conn.execute(text(query), doc_ids)
            rows = result.fetchall()
            columns = result.keys()
            return pd.DataFrame(rows, columns=columns)
        
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
            doc_rows = self.fetch_documents_from_db(engine, doc_ids)

            # Optional: merge back for scores or ranking
            merged_results = pd.merge(results, doc_rows, left_on='docno', right_on='Job Id', how='left')
            return merged_results
        else:
            return results
        
    
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