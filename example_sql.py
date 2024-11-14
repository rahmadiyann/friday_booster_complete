from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(dotenv_path='.env')
PSQL_URL = os.getenv('POSTGRES_URL')
print(PSQL_URL)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=OPENAI_API_KEY
)

engine = create_engine(PSQL_URL)

last_7_days_history_query = text("""
    SELECT 
        ds.title AS song_name, 
        da.title AS album_name, 
        dar.name AS artist_name, 
        FLOOR(SUM(ds.duration_ms) / (1000 * 60)) AS total_minute_listened
    FROM 
        fact_history fh
    JOIN 
        dim_song ds ON fh.song_id = ds.song_id
    JOIN 
        dim_album da ON fh.album_id = da.album_id
    JOIN 
        dim_artist dar ON fh.artist_id = dar.artist_id
    WHERE 
        fh.played_at >= CURRENT_DATE - INTERVAL '1 week'
    AND 
        fh.played_at < CURRENT_DATE + INTERVAL '1 day'
    GROUP BY 
        ds.title, da.title, dar.name
    ORDER BY 
        total_minute_listened DESC
    LIMIT 10
""")

def get_query_result(query: str) -> dict:
    with engine.connect() as con:
        result = con.execute(query)
        columns = ", ".join(result.keys())
        data = result.fetchall()
        result = {
            "columns": columns,
            "data": data
        }
        return result
            
def get_recommendation(query_string: str, client: OpenAI) -> dict:
    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a music recommendation system. You are given a query and you need to recommend 5 songs that the user might like based on the query."},
            {"role": "user", "content": f"Here is the query result: {query_string}, return in the format of a json with the following keys: listening_summary['total_song', 'total_minute_listened', 'most_listened_song'], mood_recap (a guess of what the listener is going through (str)), song_recs['song_name', 'album_name', 'artist_name']"}
        ],
        response_format={"type": "json_object"}
    )
    print(f"Total tokens used: {result.usage.total_tokens}")
    return result.choices[0].message.content
    
result = get_query_result(last_7_days_history_query)
recommendation = get_recommendation(result, client)
print(f"Recommendation: {recommendation}")