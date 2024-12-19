import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define upload folders
app.config['VIDEO_UPLOAD_FOLDER'] = 'uploads/videos'
app.config['DOCUMENT_UPLOAD_FOLDER'] = 'uploads/documents'
app.config['YOUTUBE_URL_FOLDER'] = 'uploads/youtube'
app.config['ALLOWED_VIDEO_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'flv'}
app.config['ALLOWED_DOCUMENT_EXTENSIONS'] = {'pdf', 'txt', 'docx'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max size 50 MB

# Create necessary directories if they don't exist
os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOCUMENT_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['YOUTUBE_URL_FOLDER'], exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Store uploaded files and URLs in memory for now
uploads_data = []

# Serve the upload page
@app.route('/')
def index():
    return render_template('upload_file.html', uploads=uploads_data)

# Route to upload video files
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename, app.config['ALLOWED_VIDEO_EXTENSIONS']):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], filename))
        uploads_data.append({'type': 'video', 'filename': filename})
        return render_template('upload_file.html', uploads=uploads_data)

    return jsonify({'error': 'File type not allowed'}), 400

# Route to upload document files (PDF, DOCX)
@app.route('/upload_document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename, app.config['ALLOWED_DOCUMENT_EXTENSIONS']):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['DOCUMENT_UPLOAD_FOLDER'], filename))
        uploads_data.append({'type': 'document', 'filename': filename})
        return render_template('upload_file.html', uploads=uploads_data)

    return jsonify({'error': 'File type not allowed'}), 400

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

# Route to fetch all uploads
@app.route('/get_uploads', methods=['GET'])
def get_uploads():
    all_uploads = []

    # Load video files
    video_files = [
        f for f in os.listdir(app.config['VIDEO_UPLOAD_FOLDER'])
        if allowed_file(f, app.config['ALLOWED_VIDEO_EXTENSIONS'])
    ]
    for video_file in video_files:
        all_uploads.append({
            'type': 'video',
            'filename': video_file
        })

    # Load document files
    document_files = [
        f for f in os.listdir(app.config['DOCUMENT_UPLOAD_FOLDER'])
        if allowed_file(f, app.config['ALLOWED_DOCUMENT_EXTENSIONS'])
    ]
    for document_file in document_files:
        all_uploads.append({
            'type': 'document',
            'filename': document_file
        })

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

    return jsonify({'uploads': all_uploads})

if __name__ == '__main__':
    # Bind to all available interfaces to allow access from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
