from fastapi import FastAPI
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import numpy as np
from typing import List

app = FastAPI()


@app.post("/")
def apply_nlp(): 
    return {"Data": "Text"}


def nltk_POS_lemmatizer(sentence: str) -> List[str]:
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(sentence)
    token_tag_pairs = nltk.pos_tag(tokens)

    return [lemmatizer.lemmatize(token[0], tag_dict.get(token[1][0], wordnet.NOUN)).lower()
            for token in token_tag_pairs if token[0] not in "?!,."]


def bag_words(sentence, known_words):
    bag = [0] * len(known_words)

    word_pattern = nltk_POS_lemmatizer(sentence)

    for new_word in word_pattern:
        for i, word in enumerate(known_words):
            if new_word == word:
                bag[i] = 1

    return np.array(bag)