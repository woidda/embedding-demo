import streamlit as st
import json
from opensearchpy import OpenSearch, exceptions

# --- Page Configuration ---
st.set_page_config(page_title="Simple OpenSearch UI", layout="wide")
st.title(" einfache OpenSearch Demo UI")
st.write("Dies ist eine einfache Benutzeroberfläche zur Interaktion mit einem einzelnen OpenSearch-Knoten.")

# --- Sidebar Configuration ---
st.sidebar.header("OpenSearch Verbindung")
os_host = st.sidebar.text_input("Host", "localhost")
os_port = st.sidebar.number_input("Port", 1, 65535, 9200)
os_user = st.sidebar.text_input("Benutzer", "admin")
# Use Streamlit's password input for security
os_password = st.sidebar.text_input("Passwort", type="password", value="Ag4skH8KV8mxee7n5XouNNd2ooA5JC") # <-- CHANGE DEFAULT IF NEEDED

# --- Helper Function to Get Client ---
# Use st.cache_resource to avoid reconnecting unnecessarily if config doesn't change
# Note: Caching might keep connections open longer than desired in some scenarios.
# For this simple demo, it's generally fine. Consider scope if expanding.
@st.cache_resource(ttl=300) # Cache client for 5 minutes
def get_opensearch_client(host, port, user, password):
    """Creates and returns an OpenSearch client instance."""
    client = None
    error_message = ""
    try:
        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=(user, password),
            use_ssl=True,            # Assuming HTTPS based on previous setup
            verify_certs=False,      # For self-signed certs (like curl -k)
            ssl_show_warn=False      # Suppress SSL warnings in Streamlit app
        )
        # Basic check to see if connection works
        if not client.ping():
             raise exceptions.ConnectionError("Ping failed: Cannot connect to OpenSearch.")
        st.sidebar.success("Verbindung erfolgreich!") # Feedback in sidebar
    except exceptions.AuthenticationException:
        error_message = "Authentifizierung fehlgeschlagen. Bitte überprüfen Sie Benutzername und Passwort."
    except exceptions.ConnectionError as e:
        error_message = f"Verbindungsfehler: {e}. Stellen Sie sicher, dass OpenSearch läuft und die Host/Port-Angaben korrekt sind."
    except Exception as e:
        error_message = f"Ein unerwarteter Fehler ist aufgetreten: {e}"

    if error_message:
        st.sidebar.error(error_message)
        return None # Return None if connection failed

    return client

# --- Main Application Logic ---
client = get_opensearch_client(os_host, os_port, os_user, os_password)

if not client:
    st.warning("OpenSearch-Client konnte nicht erstellt werden. Bitte überprüfen Sie die Verbindungseinstellungen in der Seitenleiste und stellen Sie sicher, dass OpenSearch läuft.")
else:
    # --- Section 1: Check Cluster Info ---
    st.header("1. Cluster Status überprüfen")
    if st.button("Cluster Info abrufen"):
        with st.spinner("Rufe Cluster-Informationen ab..."):
            try:
                info = client.info()
                st.json(info)
            except exceptions.ConnectionError as e:
                st.error(f"Verbindungsfehler beim Abrufen der Info: {e}")
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Info: {e}")

    st.divider() # Visual separator

    # --- Section 2: Index Document ---
    st.header("2. Dokument indizieren")
    index_name_index = st.text_input("Index Name (zum Indizieren)", "my-demo-index")
    doc_id = st.text_input("Dokumenten-ID (optional, leer lassen für Auto-Generierung)", "")
    st.write("Dokumenteninhalt (JSON):")
    doc_body_json = st.text_area("JSON Body", value='{\n  "name": "Test Dokument",\n  "value": 123,\n  "tags": ["demo", "streamlit"]\n}', height=150)

    if st.button("Dokument indizieren"):
        if not index_name_index:
            st.warning("Bitte geben Sie einen Indexnamen an.")
        else:
            try:
                # Validate JSON
                document = json.loads(doc_body_json)

                with st.spinner(f"Indiziere Dokument in '{index_name_index}'..."):
                    params = {'index': index_name_index, 'body': document, 'refresh': True} # Refresh=True for immediate searchability (demo only)
                    if doc_id:
                         params['id'] = doc_id

                    response = client.index(**params)
                    st.success(f"Dokument erfolgreich indiziert in '{index_name_index}'!")
                    st.json(response)

            except json.JSONDecodeError:
                st.error("Ungültiges JSON im Dokumenteninhalt. Bitte korrigieren Sie es.")
            except exceptions.RequestError as e:
                 st.error(f"Fehler bei der Indizierungsanfrage: Status {e.status_code}, Info: {e.info}")
            except exceptions.ConnectionError as e:
                st.error(f"Verbindungsfehler beim Indizieren: {e}")
            except Exception as e:
                st.error(f"Fehler beim Indizieren: {e}")

    st.divider()

    # --- Section 3: Search Documents ---
    st.header("3. Dokumente suchen")
    index_name_search = st.text_input("Index Name (zum Suchen)", "my-demo-index")
    # Simple query string search for demo purposes
    search_query = st.text_input("Suchanfrage (einfache Abfragezeichenkette)", "tags:demo")

    if st.button("Suchen"):
        if not index_name_search:
            st.warning("Bitte geben Sie einen Indexnamen für die Suche an.")
        else:
            with st.spinner(f"Suche in '{index_name_search}'..."):
                try:
                    # Using a simple query_string query
                    search_body = {
                        'query': {
                            'query_string': {
                                'query': search_query
                            }
                        }
                    }
                    response = client.search(
                        index=index_name_search,
                        body=search_body
                    )

                    st.success(f"Suche abgeschlossen. {response['hits']['total']['value']} Treffer gefunden.")
                    # Display results
                    if response['hits']['hits']:
                        st.write("Treffer:")
                        # Nicely format hits
                        for hit in response['hits']['hits']:
                            st.json({
                                "_id": hit.get('_id'),
                                "_score": hit.get('_score'),
                                "_source": hit.get('_source')
                            })
                    else:
                        st.info("Keine Dokumente entsprechen Ihrer Anfrage.")

                except exceptions.NotFoundError:
                    st.error(f"Index '{index_name_search}' nicht gefunden.")
                except exceptions.RequestError as e:
                     st.error(f"Fehler bei der Suchanfrage: Status {e.status_code}, Info: {e.info}")
                except exceptions.ConnectionError as e:
                    st.error(f"Verbindungsfehler bei der Suche: {e}")
                except Exception as e:
                    st.error(f"Fehler bei der Suche: {e}")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.info("Stellen Sie sicher, dass Ihr OpenSearch-Container über Podman läuft und zugänglich ist.")