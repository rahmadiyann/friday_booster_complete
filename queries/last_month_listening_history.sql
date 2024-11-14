SELECT 
    fh.id AS listening_id,
    ds.title AS song_name, 
    dar.name AS artist_name, 
    da.title AS album_name, 
    da.image_url AS album_art
FROM 
    fact_history fh
JOIN 
    dim_song ds ON fh.song_id = ds.song_id
JOIN 
    dim_album da ON fh.album_id = da.album_id
JOIN 
    dim_artist dar ON fh.artist_id = dar.artist_id
WHERE 
    fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
AND 
    fh.played_at < CURRENT_DATE + INTERVAL '1 day'
ORDER BY 
    listening_id DESC