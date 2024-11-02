import streamlit as st
import requests
from streamlit_player import st_player
from PIL import Image

# Set page configuration for a YouTube-like layout
st.set_page_config(page_title="World IPTV Channels", page_icon="🎬", layout="wide")

# Title and Subtitle
st.markdown("<h1 style='text-align: center; color: #FF0000;'>🎬 World IPTV Channels</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Discover and Stream Live Channels Like YouTube</h4>", unsafe_allow_html=True)

# URL for the M3U playlist
M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"

# Load channels from the M3U playlist
def load_channels(m3u_url):
    channels = []
    try:
        response = requests.get(m3u_url)
        response.raise_for_status()
        lines = response.text.splitlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                channel_name = lines[i].split(",")[-1].strip()
                channel_url = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if channel_url.startswith("http"):
                    channels.append({"name": channel_name, "url": channel_url})

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching channels: {e}")
    return channels

# Load the channels
channels = load_channels(M3U_URL)

# Sidebar for search functionality and video controls
st.sidebar.title("🔍 Search Channels")
search_query = st.sidebar.text_input("Enter channel name")
filtered_channels = [channel for channel in channels if search_query.lower() in channel["name"].lower()]

# Additional player controls in sidebar
st.sidebar.markdown("<h3>🎛️ Player Controls</h3>", unsafe_allow_html=True)
is_playing = st.sidebar.checkbox("Play/Pause", value=True)
volume_level = st.sidebar.slider("Volume", 0, 100, 50)
full_screen = st.sidebar.checkbox("Full Screen Mode", value=False)

# Display the selected channel in a large player
if channels:
    if filtered_channels:
        # Choose the first channel as the default or based on user's selection
        if "selected_channel" not in st.session_state:
            st.session_state.selected_channel = filtered_channels[0]

        # Displaying the selected channel's name and additional info
        st.markdown("<h2 style='color: #FF0000;'>Now Playing</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{st.session_state.selected_channel['name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Live Streaming | {volume_level}% Volume</p>", unsafe_allow_html=True)

        # Video player with additional controls
        st_player(
            st.session_state.selected_channel["url"],
            playing=is_playing,
            controls=True,
            volume=volume_level / 100.0,  # Normalize volume between 0 and 1
            playback_rate=1.0,
            height=500 if full_screen else 360  # Adjust height based on full-screen mode
        )

        # Grid view for channel previews
        st.markdown("<h2 style='color: #FF0000;'>Channels</h2>", unsafe_allow_html=True)
        cols = st.columns(4)  # Adjust the number of columns based on screen width
        for i, channel in enumerate(filtered_channels):
            with cols[i % 4]:
                if st.button(channel["name"], key=f"channel_{i}"):
                    st.session_state.selected_channel = channel
                    st.experimental_rerun()  # Refresh to show the selected channel in player

else:
    st.warning("No channels available at the moment. Please try again later.")

# Footer
st.markdown("<p style='text-align: center; color: gray;'>Powered by IPTV-Org</p>", unsafe_allow_html=True)
