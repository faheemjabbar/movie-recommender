import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os
from fuzzywuzzy import process

# 🎬 Page setup
st.set_page_config(
    page_title="Movie Recommender 🍿",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 Custom CSS
st.markdown("""
    <style>
        .block-container { max-width: 1100px; padding-top: 2rem; margin: auto; }
        .centered-title { text-align: center; font-size: 3rem; font-weight: 800; margin-bottom: 0.4em; }
        .subtext { text-align: center; font-size: 1.1rem; color: #888; margin-bottom: 2rem; }
        .input-row { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; margin-bottom: 1.5rem; }
        .input-row > div { flex: 1 1 300px; min-width: 280px; }
        .movie-card { background: #1e1e1e; border-radius: 15px; box-shadow: 0 6px 20px rgba(0,0,0,0.5); padding: 12px; transition: transform 0.2s ease; text-align: center; }
        .movie-card:hover { transform: scale(1.05); background-color: #2c2c2c; }
        .movie-card img { width: 100%; height: 250px; object-fit: cover; border-radius: 10px; }
        .caption { font-weight: 600; font-size: 0.95rem; margin-top: 8px; color: #f2f2f2; }
        .footer { text-align: center; font-size: 0.9rem; color: gray; margin-top: 3rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered-title">🍿 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Smart suggestions based on your favorite movies. Filter by genre for better results.</div>', unsafe_allow_html=True)

# 🔗 Google Drive file download
def download_file_from_gdrive(file_id, filename):
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)

download_file_from_gdrive("13I-OMsK5Y02Jdui0_EowYp_z1F751kA7", "movies.pkl")
download_file_from_gdrive("1eJsG9WEW7ZvkhngmCFW35ve3JLlqY7Xx", "similarity.pkl")

# 📦 Load data
with open("movies.pkl", "rb") as f:
    movies = pickle.load(f)
with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

# ✅ Check required columns
required_columns = {'movie_id', 'title', 'tags', 'genres'}
if not required_columns.issubset(movies.columns):
    st.error(f"❌ movies.pkl is missing columns: {required_columns - set(movies.columns)}")
    st.stop()

# 🎭 Get unique genres
all_genres = sorted(set(genre for sublist in movies['genres'] for genre in sublist))

# 🖼️ TMDb API for poster fetching
API_KEY = '14f7934a7db114bebfa0e6cd22de461c'
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        data = requests.get(url).json()
        return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', "")
    except:
        return ""

# 🔍 Fuzzy search function
def search_movie(query):
    all_titles = movies['title'].tolist()
    matches = process.extract(query, all_titles, limit=5)
    return [match[0] for match in matches]

# 🎯 Recommendation logic
def recommend(movie, genre_filter="All"):
    movie = movie.lower()
    matched_title = None

    if movie in movies['title'].str.lower().values:
        matched_title = movies[movies['title'].str.lower() == movie].iloc[0]['title']
    else:
        match = process.extractOne(movie, movies['title'].tolist())
        if match:
            matched_title = match[0]
        else:
            return [], []

    idx = movies[movies['title'] == matched_title].index[0]
    distances = similarity[idx]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])

    recommended_titles, recommended_posters = [], []

    for i in movie_list:
        if len(recommended_titles) == 5:
            break

        movie_row = movies.iloc[i[0]]
        if genre_filter != "All" and genre_filter not in movie_row['genres']:
            continue

        recommended_titles.append(movie_row.title)
        recommended_posters.append(fetch_poster(movie_row.movie_id))

    return recommended_titles, recommended_posters

# 🎛️ UI Inputs
st.markdown("""<div class="input-row"><div>""", unsafe_allow_html=True)
movie_input = st.text_input("🎥 Type a movie name", "")
st.markdown("""</div><div>""", unsafe_allow_html=True)
selected_genre = st.selectbox("🎭 Genre Filter", ["All"] + all_genres)
st.markdown("""</div></div>""", unsafe_allow_html=True)

# 🚀 Recommend button
if st.button("🌟 Recommend"):
    if not movie_input.strip():
        st.warning("Please enter a movie name first.")
    else:
        with st.spinner("🔎 Fetching recommendations..."):
            titles, posters = recommend(movie_input, selected_genre)

        if titles:
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                if idx < len(titles):
                    with col:
                        st.markdown(f"""
                            <div class='movie-card'>
                                <img src='{posters[idx]}' alt='{titles[idx]} poster' />
                                <div class='caption'>{titles[idx][:30]}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.error("❌ No recommendations found for this movie and genre.")

# 📅 Footer
st.markdown('<div class="footer">Built with ❤️ using Streamlit & TMDb API · by Faheem Jabbar</div>', unsafe_allow_html=True)
