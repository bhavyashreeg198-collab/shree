import streamlit as st
import wikipedia
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from serpapi import GoogleSearch

# 🔑 Set your SerpAPI key here
SERPAPI_API_KEY = "fce17740e791506ab7a08b223ee7f12ccd7126ef5e6930635a6ff4f431e2bb8f"  # ← Replace with your real key

# ------------------- Streamlit Page Config ------------------- #
st.set_page_config(page_title="DJ BAK", layout="wide")
st.title("🔰 DJ BAK ")

# ------------------- Tabs ------------------- #
tab1, tab2 = st.tabs(["💬 Chatbot", "🗺️ Map Viewer"])

# ------------------- Helper Functions ------------------- #

def get_wikipedia_summary(query):
    try:
        results = wikipedia.search(query)
        if not results:
            return "❌ Sorry, I couldn't find anything on that topic."
        summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False, redirect=True)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"⚠️ Your query is ambiguous, did you mean: {', '.join(e.options[:5])}?"
    except wikipedia.PageError:
        return "❌ Sorry, I couldn't find a page matching your query."
    except Exception:
        return "😱 Oops, something went wrong."

def get_google_answer(query):
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "hl": "en"
        })
        results = search.get_dict()

        # Try answer box first
        if "answer_box" in results:
            ab = results["answer_box"]
            if "answer" in ab:
                return ab["answer"]
            elif "snippet" in ab:
                return ab["snippet"]
            elif "highlighted_words" in ab:
                return ', '.join(ab["highlighted_words"])

        # Fall back to first organic result
        if "organic_results" in results and len(results["organic_results"]) > 0:
            return results["organic_results"][0]["snippet"]

        return "❌ Couldn't find an answer from Google."
    except Exception as e:
        return f"⚠️ Google search failed: {str(e)}"

# ------------------- TAB 1: Chatbot ------------------- #
with tab1:
    st.header("🤖 Chatbot")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Choose search source
    search_engine = st.radio("Choose Info Source", ["Wikipedia", "Google"], horizontal=True)

    # User input
    user_input = st.text_input("What's on your mind!?")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            if search_engine == "Wikipedia":
                bot_response = get_wikipedia_summary(user_input)
            else:
                bot_response = get_google_answer(user_input)

        st.session_state.messages.append({"role": "bot", "content": bot_response})

    # Chat display
    for msg in st.session_state.messages:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
        st.markdown(f"**{role}:** {msg['content']}")

    # Buttons
    st.markdown("<div style='height:300px;'></div>", unsafe_allow_html=True)
    _, _, col1, col2, col3 = st.columns([5, 1, 1.5, 1.5, 1])

    with col1:
        if st.button("About Me"):
            st.info("👋 Hi! I am DJ BAK, your friendly info assistant powered by Wikipedia and Google! also useful to search locations📍")

    with col2:
        if st.button("Features"):
            st.info("💡 Ask me anything! I can fetch quick summaries from Wikipedia or search answers on Google or search places from maps🗺️✈️")

    with col3:
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []

# ------------------- TAB 2: Map Viewer ------------------- #
with tab2:
    st.header("🌐 Map Viewer")

    # Sidebar
    st.sidebar.header("🛠️ Map Options")
    map_type = st.sidebar.selectbox("Map View Type", ["Normal", "Satellite"])
    show_route = st.sidebar.checkbox("Show Route Between Two Points")

    # Geolocation
    geolocator = Nominatim(user_agent="streamlit_map_app")

    # Inputs
    locations = []
    location_1 = st.text_input("Enter Location 1:")
    location_2 = st.text_input("Enter Location 2 (Optional):")

    loc1, loc2 = None, None

    if location_1:
        with st.spinner("Locating..."):
            loc1 = geolocator.geocode(location_1)
        if loc1:
            locations.append((loc1.latitude, loc1.longitude, loc1.address))
            st.success(f"📍 Location 1 found: {loc1.address}")
        else:
            st.error("❌ Location 1 not found.")

    if location_2:
        with st.spinner("Locating..."):
            loc2 = geolocator.geocode(location_2)
        if loc2:
            locations.append((loc2.latitude, loc2.longitude, loc2.address))
            st.success(f"📍 Location 2 found: {loc2.address}")
        else:
            st.error("❌ Location 2 not found.")

    # Display map
    if locations:
        avg_lat = sum([lat for lat, _, _ in locations]) / len(locations)
        avg_lon = sum([lon for _, lon, _ in locations]) / len(locations)
        tiles = "OpenStreetMap" if map_type == "Normal" else "Esri Satellite"
        zoom = 15 if len(locations) == 1 else 12

        map_ = folium.Map(location=[avg_lat, avg_lon], zoom_start=zoom, tiles=tiles)

        for i, (lat, lon, address) in enumerate(locations):
            icon_color = "green" if i == 0 else "red"
            folium.Marker(
                [lat, lon],
                popup=address,
                tooltip=address,
                icon=folium.Icon(color=icon_color)
            ).add_to(map_)

        if show_route and len(locations) == 2:
            folium.PolyLine(
                [(locations[0][0], locations[0][1]), (locations[1][0], locations[1][1])],
                color="blue", weight=4, opacity=0.7
            ).add_to(map_)

        st.subheader("🗺️ Map")
        st_folium(map_, width=800, height=500)
    else:
        st.info("Enter at least one valid location to display the map.")

