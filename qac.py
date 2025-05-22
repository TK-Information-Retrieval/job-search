import re
from autocomplete import predict, models, load

def load_model(pickle_file:str=None) -> None:
    """
    Load dictionary
    
    parameters:
    - pickle_file (str): filepath to pickle
    
    returns: None
    """
    if pickle_file == None:
        load()
    else:
        models.load_models(pickle_file)
    
def get_suggestions(query: str, limit:int=5) -> list[str]:
    """
    Function 
    
    parameters:
    - query (str): query passed from the frontend
    - limit (int): maximum suggestions
    
    returns:
    query suggestions (list[str])
    """
    tokens = re.split(r'\W+', query)
        
    if len(tokens) > 0:
        try:
            predictions = predict(tokens[-2], tokens[-1], limit)
            if len(predictions < limit):
                predictions.extend(predict(tokens[-1], '', limit))
        except:
            predictions = predict(tokens[-1], '', limit)
        
        predictions = [query + suggestion[len(tokens[-1]):] for suggestion, _ in predictions]
        return predictions[:limit]

def main():
    top_n = 5
    load_model("qac.pkl")
    
    while True:
        query = input("Search for: ")
        print(get_suggestions(query, top_n))

if __name__ == "__main__":
    main()