import requests
import nltk
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('wordnet')

# get the sonnets through the api from gitHub
sonnets_url = "https://poetrydb.org/author,title/Shakespeare;Sonnet"
req = requests.get(sonnets_url)
sonnets = req.json()


class Document:
    def __init__(self, lines):
        self.lines = self.get_lines(lines)

    def tokenize(self) -> list[str]:
        stem_sonnet = []
        token_sonnet = []
        punct = [".", "'", ":", ";", "!", "?", '"' "'", ","]
        for line in self.lines.split("\n"):
            words = line.split()
            for word in words:
                lower_word = word.lower()
                without_punct = [character for character in lower_word if character not in punct]
                without_punct = ''.join(without_punct)
                token_sonnet.append(without_punct)
        for token in token_sonnet:
            stemmed_token = PorterStemmer().stem(token)
            stem_sonnet.append(stemmed_token)
        return stem_sonnet

    @staticmethod
    def get_lines(self):
        lines = ' \n'.join(self)
        return lines


class Query(Document):
    def __init__(self, query: str):
        super().__init__([query])


class Sonnet(Document):
    def __init__(self, sonnet: dict):
        super().__init__(sonnet['lines'])
        self.sonnet = sonnet
        self.id = self.get_id(sonnet)
        self.title = self.get_title(sonnet)

    @staticmethod
    def get_id(sonnet):
        sonnet_lst = sonnet['title'].split()
        sonnet_id = int(sonnet_lst[1].rstrip(':'))
        return sonnet_id

    @staticmethod
    def get_title(sonnet):
        sonnet_lst = sonnet['title'].split()
        title = ' '.join(sonnet_lst[2:])
        return title

    def __str__(self):
        return f"Sonnet {self.id}: {self.lines}\n"

    def __repr__(self):
        return self.__str__()

    def tokenize(self) -> list[str]:
        return super().tokenize()


class Index(dict[str, set[int]]):
    def __init__(self, documents: list[Sonnet]):
        super().__init__()
        self.documents = documents
        for document in documents:
            self.add(document)

    def add(self, document: Sonnet):
        for token in document.tokenize():
            if token not in self:
                self[token] = set()
            self[token].add(document.id)

    def search(self, query: Query) -> list[Sonnet]:
        q_token = query.tokenize()
        result_id = set()
        result = []
        for token in q_token:
            result_id.update(self[token])
        for token in q_token:
            result_id.intersection_update(self[token])
        sorted_result_id = sorted(map(int, result_id))
        for sonnet in self.documents:
            if sonnet.id in result_id:
                result.append(sonnet)
        print(f"Your search for {query} has resulted in {len(result)} sonnets ({sorted_result_id}):")
        return result

    @staticmethod
    def ui(inp):
        print("Reading sonnets")
        while True:
            print("Enter 'q' to quit")
            search_words = input(str(inp))
            search_query = Query(search_words)
            matching_sonnets = idx_sonnets.search(search_query)
            for matching_sonnet in matching_sonnets:
                print(matching_sonnet)
            if inp == "q":
                break


all_sonnets = [Sonnet(sonnet) for sonnet in sonnets]
idx_sonnets = Index(all_sonnets)
input_text = "Please type in the words you want to search the sonnets for: "
idx_sonnets.ui(input_text)
