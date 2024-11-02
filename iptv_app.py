import streamlit as st
import requests
from streamlit_player import st_player

# Set up the page configuration
st.set_page_config(page_title="World IPTV Channels", layout="wide")

# Title
st.title("🎬 World IPTV Channels")

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

# M3U URL
M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
channels = load_channels(M3U_URL)

# Sidebar for controls
st.sidebar.title("Controls")
search_query = st.sidebar.text_input("Search Channels")
volume = st.sidebar.slider("Volume", 0, 100, 50)
is_playing = st.sidebar.checkbox("Playing", value=True)

# Filter channels based on search
filtered_channels = [ch for ch in channels if search_query.lower() in ch["name"].lower()]

# Initialize session state for visible channels and playback speed
if 'visible_count' not in st.session_state:
    st.session_state.visible_count = 10  # Start by showing 10 channels

# Default playback speed
DEFAULT_PLAYBACK_SPEED = 1.0

# Display the selected channel in a player
if channels:
    if filtered_channels:
        if "selected_channel" not in st.session_state:
            st.session_state.selected_channel = filtered_channels[0]

        selected_channel = st.session_state.selected_channel
        st.subheader(f"Now Playing: {selected_channel['name']}")
        
        # Loading spinner for the player
        with st.spinner("Loading video..."):
            st_player(selected_channel['url'], playing=is_playing, volume=volume / 100.0, playback_rate=DEFAULT_PLAYBACK_SPEED)

        # Display the channel list with unique keys for each button
        st.markdown("### Available Channels")
        for i, channel in enumerate(filtered_channels[:st.session_state.visible_count]):
            if st.button(channel['name'], key=f"channel_{i}"):
                st.session_state.selected_channel = channel  # Update the selected channel
                is_playing = True  # Ensure the video plays
                # Reset playback speed to normal
                playback_speed = DEFAULT_PLAYBACK_SPEED

        # Show more button
        if st.session_state.visible_count < len(filtered_channels):
            if st.button("Show More"):
                st.session_state.visible_count += 10  # Increase the count of visible channels

    else:
        st.warning("No channels match your search.")

else:
    st.warning("No channels available.")
