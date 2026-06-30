from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],         
)

# ----------------------------
# Utility function
# ----------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

# ----------------------------
# Data
# ----------------------------
data = [
    # ---------------- MOVIES ----------------
    {"title": "The Dark Knight", "type": "movie", "genre": "action"},
    {"title": "Inception", "type": "movie", "genre": "sci-fi"},
    {"title": "Avengers Endgame", "type": "movie", "genre": "action"},
    {"title": "Interstellar", "type": "movie", "genre": "sci-fi"},
    {"title": "The Matrix", "type": "movie", "genre": "sci-fi"},
    {"title": "Joker", "type": "movie", "genre": "drama"},
    {"title": "Parasite", "type": "movie", "genre": "thriller"},
    {"title": "The Godfather", "type": "movie", "genre": "crime"},
    {"title": "Pulp Fiction", "type": "movie", "genre": "crime"},
    {"title": "Shutter Island", "type": "movie", "genre": "thriller"},
    {"title": "Titanic", "type": "movie", "genre": "romance"},
    {"title": "Gladiator", "type": "movie", "genre": "action"},
    {"title": "La La Land", "type": "movie", "genre": "musical"},
    {"title": "The Lion King", "type": "movie", "genre": "animation"},
    {"title": "Frozen", "type": "movie", "genre": "animation"},
    {"title": "The Conjuring", "type": "movie", "genre": "horror"},
    {"title": "It", "type": "movie", "genre": "horror"},
    {"title": "A Quiet Place", "type": "movie", "genre": "horror"},
    {"title": "Get Out", "type": "movie", "genre": "horror"},
    {"title": "Saw", "type": "movie", "genre": "horror"},
    {"title": "The Avengers", "type": "movie", "genre": "action"},
    {"title": "Iron Man", "type": "movie", "genre": "action"},
    {"title": "Black Panther", "type": "movie", "genre": "action"},
    {"title": "Doctor Strange", "type": "movie", "genre": "action"},
    {"title": "Thor: Ragnarok", "type": "movie", "genre": "action"},
    {"title": "The Hangover", "type": "movie", "genre": "comedy"},
    {"title": "Step Brothers", "type": "movie", "genre": "comedy"},
    {"title": "Superbad", "type": "movie", "genre": "comedy"},
    {"title": "Deadpool", "type": "movie", "genre": "comedy"},
    {"title": "Guardians of the Galaxy", "type": "movie", "genre": "action"},
    {"title": "Zombieland", "type": "movie", "genre": "comedy"},
    {"title": "Jumanji", "type": "movie", "genre": "adventure"},
    {"title": "The Grand Budapest Hotel", "type": "movie", "genre": "comedy"},
    {"title": "Jojo Rabbit", "type": "movie", "genre": "comedy"},
    {"title": "Crazy Rich Asians", "type": "movie", "genre": "romance"},
    {"title": "Bridesmaids", "type": "movie", "genre": "comedy"},
    {"title": "Night at the Museum", "type": "movie", "genre": "comedy"},
    {"title": "Shrek", "type": "movie", "genre": "animation"},
    {"title": "Kung Fu Panda", "type": "movie", "genre": "animation"},
    {"title": "Finding Nemo", "type": "movie", "genre": "animation"},
    
    # ---------------- GAMES ----------------
    {"title": "God of War", "type": "game", "genre": "action"},
    {"title": "FIFA 23", "type": "game", "genre": "sports"},
    {"title": "Minecraft", "type": "game", "genre": "adventure"},
    {"title": "The Witcher 3", "type": "game", "genre": "rpg"},
    {"title": "Cyberpunk 2077", "type": "game", "genre": "rpg"},
    {"title": "Spider-Man: Miles Morales", "type": "game", "genre": "action"},
    {"title": "Horizon Forbidden West", "type": "game", "genre": "action"},
    {"title": "Elden Ring", "type": "game", "genre": "rpg"},
    {"title": "Forza Horizon 5", "type": "game", "genre": "racing"},
    {"title": "Call of Duty: Modern Warfare", "type": "game", "genre": "shooter"},
    {"title": "League of Legends", "type": "game", "genre": "moba"},
    {"title": "Among Us", "type": "game", "genre": "party"},
    {"title": "Genshin Impact", "type": "game", "genre": "rpg"},
    {"title": "Valorant", "type": "game", "genre": "shooter"},
    {"title": "Assassin’s Creed Valhalla", "type": "game", "genre": "action"},
    {"title": "Stardew Valley", "type": "game", "genre": "simulation"},
    {"title": "The Sims 4", "type": "game", "genre": "simulation"},
    {"title": "Age of Empires IV", "type": "game", "genre": "strategy"},
    {"title": "Civilization VI", "type": "game", "genre": "strategy"},
    {"title": "Portal 2", "type": "game", "genre": "puzzle"},
    {"title": "Overwatch", "type": "game", "genre": "shooter"},
    {"title": "Grand Theft Auto V", "type": "game", "genre": "action"},
    {"title": "Red Dead Redemption 2", "type": "game", "genre": "action"},
    {"title": "Resident Evil Village", "type": "game", "genre": "horror"},
    {"title": "Dead by Daylight", "type": "game", "genre": "horror"},
    {"title": "Fall Guys", "type": "game", "genre": "party"},
    {"title": "Hades", "type": "game", "genre": "roguelike"},
    {"title": "Celeste", "type": "game", "genre": "platformer"},
    {"title": "Mario Kart 8 Deluxe", "type": "game", "genre": "racing"},
    {"title": "Super Mario Odyssey", "type": "game", "genre": "adventure"},
    {"title": "The Legend of Zelda: Breath of the Wild", "type": "game", "genre": "adventure"},
    {"title": "Animal Crossing: New Horizons", "type": "game", "genre": "simulation"},
    {"title": "Pokemon Sword", "type": "game", "genre": "rpg"},
    {"title": "Tetris Effect", "type": "game", "genre": "puzzle"},
    {"title": "Overcooked 2", "type": "game", "genre": "party"},
    {"title": "LittleBigPlanet 3", "type": "game", "genre": "platformer"},
    {"title": "Humankind", "type": "game", "genre": "strategy"},
    {"title": "Terraria", "type": "game", "genre": "sandbox"},
    {"title": "Team Fortress 2", "type": "game", "genre": "shooter"},
    {"title": "Crash Bandicoot 4", "type": "game", "genre": "platformer"}
]



df = pd.DataFrame(data)
df['processed_title'] = df['title'].apply(preprocess_text)
df['processed_genre'] = df['genre'].apply(preprocess_text)

# ----------------------------
# Intent classifier
# ----------------------------
intents = {
    'patterns': [
        'Suggest me a movie', 'I want to watch a movie',
        'Recommend a film', 'I am looking for a movie',
        'Suggest a game', 'I want to play a game',
        'Recommend a game to me', 'I am looking for a game'
    ],
    'labels': [
        'movie', 'movie', 'movie', 'movie',
        'game', 'game', 'game', 'game',
    ]
}

intents_df = pd.DataFrame(intents)
intents_df['processed_patterns'] = intents_df['patterns'].apply(preprocess_text)

vectorizer_intent = TfidfVectorizer()
X_intent = vectorizer_intent.fit_transform(intents_df['processed_patterns'])
y_intent = intents_df['labels']

clf_intent = SVC(kernel='linear')
clf_intent.fit(X_intent, y_intent)

# ----------------------------
# Recommendation function
# ----------------------------
def recommend(intent, user_input):
    filtered_df = df[df['type'] == intent].copy()

    processed_input = preprocess_text(user_input)
    filtered_df['combined'] = (
        filtered_df['processed_title'] + " " + filtered_df['processed_genre']
    )

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(filtered_df['combined'])
    input_vec = tfidf.transform([processed_input])

    similarity = cosine_similarity(tfidf_matrix, input_vec).flatten()
    filtered_df['similarity'] = similarity

    recommended = (
        filtered_df.sort_values(by='similarity', ascending=False)
        .head(3)[['title', 'genre']]
    )

    return recommended.to_dict(orient="records")

# ----------------------------
# API Request Model
# ----------------------------
class ChatRequest(BaseModel):
    message: str

# ----------------------------
# API Endpoint
# ----------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    processed_text = preprocess_text(request.message)
    intent_vec = vectorizer_intent.transform([processed_text])
    intent = clf_intent.predict(intent_vec)[0]

    recommendations = recommend(intent, request.message)

    return {
        "intent": intent,
        "recommendations": recommendations
    }
