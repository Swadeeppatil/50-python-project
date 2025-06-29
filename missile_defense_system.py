import cv2
import numpy as np
from ultralytics import YOLO
import pygame
import time
from deep_sort_realtime.deepsort_tracker import DeepSort
from shapely.geometry import Polygon, Point
from datetime import datetime
import threading
import logging
import os
import pyttsx3
import face_recognition
from firebase_admin import credentials, initialize_app, db

class MissileDefenseSystem:
    def __init__(self):
        # Initialize YOLO model
        self.model = YOLO("yolov8n.pt")
        self.tracker = DeepSort(max_age=5)
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # Initialize face recognition
        self.known_faces = self.load_known_faces()
        
        # Initialize Firebase (uncomment and add your credentials)
        # cred = credentials.Certificate("path/to/serviceAccountKey.json")
        # initialize_app(cred, {'databaseURL': 'your-database-url'})
        # self.db_ref = db.reference('detections')
        
        # Night vision mode
        self.night_vision_mode = False
        
        # Initialize logging
        logging.basicConfig(
            filename='defense_log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        
        # Initialize detection zone
        self.restricted_zone = np.array([
            [100, 100], [540, 100],
            [540, 380], [100, 380]
        ], np.int32)
        
        # Initialize missile system
        self.missile_ready = True
        self.cooldown_time = 5  # seconds
        self.last_launch_time = {}  # Track launch times per object
        
        # Load missile launch animation frames
        self.missile_frames = self.load_missile_animation()
        self.current_frame = 0
        self.showing_animation = False
        
        # Initialize audio
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)
        self.warning_sound = pygame.mixer.Sound(buffer=np.sin(2 * np.pi * np.arange(44100) * 440 / 44100).astype(np.float32))
        self.launch_sound = pygame.mixer.Sound(buffer=np.sin(2 * np.pi * np.arange(44100) * 880 / 44100).astype(np.float32))
        
        # Initialize colors and tracking
        self.colors = {
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255)
        }
        self.track_history = {}
        self.stats = {
            'total_detections': 0,
            'launches': 0,
            'start_time': datetime.now()
        }

    def load_missile_animation(self):
        # Create simple missile animation frames
        frames = []
        for i in range(5):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.line(frame, (50, 90-i*20), (50, 10-i*20), (0, 255, 0), 3)
            frames.append(frame)
        return frames

    def load_known_faces(self):
        known_faces = []
        faces_dir = "known_faces"
        if os.path.exists(faces_dir):
            for file in os.listdir(faces_dir):
                if file.endswith((".jpg", ".png")):
                    image = face_recognition.load_image_file(os.path.join(faces_dir, file))
                    encoding = face_recognition.face_encodings(image)[0]
                    known_faces.append(encoding)
        return known_faces

    def announce_warning(self, text):
        threading.Thread(target=self.tts_engine.say, args=(text,)).start()
        self.tts_engine.runAndWait()

    def apply_night_vision(self, frame):
        # Convert to grayscale and apply CLAHE
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        # Apply false color
        return cv2.applyColorMap(enhanced, cv2.COLORMAP_BONE)

    def simulate_missile_launch(self, target_point):
        if not self.missile_ready:
            return
            
        self.missile_ready = False
        self.showing_animation = True
        self.current_frame = 0
        self.launch_sound.play()
        
        # Log launch
        logging.info(f"Missile launched at target coordinates: {target_point}")
        self.stats['launches'] += 1
        
        # Start cooldown timer
        threading.Timer(self.cooldown_time, self.reset_missile).start()

    def reset_missile(self):
        self.missile_ready = True
        self.showing_animation = False

    def draw_missile_animation(self, frame, target_point):
        if self.showing_animation and self.current_frame < len(self.missile_frames):
            missile_frame = self.missile_frames[self.current_frame]
            x, y = target_point
            h, w = missile_frame.shape[:2]
            frame[y-h//2:y+h//2, x-w//2:x+w//2] = cv2.addWeighted(
                frame[y-h//2:y+h//2, x-w//2:x+w//2], 0.7,
                missile_frame, 0.3, 0
            )
            self.current_frame += 1

    def draw_interface(self, frame):
        # Draw status
        status_text = f"Missile System: {'READY' if self.missile_ready else 'COOLDOWN'}"
        cv2.putText(frame, status_text, (10, 460),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                   (0, 255, 0) if self.missile_ready else (0, 0, 255), 2)
        
        # Draw statistics
        stats_text = [
            f"Runtime: {(datetime.now() - self.stats['start_time']).seconds}s",
            f"Detections: {self.stats['total_detections']}",
            f"Launches: {self.stats['launches']}"
        ]
        for i, text in enumerate(stats_text):
            cv2.putText(frame, text, (10, 30 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       self.colors['white'], 2)

    def process_frame(self, frame):
        # Apply night vision if enabled
        if self.night_vision_mode:
            frame = self.apply_night_vision(frame)
        
        # Face recognition
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        # YOLO detection
        results = self.model(frame, classes=[0, 1, 2, 3, 4])  # 0: person, 1: bicycle, 2: car...
        detections = []
        
        for result in results[0].boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            # Only track humans and vehicles
            if class_id in [0, 1, 2, 3, 4] and score > 0.5:
                detections.append(([x1, y1, x2, y2], score, int(class_id)))
                self.stats['total_detections'] += 1
                
                # Send to Firebase (uncomment to enable)
                # self.db_ref.push().set({
                #     'timestamp': datetime.now().isoformat(),
                #     'class_id': int(class_id),
                #     'confidence': float(score)
                # })

        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            center_point = (int((x1 + x2)/2), int((y1 + y2)/2))
            
            # Check for intrusion
            if self.is_in_restricted_zone(center_point):
                if (track.track_id not in self.last_launch_time or 
                    time.time() - self.last_launch_time[track.track_id] > self.cooldown_time):
                    # Voice alert
                    self.announce_warning("Warning! Restricted zone breach detected!")
                    self.warning_sound.play()
                    self.simulate_missile_launch(center_point)
                    self.last_launch_time[track.track_id] = time.time()
                color = self.colors['red']
            else:
                color = self.colors['green']
            
            # Draw tracking visuals
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"Target {track.track_id}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, color, 2)
            
            # Update and draw track history
            if track.track_id not in self.track_history:
                self.track_history[track.track_id] = []
            self.track_history[track.track_id].append(center_point)
            
            if len(self.track_history[track.track_id]) > 2:
                points = np.array(self.track_history[track.track_id], np.int32)
                cv2.polylines(frame, [points], False, self.colors['yellow'], 2)
            
            # Draw missile animation if active
            if self.showing_animation:
                self.draw_missile_animation(frame, center_point)
        
        # Draw interface elements
        cv2.polylines(frame, [self.restricted_zone], True, self.colors['red'], 2)
        cv2.putText(frame, "Restricted Airspace", 
                   (self.restricted_zone[0][0], self.restricted_zone[0][1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['red'], 2)
        self.draw_interface(frame)
        
        return frame

    def is_in_restricted_zone(self, point):
        polygon = Polygon(self.restricted_zone)
        point = Point(point)
        return polygon.contains(point)

    def run(self):
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Toggle night vision with 'n' key
            if cv2.waitKey(1) & 0xFF == ord('n'):
                self.night_vision_mode = not self.night_vision_mode
                
            processed_frame = self.process_frame(frame)
            cv2.imshow("Missile Defense System", processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    defense_system = MissileDefenseSystem()
    defense_system.run()