SELECT 
    ds.title AS song_name, 
    da.title AS album, 
    dar.name AS artist, 
    da.image_url AS album_art, 
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
    fh.played_at >= CURRENT_DATE - INTERVAL '1 month'
AND 
    fh.played_at < CURRENT_DATE + INTERVAL '1 day'
GROUP BY 
    ds.title, da.title, dar.name, da.image_url
ORDER BY 
    total_minute_listened DESC
LIMIT 10