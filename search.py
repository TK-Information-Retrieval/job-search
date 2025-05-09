import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import sys
from dotenv import load_dotenv

from index import SearchEngine   

load_dotenv()


# Database connection parameters - using your Supabase credentials
db_params = {
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),  
    'password': os.getenv('DB_PASSWORD'), 
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

password_encoded = quote_plus(db_params['password'])
connection_string = f"postgresql://{db_params['user']}:{password_encoded}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

if __name__ == "__main__":
    print("Job Search Engine")
    print("-" * 50)
    try:
        engine = create_engine(
            connection_string,
            connect_args={
                'connect_timeout': 30,  # Longer timeout
                'application_name': 'job_listings_import'  # Help identify this connection in logs
            }
        )
        print("SQLAlchemy engine created successfully")
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        sys.exit(1)

    search_engine = SearchEngine()
    search_engine.load_index()
    search_engine.set_retrieval_model("BM25")
    
    # Perform searches
    print("\nSearch example 1: 'python programming'")
    results = search_engine.search("python programming",engine=engine)

    try:
        display_cols = ['Job Id', 'Job Title', 'Job Description', 'score']
        print(results[display_cols].to_string(index=False))
    except KeyError as e:
        print(f"Original columns not found ({e}), using available columns instead")
        display_cols = [col for col in results.columns if col in 
                    ['docno', 'score', 'rank', 'Job Title', 'Job Description']]
        if display_cols:
            print(results[display_cols].to_string(index=False))
        else:
            print(results.to_string(index=False))

    # Try to summarize results
    try:
        summary = search_engine.summarize_results(results)
        print("\nSummary of results:\n", summary)
    except Exception as e:
        print(f"Could not generate summary: {e}")