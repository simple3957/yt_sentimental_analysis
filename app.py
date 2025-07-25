import streamlit as st
import os
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats
import plotly.graph_objects as go

# --- Clean up old CSVs ---
def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

# --- Page Config ---
st.set_page_config(page_title='YouTube Sentiment Analyzer', page_icon='🎬', layout="wide")

# --- Modern CSS & Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f8f9fa 0%, #cfe9f1 100%) !important;
    }
    .block-container {
        padding: 2rem 3rem;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff !important;
        border: 2px solid #6c63ff !important;
        color: #333 !important;
        font-weight: 500;
        padding: 0.6rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
    }
    .stButton>button {
        background: linear-gradient(90deg, #6c63ff 0%, #48c6ef 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #48c6ef 0%, #6c63ff 100%);
        transform: scale(1.05);
        color: #fff;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #2f3542 0%, #57606f 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.5rem 1rem;
    }
    h1, h2, h4 {
        text-align: center;
        color: #2d3436;
    }
    .stMetric { text-align: center; }
    .stPlotlyChart {
        padding: 1rem;
        border-radius: 15px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .card {
        background-color: #ffffff;
        padding: 1rem 2rem;
        margin: 1rem 0;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    #MainMenu, footer {visibility: hidden;}
    section[data-testid="stSidebar"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# --- Page Title ---
st.markdown("<h1>YouTube Sentiment Analyzer 🎬</h1>", unsafe_allow_html=True)
st.markdown("<h4>Get instant, colorful insights into YouTube comments with interactive visuals!</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- Input Section ---
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    youtube_link = st.text_input("", placeholder="Paste YouTube Video URL here", key="url_input")
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

directory_path = os.getcwd()

if analyze_btn and youtube_link:
    video_id = extract_video_id(youtube_link)
    channel_id = get_channel_id(video_id)

    if video_id:
        with st.spinner("Fetching comments and channel info..."):
            csv_file = save_video_comments_to_csv(video_id)
            delete_non_matching_csv_files(directory_path, video_id)
            st.success("Comments saved to CSV!")
            st.download_button(
                label="⬇️ Download Comments",
                data=open(csv_file, 'rb').read(),
                file_name=os.path.basename(csv_file),
                mime="text/csv"
            )
            channel_info = get_channel_info(youtube, channel_id)
            stats = get_video_stats(video_id)
            results = analyze_sentiment(csv_file)

        # --- Channel Overview ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📺 Channel Overview")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(channel_info['channel_logo_url'], width=120)
        with col2:
            st.markdown(f"<h2 style='color:#6c63ff;'>{channel_info['channel_title']}</h2>", unsafe_allow_html=True)
            st.markdown(f"**Created:** {channel_info['channel_created_date'][:10]}")
            st.markdown(f"**Subscribers:** {int(channel_info['subscriber_count']):,}")
            st.markdown(f"**Total Videos:** {channel_info['video_count']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Video Overview ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎥 Video Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Views", f"{int(stats['viewCount']):,}")
        col2.metric("Likes", f"{int(stats['likeCount']):,}")
        col3.metric("Comments", f"{int(stats['commentCount']):,}")
        st.video(youtube_link)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Sentiment Result ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Sentiment Analysis")
        col1, col2, col3 = st.columns(3)
        col1.success(f"😊 Positive: {results['num_positive']}")
        col2.error(f"😠 Negative: {results['num_negative']}")
        col3.info(f"😐 Neutral: {results['num_neutral']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Pie Chart ---
        st.markdown("### 🧁 Sentiment Distribution")
        labels = ['Positive', 'Negative', 'Neutral']
        values = [results['num_positive'], results['num_negative'], results['num_neutral']]
        colors = ['#43e97b', '#ff6f61', '#ffd166']

        fig = go.Figure(
            data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors, line=dict(color='#232946', width=4)),
                hole=0.45,
                pull=[0.12, 0.08, 0.10],
                textinfo='label+percent+value',
                hoverinfo='label+value+percent',
                rotation=30,
                direction='clockwise'
            )]
        )
        fig.update_traces(textfont_size=20, opacity=0.96)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text="Sentiment", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Sentiment Over Time ---
        st.markdown("### ⏳ Sentiment Over Time")
        plot_sentiment(csv_file)

        # --- Channel Description ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Channel Description")
        st.info(channel_info['channel_description'])
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("❌ Invalid YouTube link provided.")
elif not youtube_link:
    st.markdown(
        "<div style='text-align:center; color:#6c63ff; font-size:18px; font-weight:bold;'>"
        "Paste a YouTube video link and click <span style='color:#232946;'>Analyze</span> to get started!"
        "</div>",
        unsafe_allow_html=True
    )
