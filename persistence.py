import sqlite3

con = sqlite3.connect("data/data.db")
cur = con.cursor()

def get_youtube_url(track_name):
    query = cur.execute("SELECT youtube_url from tracks where track = ?", (track_name,))
    res = query.fetchone()
    if res:
        return res[0]


def insert_track(track_name, youtube_url):
    data = {'track': track_name, 'youtube_url': youtube_url}
    with con:
        con.execute("INSERT INTO tracks VALUES(:track, :youtube_url)", data)


def init_db():
    with con:
        con.execute("CREATE TABLE IF NOT EXISTS tracks(track, youtube_url)")