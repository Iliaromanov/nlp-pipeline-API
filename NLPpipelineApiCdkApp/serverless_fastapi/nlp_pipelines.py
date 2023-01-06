import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer

from typing import List


def nltk_stemmer(sentence: str) -> List[str]:
    stemmer = LancasterStemmer()
    tokens = nltk.word_tokenize(sentence)

    return [stemmer.stem(w) for w in tokens if w not in "?!,."]


def nltk_no_POS_lemmatizer(sentence: str) -> List[str]:
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(sentence)

    return [lemmatizer.lemmatize(w.lower()) for w in tokens if w not in "?!,."]


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


nlp_pipelines = {  # more pipelines coming soon
    "nltk_stemmer": nltk_stemmer,
    "nltk_no_POS_lemmatizer": nltk_no_POS_lemmatizer,
    "nltk_POS_lemmatizer": nltk_POS_lemmatizer
}


def bag_words(sentence, known_words, nlp):
    bag = [0] * len(known_words)

    word_pattern = nlp(sentence)

    for new_word in word_pattern:
        for i, word in enumerate(known_words):
            if new_word == word:
                bag[i] = 1

    return bag


def word_vectors(sentence):
    pass