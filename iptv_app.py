import streamlit as st
import requests
from streamlit_player import st_player

# Set up the page configuration with a theme
st.set_page_config(
    page_title="World IPTV Channels",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display the logo at the top of the page using an image URL
logo_url = "https://raw.githubusercontent.com/Arghayadasdev/World-IPTV-Channels/main/logo.png"
st.image(logo_url, width=200)  # Adjust width as necessary

# Initialize theme setting in session state, default to Dark theme
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"  # Default to Dark theme

# Sidebar controls
st.sidebar.title("Controls")

# Theme toggle switch
st.sidebar.markdown("### Theme")
st.session_state.theme = st.sidebar.radio("Choose Theme", ("Light", "Dark"))

# Define CSS for Light and Dark themes
light_theme_css = """
    <style>
        .stApp { background-color: #f8f9fa; }
        .title { font-size: 2.5em; font-weight: 600; color: #343a40; }
        .header { font-size: 1.5em; font-weight: 500; color: #495057; margin-top: 0.8em; }
        .channel-card {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
            padding: 0.8em;
            margin: 0.5em 0;
            color: #1860a8;
            font-weight: 500;
            cursor: pointer;
        }
        .channel-card:hover {
            background-color: #5d61d9;
            color: #ffffff;
        }
    </style>
"""

dark_theme_css = """
    <style>
        .stApp { background-color: #1e1e1e; }
        .title { font-size: 2.5em; font-weight: 600; color: #f0f0f0; }
        .header { font-size: 1.5em; font-weight: 500; color: #cccccc; margin-top: 0.8em; }
        .channel-card {
            background-color: #2b2b2b;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
            padding: 0.8em;
            margin: 0.5em 0;
            color: #79a7ff;
            font-weight: 500;
            cursor: pointer;
        }
        .channel-card:hover {
            background-color: #4c4cff;
            color: #ffffff;
        }
    </style>
"""

# Apply the selected theme CSS
if st.session_state.theme == "Light":
    st.markdown(light_theme_css, unsafe_allow_html=True)
else:
    st.markdown(dark_theme_css, unsafe_allow_html=True)

# Page Title
st.markdown("<div class='title'>🌐 World IPTV Channels</div>", unsafe_allow_html=True)

# URLs for main, live, and additional stream playlists
MAIN_M3U_URL = "https://raw.githubusercontent.com/Arghayadasdev/World-IPTV-Channels/refs/heads/main/bloginstall-iptv.m3u"
LIVE_M3U_URL = "https://raw.githubusercontent.com/FunctionError/PiratesTv/main/combined_playlist.m3u"
STREAM_M3U_URL = "https://raw.githubusercontent.com/imdhiru/bloginstall-iptv/main/bloginstall-bangla.m3u"

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
        st.error(f"Error fetching channels from {url}: {e}")
    return channels

# Load all channel lists
main_channels = load_channels(MAIN_M3U_URL)
live_channels = load_channels(LIVE_M3U_URL)
stream_channels = load_channels(STREAM_M3U_URL)

# Other sidebar controls
search_query = st.sidebar.text_input("Search Channels")
volume = st.sidebar.slider("Volume", 0, 100, 50)
playback_speed = st.sidebar.selectbox("Playback Speed", [0.5, 1.0, 1.5, 2.0], index=1)
is_playing = st.sidebar.checkbox("Playing", value=True)

# Filtering function
def filter_channels(channels, search_query):
    return [ch for ch in channels if search_query.lower() in ch["name"].lower()]

# Filtered channel lists based on search
filtered_main_channels = filter_channels(main_channels, search_query)
filtered_live_channels = filter_channels(live_channels, search_query)
filtered_stream_channels = filter_channels(stream_channels, search_query)

# Initialize session state for selected channel and visible channel counts
if 'selected_channel' not in st.session_state:
    st.session_state.selected_channel = filtered_main_channels[0] if filtered_main_channels else None
    st.session_state.selected_channel_index = 0

# Initialize session state for displayed channels if not already set
if 'main_channel_display_limit' not in st.session_state:
    st.session_state.main_channel_display_limit = 10
if 'live_channel_display_limit' not in st.session_state:
    st.session_state.live_channel_display_limit = 10
if 'stream_channel_display_limit' not in st.session_state:
    st.session_state.stream_channel_display_limit = 10

# Function to handle channel change
def change_channel(direction, channels):
    if not channels:
        return
    current_index = st.session_state.selected_channel_index
    new_index = (current_index + (1 if direction == "next" else -1)) % len(channels)
    st.session_state.selected_channel = channels[new_index]
    st.session_state.selected_channel_index = new_index

# Display the selected channel
st.markdown("<div class='header'>🎥 Now Playing</div>", unsafe_allow_html=True)
if st.session_state.selected_channel:
    st.subheader(f"{st.session_state.selected_channel['name']}")
    
    with st.spinner("Loading video..."):
        st_player(st.session_state.selected_channel['url'], playing=is_playing, volume=volume / 100.0, playback_rate=playback_speed)

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous Channel"):
            change_channel("prev", filtered_main_channels)
    with col3:
        if st.button("Next Channel"):
            change_channel("next", filtered_main_channels)
else:
    st.warning("No channel selected.")

# Tabbed interface for Main, Live, and Stream sections
tabs = st.tabs(["Main Channels", "Live Channels", "Stream Channels"])

# Function to display a limited list of channels with "Load More" button
def display_channel_list(channels, section_key, display_limit_key):
    display_limit = st.session_state[display_limit_key]
    
    if channels:
        # Display only up to the current limit of channels
        for i, channel in enumerate(channels[:display_limit]):
            if st.button(channel['name'], key=f"{section_key}_channel_{i}"):
                st.session_state.selected_channel = channel
                st.session_state.selected_channel_index = i
        
        # Show "Load More" button if there are more channels to display
        if len(channels) > display_limit:
            if st.button("Load More", key=f"{section_key}_load_more"):
                st.session_state[display_limit_key] += 10  # Increment display limit by 10
    else:
        st.warning(f"No channels available in {section_key.capitalize()} Channels.")

# Main Channels Tab
with tabs[0]:
    st.header("📺 Main Channels")
    display_channel_list(filtered_main_channels, "main", "main_channel_display_limit")

# Live Channels Tab
with tabs[1]:
    st.header("🔴 Live Channels")
    display_channel_list(filtered_live_channels, "live", "live_channel_display_limit")

# Stream Channels Tab
with tabs[2]:
    st.header("🌐 Stream Channels")
    display_channel_list(filtered_stream_channels, "stream", "stream_channel_display_limit")
