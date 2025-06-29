from flask import Flask, render_template, request, send_file, jsonify
from celery import Celery
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
import nltk
from nltk.tokenize import sent_tokenize
import os
import uuid
import time
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/generated'

# Configure Celery
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Initialize NLTK
nltk.download('punkt')

# Initialize Stable Diffusion
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

class VideoGenerator:
    def __init__(self):
        self.temp_dir = Path('static/generated')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_images(self, text_segments):
        image_paths = []
        for segment in text_segments:
            # Generate unique filename
            filename = f"img_{uuid.uuid4()}.png"
            image_path = self.temp_dir / filename
            
            # Generate image using Stable Diffusion
            image = pipe(segment).images[0]
            image.save(str(image_path))
            image_paths.append(str(image_path))
        
        return image_paths
    
    def generate_audio(self, text_segments):
        audio_paths = []
        for segment in text_segments:
            filename = f"audio_{uuid.uuid4()}.mp3"
            audio_path = self.temp_dir / filename
            
            # Generate audio using gTTS
            tts = gTTS(text=segment, lang='en')
            tts.save(str(audio_path))
            audio_paths.append(str(audio_path))
        
        return audio_paths
    
    def create_video(self, image_paths, audio_paths, output_path):
        clips = []
        for img_path, audio_path in zip(image_paths, audio_paths):
            # Load audio to get duration
            audio = AudioFileClip(audio_path)
            # Create image clip with same duration as audio
            image = ImageClip(img_path).set_duration(audio.duration)
            # Combine image and audio
            video_clip = image.set_audio(audio)
            clips.append(video_clip)
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips)
        # Write final video
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        return output_path

@celery.task
def generate_video_task(text, settings):
    generator = VideoGenerator()
    
    # Split text into segments
    segments = sent_tokenize(text)
    
    # Generate images and audio
    image_paths = generator.generate_images(segments)
    audio_paths = generator.generate_audio(segments)
    
    # Create unique output filename
    output_path = f"static/generated/video_{uuid.uuid4()}.mp4"
    
    # Generate video
    final_video = generator.create_video(image_paths, audio_paths, output_path)
    
    # Cleanup temporary files
    for path in image_paths + audio_paths:
        os.remove(path)
    
    return final_video

@app.route('/')
def home():
    return render_template('index.html')

 # Replace Celery task management with SQLite
def init_task_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id TEXT PRIMARY KEY,
                  status TEXT,
                  result TEXT)''')
    conn.commit()
    conn.close()

def update_task_status(task_id, status, result=None):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET status = ?, result = ? WHERE id = ?',
              (status, json.dumps(result) if result else None, task_id))
    conn.commit()
    conn.close()

def get_task_status(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT status, result FROM tasks WHERE id = ?', (task_id,))
    result = c.fetchone()
    conn.close()
    return result if result else (None, None)

# Replace @celery.task with regular function
def process_video_generation(task_id, text, settings):
    try:
        generator = VideoGenerator()
        segments = sent_tokenize(text)
        image_paths = generator.generate_images(segments)
        audio_paths = generator.generate_audio(segments)
        output_path = f"static/generated/video_{uuid.uuid4()}.mp4"
        final_video = generator.create_video(image_paths, audio_paths, output_path)
        
        # Cleanup temporary files
        for path in image_paths + audio_paths:
            os.remove(path)
            
        update_task_status(task_id, 'SUCCESS', final_video)
    except Exception as e:
        update_task_status(task_id, 'FAILURE', str(e))

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    settings = {
        'duration': request.form.get('duration', '60'),
        'theme': request.form.get('theme', 'default'),
        'voice': request.form.get('voice', 'default')
    }
    
    # Create new task
    task_id = str(uuid.uuid4())
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (id, status) VALUES (?, ?)', (task_id, 'PENDING'))
    conn.commit()
    conn.close()
    
    # Start processing in background
    Thread(target=process_video_generation, args=(task_id, text, settings)).start()
    
    return jsonify({'task_id': task_id})

# Initialize database when app starts
init_task_db()

@app.route('/status/<task_id>')
def status(task_id):
    task = generate_video_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'video_path': task.get()
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)