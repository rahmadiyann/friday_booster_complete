SELECT 
    ds.title AS song_name, 
    da.image_url AS album_art, 
    MAX(fh.played_at) AS last_played, 
    EXTRACT(DAY FROM (NOW() - MAX(fh.played_at))) AS days_ago
FROM 
    fact_history fh
JOIN 
    dim_song ds ON fh.song_id = ds.song_id
JOIN 
    dim_album da ON fh.album_id = da.album_id
GROUP 
    BY ds.title, da.image_url
ORDER 
    BY days_ago DESC
LIMIT 10