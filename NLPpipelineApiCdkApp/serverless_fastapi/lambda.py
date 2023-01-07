import logging
import json

from .nlp_pipelines import nlp_pipelines, nltk_POS_lemmatizer, bag_words

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def apply_nlp(payload):
    sentence = payload["sentence"]
    nlp_name = payload["nlp_pipeline"]
    known_words = payload["known_words"]
    nlp = nlp_pipelines.get(nlp_name, nltk_POS_lemmatizer)

    print("PROCESSING WORDS: ")
    print("processed words: ", nlp(sentence))
    print("bagging words: ", bag_words(sentence, known_words, nlp))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "processed_words": nlp(sentence),
            "bag": bag_words(sentence, known_words, nlp),
        })
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
