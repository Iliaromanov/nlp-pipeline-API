from fastapi import FastAPI
from pydantic import BaseModel

from nlp_pipelines import *
from typing import List, Optional

app = FastAPI()


class SentenceRequest(BaseModel):
    sentence: str
    known_words: List[str]
    nlp_pipeline: Optional[str] = None


@app.post("/")
def apply_nlp(payload: SentenceRequest):
    sentence = payload.sentence
    nlp_name = payload.nlp_pipeline
    known_words = payload.known_words
    nlp = nlp_pipelines.get(nlp_name, nltk_POS_lemmatizer)

    return {
        "processed_words": nlp(sentence),
        "bag": bag_words(sentence, known_words, nlp)
    }