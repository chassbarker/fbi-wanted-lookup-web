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

# Display labels map to FBI field office identifiers.
FIELD_OFFICES = {
    "All offices": "",
    "Albany": "albany",
    "Albuquerque": "albuquerque",
    "Anchorage": "anchorage",
    "Atlanta": "atlanta",
    "Baltimore": "baltimore",
    "Birmingham": "birmingham",
    "Boston": "boston",
    "Buffalo": "buffalo",
    "Charlotte": "charlotte",
    "Chicago": "chicago",
    "Cincinnati": "cincinnati",
    "Cleveland": "cleveland",
    "Columbia": "columbia",
    "Dallas": "dallas",
    "Denver": "denver",
    "Detroit": "detroit",
    "El Paso": "elpaso",
    "Honolulu": "honolulu",
    "Houston": "houston",
    "Indianapolis": "indianapolis",
    "Jackson": "jackson",
    "Jacksonville": "jacksonville",
    "Kansas City": "kansascity",
    "Knoxville": "knoxville",
    "Las Vegas": "lasvegas",
    "Little Rock": "littlerock",
    "Los Angeles": "losangeles",
    "Louisville": "louisville",
    "Memphis": "memphis",
    "Miami": "miami",
    "Milwaukee": "milwaukee",
    "Minneapolis": "minneapolis",
    "Mobile": "mobile",
    "New Haven": "newhaven",
    "New Orleans": "neworleans",
    "New York": "newyork",
    "Newark": "newark",
    "Norfolk": "norfolk",
    "Oklahoma City": "oklahomacity",
    "Omaha": "omaha",
    "Philadelphia": "philadelphia",
    "Phoenix": "phoenix",
    "Pittsburgh": "pittsburgh",
    "Portland": "portland",
    "Richmond": "richmond",
    "Sacramento": "sacramento",
    "Salt Lake City": "saltlakecity",
    "San Antonio": "sanantonio",
    "San Diego": "sandiego",
    "San Francisco": "sanfrancisco",
    "San Juan": "sanjuan",
    "Seattle": "seattle",
    "Springfield": "springfield",
    "St. Louis": "stlouis",
    "Tampa": "tampa",
    "Washington": "washington"
}


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
def fetch_listings(office, page, classification=""):
    """Fetch one page and cache identical searches for five minutes."""
    params = {"page": page}
    if classification:
        params["poster_classification"] = classification
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
    st.set_page_config(page_title="FBI Public Case Explorer | Chassidy Barker", page_icon="🔎", layout="centered")
    st.markdown("""
    <style>
    .stApp {background: #f4f6fa; color: #17263d;}
    .block-container {max-width: 940px; padding-top: 2.5rem; padding-bottom: 3rem;}
    h1, h2, h3 {color: #14253e !important; letter-spacing: -.025em;}
    h1 {font-size: clamp(2.2rem, 6vw, 3.5rem) !important; font-weight: 800 !important;}
    p, label, .stCaption {color: #47576f;}
    [data-testid="stForm"] {background: white; border: 1px solid #dbe2ed; border-radius: 18px; padding: 1.5rem; box-shadow: 0 8px 28px #17263d08;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px;}
    [data-testid="stTextInput"] input {color: #17263d; background: #f8fafd;}
    .stFormSubmitButton button {background: #174c66; border: 0; border-radius: 10px; min-height: 3rem; font-weight: 650;}
    .stFormSubmitButton button p {color: white !important;}
    .stFormSubmitButton button:hover {background: #113b51;}
    [data-testid="stLinkButton"] a {border: 1px solid #c6d8e2; background: white; border-radius: 9px;}
    .eyebrow {font-size: .72rem; font-weight: 750; letter-spacing: .14em; color: #174c66; margin-bottom: .5rem;}
    .intro {font-size: 1.08rem; max-width: 620px; line-height: 1.7; margin-bottom: 1.5rem;}
    .empty-state {text-align: center; border: 1px dashed #cbd5e3; border-radius: 16px; padding: 2.2rem 1rem; margin-top: 1.8rem; background: #ffffff80;}
    .empty-state strong {color: #243b57; font-size: 1.1rem;}
    </style>
    <div class="eyebrow">INDEPENDENT PROJECT BY CHASSIDY BARKER</div>
    """, unsafe_allow_html=True)
    st.title("FBI Public Case Explorer")
    st.markdown('<p class="intro">Explore public FBI notices in one place. Search by field office, read a brief case summary, and go directly to the official listing.</p>', unsafe_allow_html=True)
    with st.form("search"):
        st.subheader("Find public listings")
        st.caption("Field offices cover regions, so results may include nearby cities.")
        office_name = st.selectbox("FBI field office", list(FIELD_OFFICES))
        listing_types = {"All listings": "", "Missing-person posters": "missing", "Ten Most Wanted posters": "ten", "Seeking information": "information"}
        listing_type = st.selectbox("Listing type", list(listing_types))
        st.caption("Types follow FBI poster classifications. Other missing-person notices may also appear under All listings. Posters may include captured or historical notices; check the official page for status.")
        left, right = st.columns(2)
        page = left.number_input("Results page", min_value=1, max_value=1000, value=1, step=1)
        limit = right.selectbox("Listings to display", [5, 10, 20])
        submitted = st.form_submit_button("Search FBI listings", type="primary", use_container_width=True)
    if submitted:
        office = FIELD_OFFICES[office_name]
        if office and not office.isascii() or (office and not office.isalpha()):
            st.error("Enter a field office name using letters and spaces.")
        else:
            try:
                with st.spinner("Retrieving public listings..."):
                    items, retrieved = fetch_listings(office, int(page), listing_types[listing_type])
                st.session_state["results"] = (items, retrieved, (office_name.strip() or "All offices") + " / " + listing_type, int(page), limit)
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
        st.subheader(f"Results · {label.title()}")
        st.caption(f"Page {selected_page} · Retrieved {retrieved} · Identical searches cached for five minutes")
        if not items:
            st.info("No listings found on this page. Check the office name or try page 1.")
        else:
            st.caption(f"Showing {min(limit, len(items))} of {len(items)} listings returned on this page.")
            for index, item in enumerate(items[:limit], start=1):
                with st.container(border=True):
                    subjects = item.get("subjects")
                    if not isinstance(subjects, list):
                        subjects = []
                    categories = [clean_text(value, "") for value in subjects if isinstance(value, str)]
                    category = " / ".join(value for value in categories if value) or {
                        "missing": "Missing-person poster",
                        "ten": "Ten Most Wanted poster",
                        "information": "Seeking information",
                    }.get(item.get("poster_classification"), "Public notice")
                    st.caption(f"PUBLIC LISTING {index:02d}")
                    st.text(f"FBI category: {category}")
                    st.subheader(clean_text(item.get("title"), "Untitled listing"))
                    st.text(clean_text(item.get("description"), "No description provided."))
                    link = official_link(item.get("url"))
                    if link:
                        st.link_button("View official FBI listing", link)
    else:
        st.markdown('<div class="empty-state"><strong>Your search starts here</strong><p>Choose a field office above, or select All offices to explore more listings.<br>Results can include wanted persons, missing persons, and requests for information.</p></div>', unsafe_allow_html=True)
    with st.expander("About this project"):
        st.write("I started this as a Python class assignment and expanded it into a public web app. My interest in true crime made it a practical way to learn how programs retrieve and display information from an API.")
        st.write("Built with Python, Streamlit, and requests. The app uses HTTP requests, JSON parsing, five-minute caching, and error handling. ChatGPT assisted with development.")
        st.markdown("[View the code on GitHub](https://github.com/chassbarker/fbi-wanted-lookup-web) · [Visit my portfolio](https://www.chassidybarker.com/)")
    st.divider()
    st.caption("Source: FBI Wanted API · Independent educational project; not affiliated with the FBI. Listings may include wanted persons, missing persons, and requests for information. A listing does not establish guilt. Check the official page for current details.")
    st.markdown("[FBI data source and documentation](https://www.fbi.gov/wanted/api)")


if __name__ == "__main__":
    main()
