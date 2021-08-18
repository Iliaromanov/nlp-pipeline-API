# NLP-pipeline-API
REST API that applies natural language processing pipelines to provided raw text data.Built using Python FastAPI. 

This API was built as a microservice for my Resume Chatbot web app, but is useful for any NLP related tasks.

## Why Preprocess Text Data?

Preprocessing free text data is a crucial step in making that data usable for analysis and machine learning model training. Raw text data may contain unwanted or unimportant text which reduces the accuracy and efficiency during model training and might make the data hard to understand/analyze. NLP is necessary to highlight the attributes of the data that you want your machine learning system to pick up on.

## Usage

url: https://nlp-pipeline-api.herokuapp.com/

Sample JSON request body:
```yaml
{
    "sentence": "Hello world! My name is Ilia's resume.,? blablabla coming having doing",
    "known_words": ["hello", "goodbye", "ilia", "romanov", "run", "to", "come", "have", "foo", "do"],
    "nlp_pipeline": "nltk_POS_lemmatizer"
}
```
Sample response:
```yaml
{
    "processed_words": [
        "hello",
        "world",
        "my",
        "name",
        "be",
        "ilia",
        "'s",
        "resume",
        "blablabla",
        "come",
        "have",
        "do"
    ],
    "bag": [1, 0, 1, 0, 0, 0, 1, 1, 0, 1]
}
```

Currently available NLP pipelines: 
- **nltk_stemmer**: tokenizes sentence, then applies `nltk.stem.lancaster.LancasterStemmer()` and removes punctuation symbols.
- **nltk_no_POS_lemmatizer**: tokenizes sentence, then applies `nltk.stem.WordNetLemmatizer()` *without providing wordnet Part of Sentence (POS) tags for tokens* and removes punctuation symbols.
- **nltk_POS_lemmatizer**: same as **nltk_no_POS_lemmatizer**, except POS tags are identified and passed to the `WordNetLemmatizer()` for each word token.
