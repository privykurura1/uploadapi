import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the folder paths to store metadata for YouTube and Article URLs
app.config['YOUTUBE_URL_FOLDER'] = 'uploads/youtube'
app.config['ARTICLE_URL_FOLDER'] = 'uploads/articles'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max size 50 MB

# Create necessary directories if they don't exist
os.makedirs(app.config['YOUTUBE_URL_FOLDER'], exist_ok=True)
os.makedirs(app.config['ARTICLE_URL_FOLDER'], exist_ok=True)

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

    # Generate a unique filename for YouTube URL
    youtube_id = secure_filename(youtube_url.split('=')[-1])  # Extract ID from URL
    youtube_metadata = {
        'type': 'youtube',
        'url': youtube_url  # Direct link to the YouTube video
    }

    # Save metadata as a JSON file in the YouTube URL folder
    metadata_file_path = os.path.join(app.config['YOUTUBE_URL_FOLDER'], f'{youtube_id}.json')
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(youtube_metadata, metadata_file)

    uploads_data.append(youtube_metadata)
    return render_template('upload_file.html', uploads=uploads_data)

# Route to add article URL
@app.route('/add_article', methods=['POST'])
def add_article():
    article_url = request.form.get('article_url')

    if not article_url:
        return jsonify({'error': 'Article URL is required'}), 400

    # Generate a unique filename for the article URL
    article_id = secure_filename(article_url.split('/')[-1])  # Extract a unique part of the URL
    article_metadata = {
        'type': 'article',
        'url': article_url  # Direct link to the article
    }

    # Save metadata as a JSON file in the Article URL folder
    metadata_file_path = os.path.join(app.config['ARTICLE_URL_FOLDER'], f'{article_id}.json')
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(article_metadata, metadata_file)

    uploads_data.append(article_metadata)
    return render_template('upload_file.html', uploads=uploads_data)

# Route to fetch all uploads
@app.route('/get_uploads', methods=['GET'])
def get_uploads():
    all_uploads = []

    # Load YouTube metadata from the YouTube folder
    youtube_files = [
        os.path.join(app.config['YOUTUBE_URL_FOLDER'], f)
        for f in os.listdir(app.config['YOUTUBE_URL_FOLDER'])
        if f.endswith('.json')
    ]
    for youtube_file in youtube_files:
        with open(youtube_file, 'r') as f:
            metadata = json.load(f)
            all_uploads.append(metadata)

    # Load article metadata from the Article folder
    article_files = [
        os.path.join(app.config['ARTICLE_URL_FOLDER'], f)
        for f in os.listdir(app.config['ARTICLE_URL_FOLDER'])
        if f.endswith('.json')
    ]
    for article_file in article_files:
        with open(article_file, 'r') as f:
            metadata = json.load(f)
            all_uploads.append(metadata)

    return jsonify({'uploads': all_uploads})

if __name__ == '__main__':
    # Bind to all available interfaces to allow access from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
