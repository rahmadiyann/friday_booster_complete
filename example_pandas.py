import pandas as pd
from openai import OpenAI
import os
import dotenv
from typing import Dict, Any

def load_env() -> None:
    dotenv.load_dotenv(dotenv_path='.env')

def init_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def load_and_process_df(filename: str, id_col: str, rename_map: Dict[str, str] = None) -> pd.DataFrame:
    df = pd.read_csv(os.path.join('datas', filename))
    df[id_col] = df[id_col].astype(str)
    if rename_map:
        df = df.rename(columns=rename_map)
    return df

def process_history_df(df: pd.DataFrame) -> pd.DataFrame:
    id_cols = ['song_id', 'album_id', 'artist_id']
    df[id_cols] = df[id_cols].astype(str)
    df['played_at'] = pd.to_datetime(df['played_at'], format='ISO8601')
    return df

def join_dataframes(history_df: pd.DataFrame, songs_df: pd.DataFrame, 
                   albums_df: pd.DataFrame, artists_df: pd.DataFrame) -> pd.DataFrame:
    return (history_df
        .merge(songs_df, on='song_id', how='left')
        .merge(albums_df, on='album_id', how='left')
        .merge(artists_df, on='artist_id', how='left')
    )

def filter_last_week(df: pd.DataFrame) -> pd.DataFrame:
    week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    return df[df['played_at'] >= week_ago]

def get_top_10_counts(df: pd.DataFrame, columns: list[str]) -> Dict[str, pd.Series]:
    return {
        f'top10{col.split("_")[0]}': df.value_counts(col).head(10)
        for col in columns
    }

def get_ai_analysis(client: OpenAI, top_counts: Dict[str, pd.Series]) -> Dict[str, Any]:
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Be a music expert and give me a summary of the last week's music listening, a mood board, and a recommendation for the next song to listen to."},
            {"role": "user", "content": f"Here is the data: {', '.join(f'{k}: {v.to_string()}' for k,v in top_counts.items())}. Return the response in a list of object/json with the following keys: summary, mood_board, recommendation."},
        ],
        response_format={"type": "json_object"},
    )
    
    print(f'Usage: {completion.usage}')
    return completion.choices[0].message.content

def main():
    load_env()
    client = init_openai_client()
    
    # Load and process dataframes
    songs_df = load_and_process_df('dim_song.csv', 'song_id', {'title': 'song_name'})
    albums_df = load_and_process_df('dim_album.csv', 'album_id', {'title': 'album_name'})
    artists_df = load_and_process_df('dim_artist.csv', 'artist_id', {'name': 'artist_name'})
    history_df = load_and_process_df('fact_history.csv', 'song_id')
    history_df = process_history_df(history_df)
    
    # Join and analyze
    joined_df = join_dataframes(history_df, songs_df, albums_df, artists_df)
    last_week_df = filter_last_week(joined_df)
    summary_cols = ['song_name', 'artist_name', 'album_name']
    summary = last_week_df[summary_cols]
    
    top_counts = get_top_10_counts(summary, summary_cols)
    analysis = get_ai_analysis(client, top_counts)
    print('==========')
    print(analysis)

if __name__ == "__main__":
    main()