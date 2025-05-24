import re
import autocomplete

class QueryAutoCompletion():
    def __init__(self, filepath=None):
        """
        Initializes QAC class
        """
            
    def load_model(self, pickle_filepath:str=None) -> None:
        """
        Load dictionary
        
        parameters:
        - pickle_filepath (str): filepath to pickle
        
        returns: None
        """
        if pickle_filepath == None:
            autocomplete.load()
        else:
            autocomplete.models.load_models(pickle_filepath)
        
    def get_suggestions(self, query: str, limit:int=5) -> list[str]:
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
                predictions = autocomplete.predict(tokens[-2], tokens[-1], limit)
                if len(predictions < limit):
                    predictions.extend(autocomplete.predict(tokens[-1], '', limit))
            except:
                predictions = autocomplete.predict(tokens[-1], '', limit)
            
            predictions = [query + suggestion[len(tokens[-1]):] 
                           for suggestion, _ in predictions]
            return predictions[:limit]

def main():
    qac = QueryAutoCompletion()
    qac.load_model("qac.pkl")
    
    while True:
        query = input("Search for: ")
        print(qac.get_suggestions(query, 7))

if __name__ == "__main__":
    main()