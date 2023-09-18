from flask import Flask, request, Response, render_template, flash, redirect, url_for, send_from_directory

import os
import mido
from mido import MidiFile, MidiTrack
from werkzeug.utils import secure_filename
import io

app = Flask(__name__, static_url_path='/static')

ALLOWED_EXTENSIONS = {'mid'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            cleaned_midi = clean_midi(file)
            return Response(cleaned_midi.getvalue(),
                            mimetype="audio/midi",
                            headers={"Content-Disposition": f"attachment;filename={file.filename.split('.')[0]}_cleaned.mid"})

    return render_template("index.html")

def clean_midi(file):
    mid = MidiFile(file=file.stream)
    new_mid = MidiFile()

    for track in mid.tracks:
        new_track = MidiTrack()
        for msg in track:
            if msg.is_meta and (msg.type == 'unknown_meta' or msg.type == 75):
                continue
            else:
                new_track.append(msg)
        new_mid.tracks.append(new_track)

    buffer = io.BytesIO()
    new_mid.save(file=buffer)
    buffer.seek(0)

    return buffer

if __name__ == '__main__':
    app.run(debug=True, port=5000)
