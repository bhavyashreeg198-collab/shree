import streamlit as st
import wikipedia
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Set page configuration
st.set_page_config(page_title="DJ BAK", layout="wide")

st.title("🔰 DJ BAK ")

# Create two tabs: Chatbot & Map Viewer
tab1, tab2 = st.tabs(["💬 Chatbot", "🗺️ Map Viewer"])

# ---------------- TAB 1: Chatbot ---------------- #
with tab1:
    st.header("🤖 Chatbot")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def get_wikipedia_summary(query):
        try:
            results = wikipedia.search(query)
            if not results:
                return "Sorry, I couldn't find anything on that topic."

            summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False, redirect=True)
            return summary
        except wikipedia.DisambiguationError as e:
            return f"Your query is ambiguous, did you mean: {', '.join(e.options[:5])}?"
        except wikipedia.PageError:
            return "Sorry, I couldn't find a page matching your query 😟"
        except Exception:
            return "Oops, something went wrong 😱"

    user_input = st.text_input("What's on your mind!?")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        bot_response = get_wikipedia_summary(user_input)
        st.session_state.messages.append({"role": "bot", "content": bot_response})

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

    # Buttons aligned right
    st.markdown("<div style='height:400px;'></div>", unsafe_allow_html=True)
    _, _, col1, col2 = st.columns([6, 1, 1.5, 1.5])

    with col1:
        if st.button("About Me"):
            st.info("👋 Hi! I am DJ BAK, your friendly info assistant powered by Wikipedia.")

    with col2:
        if st.button("Features"):
            st.info("💡 Ask me about any topic and I’ll fetch a quick summary from Wikipedia!")

# ---------------- TAB 2: Map Viewer ---------------- #
with tab2:
    st.header("🌐 Map Viewer")

    # Sidebar options
    st.sidebar.header("🛠️ Map Options")
    map_type = st.sidebar.selectbox("Map View Type", ["Normal", "Satellite"])
    show_route = st.sidebar.checkbox("Show Route Between Two Points")

    # Geocoder
    geolocator = Nominatim(user_agent="streamlit_map_app")

    # Input fields
    locations = []
    location_1 = st.text_input("Enter Location 1:")
    location_2 = st.text_input("Enter Location 2 (Optional):")

    loc1, loc2 = None, None

    if location_1:
        loc1 = geolocator.geocode(location_1)
        if loc1:
            locations.append((loc1.latitude, loc1.longitude, loc1.address))
            st.success(f"📍 Location 1 found: {loc1.address}")
        else:
            st.error("Location 1 not found.")

    if location_2:
        loc2 = geolocator.geocode(location_2)
        if loc2:
            locations.append((loc2.latitude, loc2.longitude, loc2.address))
            st.success(f"📍 Location 2 found: {loc2.address}")
        else:
            st.error("Location 2 not found.")

    # Show map if valid locations
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
            route_coords = [(locations[0][0], locations[0][1]), (locations[1][0], locations[1][1])]
            folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.7).add_to(map_)

        st.subheader("🗺️ Map")
        st_folium(map_, width=800, height=500)
    else:
        st.info("Enter at least one valid location to display the map.")