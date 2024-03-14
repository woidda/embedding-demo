from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_openai import OpenAIEmbeddings
from opensearch_client import client

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
# takes the API key from the environment
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


@app.get("/open-ai-embeddings/", tags=["open-ai-embeddings"])
async def root(text: str) -> dict[str, list[float]]:
    return {"vector": embeddings.embed_query(text)}


def search_reviews(text, n):
    embedding = embeddings.embed_query(text)
    body = {"size": n, "query": {"knn": {"embedding": {"vector": embedding, "k": n}}}}
    response = client.search(index="word_embeddings", body=body)
    return response["hits"]["hits"]


@app.get("/open-ai-embeddings/search", tags=["open-ai-embeddings"])
async def search(text: str) -> dict[str, Any]:
    # e.g. text = "whole wheat pasta"
    return {"results": search_reviews(text, n=3)}
