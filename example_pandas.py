import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv(dotenv_path='.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
data_dir = os.path.join('datas')


def get_ai_analysis(client: OpenAI, top_counts: str) -> Dict[str, Any]:
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Be a music expert and give me a summary of the last week's music listening, a mood board, and a recommendation for the next song to listen to."},
            {"role": "user", "content": f"Here is the data: {top_counts}. Return the response in a list of object/json with the following keys: summary, mood_board, recommendation."},
        ],
        response_format={"type": "json_object"},
    )
    
    print(f'\n\nUsage: {completion.usage.completion_tokens} tokens\n\n')
    return completion.choices[0].message.content

album_df = pd.read_csv(os.path.join(data_dir, 'dim_album.csv'))
song_df = pd.read_csv(os.path.join(data_dir, 'dim_song.csv'))
artist_df = pd.read_csv(os.path.join(data_dir, 'dim_artist.csv'))
history_df = pd.read_csv(os.path.join(data_dir, 'fact_history.csv'))

# a bit of data preprocessing
album_df['album_id'] = album_df['album_id'].astype(str)
album_df.rename(columns={'title': 'album_name'}, inplace=True)

song_df['song_id'] = song_df['song_id'].astype(str)
song_df.rename(columns={'title': 'song_name'}, inplace=True)

artist_df['artist_id'] = artist_df['artist_id'].astype(str)
artist_df.rename(columns={'name': 'artist_name'}, inplace=True)

history_df['song_id'] = history_df['song_id'].astype(str)
history_df['played_at'] = pd.to_datetime(history_df['played_at'], format='ISO8601')

# join dataframes

joined_df = history_df.merge(song_df, on='song_id', how='left').merge(album_df, on='album_id', how='left').merge(artist_df, on='artist_id', how='left')

# filter last week
last_week_df = joined_df[joined_df['played_at'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]

# top 10 counts
top_10_counts = last_week_df.value_counts(['song_name', 'artist_name', 'album_name']).head(10)

# get ai analysis
ai_analysis = get_ai_analysis(client, top_10_counts)
print(ai_analysis)