import requests

def analyze_sentiment(text):

    sentiment_api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"
    sentiment_payload = {"inputs": text}
    sentiment_result = query_huggingface_api(sentiment_api_url, sentiment_payload)
    print("Sentiment Analysis Result:", sentiment_result)

def summarize(text):
    summarization_api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    summarization_payload = {"inputs": text}
    summary_result = query_huggingface_api(summarization_api_url, summarization_payload)
    print("Summarization Result:", summary_result[0]["summary_text"])

# Function to call Hugging Face Inference API
def query_huggingface_api(api_url, payload):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "x-wait-for-model": "true"
    }

    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()
