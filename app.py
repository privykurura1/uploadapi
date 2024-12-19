import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define upload folders
app.config['ARTICLE_UPLOAD_FOLDER'] = 'uploads/articles'
app.config['YOUTUBE_URL_FOLDER'] = 'uploads/youtube'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max size 50 MB

# Create necessary directories if they don't exist
os.makedirs(app.config['ARTICLE_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['YOUTUBE_URL_FOLDER'], exist_ok=True)

# Store uploaded files and URLs in memory for now
uploads_data = []

# Serve the upload page
@app.route('/')
def index():
    return render_template('upload_file.html', uploads=uploads_data)

# Route to add YouTube video URL
@app.route('/add_youtube_video', methods=['POST'])
def add_youtube_video():
    youtube_url = request.form.get('youtube_url')

    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    # Save the YouTube URL metadata as a JSON file
    youtube_metadata = {
        'type': 'youtube',
        'youtube_url': youtube_url
    }
    youtube_id = secure_filename(youtube_url.split('=')[-1])  # Extract a unique ID from the URL
    metadata_file_path = os.path.join(app.config['YOUTUBE_URL_FOLDER'], f'{youtube_id}.json')

    # Save metadata to a file to persist across server restarts
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(youtube_metadata, metadata_file)

    uploads_data.append(youtube_metadata)
    return render_template('upload_file.html', uploads=uploads_data)

# Route to add article notes
@app.route('/add_article', methods=['POST'])
def add_article():
    article_title = request.form.get('title')
    article_content = request.form.get('content')

    if not article_title or not article_content:
        return jsonify({'error': 'Article title and content are required'}), 400

    # Save article as a text file
    article_filename = secure_filename(f'{article_title}.txt')
    article_file_path = os.path.join(app.config['ARTICLE_UPLOAD_FOLDER'], article_filename)

    with open(article_file_path, 'w') as article_file:
        article_file.write(f"Title: {article_title}\n\n{article_content}")

    # Store article metadata
    article_metadata = {
        'type': 'article',
        'title': article_title,
        'file_path': article_file_path
    }

    uploads_data.append(article_metadata)
    return render_template('upload_file.html', uploads=uploads_data)

# Route to fetch all uploads
@app.route('/get_uploads', methods=['GET'])
def get_uploads():
    all_uploads = []

    # Load YouTube metadata from files to include in the response
    youtube_files = [
        os.path.join(app.config['YOUTUBE_URL_FOLDER'], f)
        for f in os.listdir(app.config['YOUTUBE_URL_FOLDER'])
        if f.endswith('.json')
    ]
    for youtube_file in youtube_files:
        with open(youtube_file, 'r') as f:
            metadata = json.load(f)
            all_uploads.append(metadata)

    # Load article files (stored as text files)
    article_files = [
        f for f in os.listdir(app.config['ARTICLE_UPLOAD_FOLDER'])
        if f.endswith('.txt')
    ]
    for article_file in article_files:
        with open(os.path.join(app.config['ARTICLE_UPLOAD_FOLDER'], article_file), 'r') as f:
            content = f.read()
        title = article_file.rsplit('.', 1)[0]  # Use filename as title
        article_metadata = {
            'type': 'article',
            'title': title,
            'content': content
        }
        all_uploads.append(article_metadata)

    return jsonify({'uploads': all_uploads})

if __name__ == '__main__':
    # Bind to all available interfaces to allow access from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
