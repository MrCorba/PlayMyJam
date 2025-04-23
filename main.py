from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from collections import Counter

app = Flask(__name__)
DB = 'requests.db'
DJ_PASSWORD = 'secret123'  # Change this to whatever you want

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            played INTEGER DEFAULT 0
        )''')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        artist = request.form['artist'].strip()
        title = request.form['title'].strip()
        if artist and title:
            with sqlite3.connect(DB) as con:
                con.execute('INSERT INTO songs (artist, title) VALUES (?, ?)', (artist, title))
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/dj', methods=['GET', 'POST'])
def dj():
    if request.args.get('pw') != DJ_PASSWORD:
        return "Unauthorized", 401

    if request.method == 'POST':
        song_id = request.form.get('played')
        if song_id:
            with sqlite3.connect(DB) as con:
                con.execute('UPDATE songs SET played = 1 WHERE id = ?', (song_id,))
        return redirect(url_for('dj', pw=DJ_PASSWORD))

    with sqlite3.connect(DB) as con:
        songs = con.execute('SELECT id, artist, title, played FROM songs').fetchall()
    
    counter = Counter((s[1].lower(), s[2].lower()) for s in songs)
    unique_songs = {}
    for s in songs:
        key = (s[1].lower(), s[2].lower())
        if key not in unique_songs:
            unique_songs[key] = {
                'id': s[0],
                'artist': s[1],
                'title': s[2],
                'played': s[3],
                'count': counter[key]
            }

    return render_template('dj.html', songs=list(unique_songs.values()))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
