import os

from opensearchpy import OpenSearch, RequestsHttpConnection
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

host = os.environ.get("OPENSEARCH_HOST")
port = os.environ.get("OPENSEARCH_PORT")
auth = ("admin", os.environ.get("OPENSEARCH_INITIAL_ADMIN_PASSWORD"))
client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    connection_class=RequestsHttpConnection,
)
