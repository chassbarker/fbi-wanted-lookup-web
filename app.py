"""FBI public listing browser by Chassidy Barker.

Run: python -m streamlit run app.py
Source: https://www.fbi.gov/wanted/api
AI assistance: ChatGPT assisted with adapting the course CLI to Streamlit.
"""
from datetime import datetime, timezone
from html import unescape
import re
from urllib.parse import urlsplit

import requests
import streamlit as st

API_URL = "https://api.fbi.gov/wanted/v1/list"


def clean_text(value, fallback="Not provided"):
    """Convert API HTML snippets into plain display text."""
    if not isinstance(value, str) or not value.strip():
        return fallback
    return unescape(re.sub(r"<[^>]*>", " ", value)).strip()


def official_link(value):
    """Only offer HTTPS links on the official FBI domain."""
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    if parsed.scheme == "https" and parsed.hostname in {"fbi.gov", "www.fbi.gov"}:
        return value
    return None


@st.cache_data(ttl=300, max_entries=100, show_spinner=False)
def fetch_listings(office, page):
    """Fetch one page and cache identical searches for five minutes."""
    params = {"page": page}
    if office:
        params["field_offices"] = office
    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Unexpected response format")
    items = [item for item in data["items"] if isinstance(item, dict)]
    return items, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main():
    st.set_page_config(page_title="FBI Wanted Lookup | Chassidy Barker", page_icon="🔎", layout="centered")
    st.caption("A PYTHON API PROJECT BY CHASSIDY BARKER")
    st.title("FBI Wanted Lookup")
    st.write("Explore public FBI listings by field office. Find case descriptions and open the official pages for details.")
    with st.form("search"):
        office_name = st.text_input("FBI field office", placeholder="San Antonio, Miami, or leave blank for all offices", max_chars=60)
        left, right = st.columns(2)
        page = left.number_input("Results page", min_value=1, max_value=1000, value=1, step=1)
        limit = right.selectbox("Listings to display", [5, 10, 20])
        submitted = st.form_submit_button("Search FBI listings", type="primary", use_container_width=True)
    if submitted:
        office = re.sub(r"[\s-]+", "", office_name.strip().lower())
        if office and not office.isascii() or (office and not office.isalpha()):
            st.error("Enter a field office name using letters and spaces.")
        else:
            try:
                with st.spinner("Retrieving public listings..."):
                    items, retrieved = fetch_listings(office, int(page))
                st.session_state["results"] = (items, retrieved, office_name.strip() or "All offices", int(page), limit)
            except requests.Timeout:
                st.session_state.pop("results", None)
                st.error("The FBI service took too long to respond. Please try again later.")
            except requests.RequestException:
                st.session_state.pop("results", None)
                st.error("Unable to retrieve listings right now. Check your connection or try again later.")
            except ValueError:
                st.session_state.pop("results", None)
                st.error("The service returned an unexpected response. Please try again later.")
    if "results" in st.session_state:
        items, retrieved, label, selected_page, limit = st.session_state["results"]
        st.subheader(label)
        st.caption(f"Page {selected_page} · Retrieved {retrieved} · Identical searches cached for five minutes")
        if not items:
            st.info("No listings found on this page. Check the office name or try page 1.")
        else:
            st.caption(f"Showing {min(limit, len(items))} of {len(items)} listings returned on this page.")
            for item in items[:limit]:
                with st.container(border=True):
                    st.subheader(clean_text(item.get("title"), "Untitled listing"))
                    st.text(clean_text(item.get("description"), "No description provided."))
                    link = official_link(item.get("url"))
                    if link:
                        st.link_button("View official FBI listing", link)
    st.divider()
    st.caption("Source: FBI Wanted API · Independent educational project; not affiliated with the FBI. Listings may include wanted persons, missing persons, and requests for information. A listing does not establish guilt. Check the official page for current details.")
    st.markdown("[FBI data source and documentation](https://www.fbi.gov/wanted/api)")


if __name__ == "__main__":
    main()
