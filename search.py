from index import SearchEngine   

if __name__ == "__main__":
    print("Job Search Engine")
    print("-" * 50)
    search_engine = SearchEngine()
    search_engine.load_index()
    search_engine.set_retrieval_model("BM25")
    
    # Perform searches
    print("\nSearch example 1: 'python programming'")
    results = search_engine.search("python programming")

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