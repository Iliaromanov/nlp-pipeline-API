from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from .nlp_pipelines import *
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

def create_app() -> FastAPI:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors self"
        app.logger.info(
            "[from:%s|%s %s]+[%s]=>[%d|%dbytes]"
            % (
                request.remote_addr,
                request.method,
                request.url,
                request.data,
                response.status_code,
                response.content_length,
            )
        )
        return response

    return app


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)