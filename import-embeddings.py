import json
import csv
import os

from dotenv import load_dotenv
from opensearchpy import helpers

from opensearchpy import OpenSearch

# Load environment variables from .env file
load_dotenv()

host = os.environ.get("OPENSEARCH_HOST", "localhost")
port = os.environ.get("OPENSEARCH_PORT", 9200)
auth = ("admin", os.environ.get("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))

client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_auth=auth,
    use_ssl=True,  # Assuming HTTPS based on previous setup
    verify_certs=False,  # For self-signed certs (like curl -k)
    ssl_show_warn=False,  # Suppress SSL warnings in Streamlit app
)


csv_file_path = "./data/fine_food_reviews_with_embeddings_1k.csv"


def get_embedding_dimension(file_path):
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Only check the first non-empty embedding
            embedding_str = row.get("embedding")
            if embedding_str and embedding_str.strip():
                embedding_list = embedding_str.strip().split(",")
                return len(embedding_list)
        raise ValueError("No non-empty embeddings found in the CSV file.")


if __name__ == "__main__":
    # Define your OpenSearch index
    index_name = "word_embeddings"
    index_body = {
        "settings": {
            "index": {
                "knn": "true",
                "knn.algo_param.ef_search": 100,
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        },
        "mappings": {
            "properties": {
                "ProductId": {"type": "keyword"},
                "UserId": {"type": "keyword"},
                "Score": {"type": "integer"},
                "Summary": {"type": "text"},
                "Text": {"type": "text"},
                "combined": {"type": "text"},
                "n_tokens": {"type": "integer"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": get_embedding_dimension(csv_file_path),
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                        "space_type": "l2",
                        "parameters": {"ef_construction": 256, "m": 8},
                    },
                },
            }
        },
    }

    # Create the index
    try:
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body=index_body)
            print(f"Created index {index_name}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Function to process the CSV file and yield documents
    def process_csv(file_path):
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Transform the 'embedding' field from string to list of floats
                if row["embedding"]:
                    row["embedding"] = json.loads(row["embedding"])
                # Ignore the first column (just an ID)
                doc = {k: row[k] for k in row if k not in ("",)}
                yield {"_index": index_name, "_source": doc}

    # Bulk index the data
    helpers.bulk(client, process_csv(csv_file_path))
