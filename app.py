import streamlit as st
import requests
import json

# --- Configuration ---
FASTAPI_BASE_URL = "http://localhost:8000" # Adjust if needed
SEARCH_ENDPOINT = f"{FASTAPI_BASE_URL}/open-ai-embeddings/search"
MAX_DESC_LENGTH = 350 # Allow slightly longer description in wide layout

# --- Initialize Session State ---
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# --- Helper Function to Call API ---
# (Same robust function as before)
def call_api(url: str, params: dict) -> dict | None:
    """Makes a GET request to the specified API endpoint."""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.Timeout:
        st.error("API request timed out. The server might be busy.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API at {url}. Is the backend running?")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response status: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                st.error(f"Server error detail: {error_detail}")
            except json.JSONDecodeError:
                st.error(f"Raw server response: {e.response.text[:500]}...")
        return None
    except json.JSONDecodeError:
        st.error(f"Failed to decode JSON response from API. Raw response: {response.text[:500]}...")
        return None

# --- Helper Function for Truncation ---
def truncate_text(text: str, max_length: int) -> str:
    """Truncates text and adds ellipsis if it exceeds max_length."""
    if len(text) > max_length:
        # Find the last space before the limit to avoid cutting mid-word
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + "..."
    return text

# --- Streamlit App Layout ---
# <<< Set layout to wide >>>
st.set_page_config(page_title="Semantic Product Search", layout="wide", page_icon="✨")

st.title("✨ Semantic Product Search")
st.caption("Enter a query to find semantically similar items in the OpenSearch index.")

# --- Search Form ---
with st.form(key="search_form"):
    search_query = st.text_input(
        "Search query",
        placeholder="e.g., healthy breakfast options or japanese soup broth",
        key="search_input_main_wide", # Ensure unique key
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Search")

    if submitted and search_query:
        st.session_state.last_query = search_query
        with st.spinner(f"Searching for items similar to '{search_query}'..."):
            params = {"text": search_query}
            api_response = call_api(SEARCH_ENDPOINT, params)
            st.session_state.search_results = api_response
            # Error messages handled by call_api

    elif submitted and not search_query:
        st.warning("Please enter a search query.")
        st.session_state.search_results = None
        st.session_state.last_query = ""

# --- Display Results ---
st.markdown("---")

if st.session_state.search_results:
    results_data = st.session_state.search_results.get("results", [])

    if not results_data:
        st.info(f"No results found for '{st.session_state.last_query}'. Try searching for something else!")
    else:
        # Displaying result count is often helpful
        st.subheader(f"Results for '{st.session_state.last_query}':")
        st.write("") # Add a bit of space before the first result

        for i, hit in enumerate(results_data):
            source_data = hit.get('_source', {})

            # --- Extract Data ---
            title = source_data.get('Summary', 'No Summary')
            description = source_data.get('Text', '')
            product_id = source_data.get('ProductId', 'N/A') # Get ProductId

            # --- Truncate ---
            truncated_description = truncate_text(description, MAX_DESC_LENGTH) if description else "No Description"

            # --- Render Result Item ---
            # Use columns for layout: main content | score
            # Adjust ratios for wide layout
            col1, col2 = st.columns([0.85, 0.15])

            with col1: # Main content column
                # Use markdown H4 or bold for title + an icon
                st.markdown(f"##### 📄 **{title}**") # Using H5 for slightly larger bold + icon
                st.caption(f"Product ID: {product_id}") # Show Product ID subtly
                st.write(truncated_description) # Show description

            with col2: # Score column
                st.metric(label="Similarity Score", value=f"{hit['_score']:.3f}")

            # --- Expander for Raw JSON (stays below columns) ---
            with st.expander("View Full Data (JSON)"):
                st.json(hit)

            st.divider() # Use st.divider for a cleaner line between results

# Handle cases where API failed on previous run (error shown then)
elif st.session_state.last_query and not submitted:
     pass

# Optional Footer
st.markdown("---")
st.caption("Powered by FastAPI, OpenSearch & OpenAI Embeddings. Products are based on Amazon Fine Food Reviews dataset (subset)")