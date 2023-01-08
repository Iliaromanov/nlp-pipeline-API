import logging
import json
from typing import Dict, Any

from .nlp_pipelines import nlp_pipelines, nltk_POS_lemmatizer, bag_words

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def apply_nlp(payload: Dict[str, Any]):
    sentence = payload.get("sentence", None)
    nlp_name = payload.get("nlp_pipeline", "nltk_POS_lemmatizer")
    known_words = payload.get("known_words", None)
    nlp = nlp_pipelines.get(nlp_name, nltk_POS_lemmatizer)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "processed_words": nlp(sentence),
                "bag": bag_words(sentence, known_words, nlp),
            }
        ),
    }


def lambda_handler(event, context):
    try:
        logger.debug(event)
        headers = event["headers"]
        # we passed host from CloudFront function in the field
        #  X-Forwarded-Host
        cf_host = headers.pop("X-Forwarded-Host", None)
        if cf_host:
            # patch host header
            headers["Host"] = cf_host
            event["multiValueHeaders"]["Host"] = [cf_host]
            logger.info(f"Host header is successfully patched to {cf_host}")

        return apply_nlp(json.loads(event["body"]))
    except:  # noqa
        logger.exception("Exception handling lambda")
        raise
