import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDb API Key
API_KEY = '14f7934a7db114bebfa0e6cd22de461c'

# Fetch poster using movie_id
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    data = requests.get(url).json()
    return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', "")

# Recommendation logic
def recommend(movie):
    movie = movie.lower()
    if movie not in movies['title'].str.lower().values:
        return [], []

    idx = movies[movies['title'].str.lower() == movie].index[0]
    distances = similarity[idx]
    movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# Streamlit UI
st.title("🎬 Movie Recommender")

movie_name = st.text_input("Enter a movie title:")

if st.button("Recommend"):
    if movie_name.strip() == "":
        st.warning("Please enter a movie name.")
    else:
        names, posters = recommend(movie_name)
        if names:
            st.subheader("You might also like:")
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    st.image(posters[idx])
                    st.caption(names[idx])
        else:
            st.error("❌ Movie not found. Please try a different title.")
