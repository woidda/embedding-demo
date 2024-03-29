# Word Embeddings Demo

## Installation

Make sure to set the vm.max_map_count to 262144 before running the application on your local machine. This is required
for the Opensearch container to run.

```bash
sysctl -w vm.max_map_count=262144
```

Download the amazon data set with openai word embeddings via curl into data folder:

```bash
curl -o data/fine_food_reviews_with_embeddings_1k.csv https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/fine_food_reviews_with_embeddings_1k.csv
```

This is a small subset of the fine food reviews dataset with openai word embeddings.
See https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews for the full dataset.

Check the first few lines of the file to make sure it was downloaded correctly:

```bash
head data/fine_food_reviews_with_embeddings_1k.csv
```

## Running the application in development mode

To run the application, simply run the following command in one terminal window:

```bash
docker-compose up 
```

This will start the application and the Opensearch container with two nodes and opensearch dashboards.

For python local development, we create a virtual environment and install the required packages.

In other another terminal window:

First make sure the venv is activated:

```bash
source venv/bin/activate
```

then run the following command to start the application:

```bash
uvicorn main:app --reload
``` 

now you can access the application on http://localhost:8000/

## Accessing the Opensearch Dashboards

To access the Opensearch dashboards, go to http://localhost:5601/ and use the following credentials:

```bash
username: admin
password: Ag4skH8KV8mxee7n5XouNNd2ooA5JC
```