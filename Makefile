run-app:
	streamlit run app.py
run-opensearch:
	podman-compose up
run-api:
	uvicorn main:app --reload
copy-certificate:
	podman cp opensearch-node1:/usr/share/opensearch/config/root-ca.pem .
