import autocomplete

if __name__ == "__main__":
    with open('corpus.txt') as file:
        corpus = file.read()
        autocomplete.models.train_models(corpus, 'qac.pkl')