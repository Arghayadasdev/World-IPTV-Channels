import streamlit as st
import requests
from streamlit_player import st_player

# Set up the page configuration
st.set_page_config(page_title="World IPTV Channels", layout="wide")

# Title
st.title("🎬 World IPTV Channels")

# URLs for main, live, and subcategory playlists
MAIN_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
LIVE_M3U_URL = "https://raw.githubusercontent.com/FunctionError/PiratesTv/main/combined_playlist.m3u"
CATEGORY_M3U_URL = "https://iptv-org.github.io/iptv/index.category.m3u"
LANGUAGE_M3U_URL = "https://iptv-org.github.io/iptv/index.language.m3u"
COUNTRY_M3U_URL = "https://iptv-org.github.io/iptv/index.country.m3u"
REGION_M3U_URL = "https://iptv-org.github.io/iptv/index.region.m3u"

# Load channels from M3U playlist with caching
@st.cache_data
def load_channels(url):
    channels = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                name = lines[i].split(",")[-1].strip()
                url = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if url.startswith("http"):
                    channels.append({"name": name, "url": url})
    except Exception as e:
        st.error(f"Error fetching channels: {e}")
    return channels

# Load all channel lists
main_channels = load_channels(MAIN_M3U_URL)
live_channels = load_channels(LIVE_M3U_URL)
category_channels = load_channels(CATEGORY_M3U_URL)
language_channels = load_channels(LANGUAGE_M3U_URL)
country_channels = load_channels(COUNTRY_M3U_URL)
region_channels = load_channels(REGION_M3U_URL)

# Sidebar controls
st.sidebar.title("Controls")
search_query = st.sidebar.text_input("Search Channels")
volume = st.sidebar.slider("Volume", 0, 100, 50)
is_playing = st.sidebar.checkbox("Playing", value=True)

# Sidebar subcategory filters
category_filter = st.sidebar.selectbox("Category", ["All"] + [ch["name"] for ch in category_channels])
language_filter = st.sidebar.selectbox("Language", ["All"] + [ch["name"] for ch in language_channels])
country_filter = st.sidebar.selectbox("Country", ["All"] + [ch["name"] for ch in country_channels])
region_filter = st.sidebar.selectbox("Region", ["All"] + [ch["name"] for ch in region_channels])

# Default playback speed
DEFAULT_PLAYBACK_SPEED = 1.0

# Function to filter channels based on selected subcategories
def filter_channels(channels, category, language, country, region, search_query):
    filtered = channels
    if category != "All":
        filtered = [ch for ch in filtered if category in ch["name"]]
    if language != "All":
        filtered = [ch for ch in filtered if language in ch["name"]]
    if country != "All":
        filtered = [ch for ch in filtered if country in ch["name"]]
    if region != "All":
        filtered = [ch for ch in filtered if region in ch["name"]]
    return [ch for ch in filtered if search_query.lower() in ch["name"].lower()]

# Filtered main and live channels
filtered_main_channels = filter_channels(main_channels, category_filter, language_filter, country_filter, region_filter, search_query)
filtered_live_channels = filter_channels(live_channels, category_filter, language_filter, country_filter, region_filter, search_query)

# Tabbed interface for Main and Live sections
tabs = st.tabs(["Main Channels", "Live Channels"])

# Initialize session state for visible channels and selected channels
if 'main_visible_count' not in st.session_state:
    st.session_state.main_visible_count = 10  # Start by showing 10 channels
if 'live_visible_count' not in st.session_state:
    st.session_state.live_visible_count = 10

# Main Channels Tab
with tabs[0]:
    st.header("📺 Main Channels")
    if filtered_main_channels:
        if "selected_main_channel" not in st.session_state:
            st.session_state.selected_main_channel = filtered_main_channels[0]

        selected_main_channel = st.session_state.selected_main_channel
        st.subheader(f"Now Playing: {selected_main_channel['name']}")
        
        # Display the player for the selected main channel
        with st.spinner("Loading video..."):
            st_player(selected_main_channel['url'], playing=is_playing, volume=volume / 100.0, playback_rate=DEFAULT_PLAYBACK_SPEED)

        # Display channel list with "Show More" button
        st.markdown("### Available Channels")
        for i, channel in enumerate(filtered_main_channels[:st.session_state.main_visible_count]):
            if st.button(channel['name'], key=f"main_channel_{i}"):
                st.session_state.selected_main_channel = channel
                is_playing = True

        # Show More button
        if st.session_state.main_visible_count < len(filtered_main_channels):
            if st.button("Show More Main Channels"):
                st.session_state.main_visible_count += 10

    else:
        st.warning("No channels match your search in Main Channels.")

# Live Channels Tab
with tabs[1]:
    st.header("🔴 Live Channels")
    if filtered_live_channels:
        if "selected_live_channel" not in st.session_state:
            st.session_state.selected_live_channel = filtered_live_channels[0]

        selected_live_channel = st.session_state.selected_live_channel
        st.subheader(f"Now Playing: {selected_live_channel['name']}")
        
        # Display the player for the selected live channel
        with st.spinner("Loading video..."):
            st_player(selected_live_channel['url'], playing=is_playing, volume=volume / 100.0, playback_rate=DEFAULT_PLAYBACK_SPEED)

        # Display channel list with "Show More" button
        st.markdown("### Available Channels")
        for i, channel in enumerate(filtered_live_channels[:st.session_state.live_visible_count]):
            if st.button(channel['name'], key=f"live_channel_{i}"):
                st.session_state.selected_live_channel = channel
                is_playing = True

        # Show More button
        if st.session_state.live_visible_count < len(filtered_live_channels):
            if st.button("Show More Live Channels"):
                st.session_state.live_visible_count += 10

    else:
        st.warning("No channels match your search in Live Channels.")
