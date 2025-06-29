import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import pygame
import time
from deep_sort_realtime.deepsort_tracker import DeepSort
from shapely.geometry import Polygon, Point
import math
from datetime import datetime

class AirDefenseSystem:
    def __init__(self):
        # Initialize YOLO model
        self.model = YOLO("yolov8n.pt")
        
        # Initialize DeepSORT tracker
        self.tracker = DeepSort(max_age=5)
        
        # Initialize detection zone
        self.restricted_zone = np.array([
            [100, 100],
            [540, 100],
            [540, 380],
            [100, 380]
        ], np.int32)
        
        # Initialize Pygame for audio
        pygame.mixer.init()
        # Generate a simple beep sound instead of loading wav file
        pygame.mixer.set_num_channels(1)
        self.alert_sound = pygame.mixer.Sound(buffer=np.sin(2 * np.pi * np.arange(44100) * 440 / 44100).astype(np.float32))
        self.alert_sound.set_volume(0.5)  # Set volume to 50%
        
        # Initialize colors
        self.colors = {
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255)
        }
        
        # Initialize tracking history
        self.track_history = {}
        
        # Initialize statistics
        self.stats = {
            'total_detections': 0,
            'intrusions': 0,
            'start_time': datetime.now()
        }

    def is_in_restricted_zone(self, point):
        """Check if point is inside restricted zone"""
        polygon = Polygon(self.restricted_zone)
        point = Point(point)
        return polygon.contains(point)

    def draw_zone(self, frame):
        """Draw restricted zone on frame"""
        cv2.polylines(frame, [self.restricted_zone], 
                     True, self.colors['red'], 2)
        cv2.putText(frame, "Restricted Airspace", 
                   (self.restricted_zone[0][0], self.restricted_zone[0][1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['red'], 2)

    def draw_stats(self, frame):
        """Draw statistics on frame"""
        stats_text = [
            f"Runtime: {(datetime.now() - self.stats['start_time']).seconds}s",
            f"Total Detections: {self.stats['total_detections']}",
            f"Intrusions: {self.stats['intrusions']}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(frame, text, (10, 30 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                       self.colors['white'], 2)

    def process_frame(self, frame):
        """Process a single frame"""
        # Run YOLO detection
        results = self.model(frame, classes=[0, 1, 2, 3, 4])  # Detect relevant classes
        
        # Get detections
        detections = []
        for result in results[0].boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            
            if score > 0.5:  # Confidence threshold
                detections.append(([x1, y1, x2, y2], score, int(class_id)))
                self.stats['total_detections'] += 1

        # Update tracker
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        # Process each track
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            # Get tracking box
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            
            # Calculate center point
            center_point = (int((x1 + x2)/2), int((y1 + y2)/2))
            
            # Check for intrusion
            if self.is_in_restricted_zone(center_point):
                color = self.colors['red']
                self.alert_sound.play()
                self.stats['intrusions'] += 1
            else:
                color = self.colors['green']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw ID
            cv2.putText(frame, f"ID: {track.track_id}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, color, 2)
            
            # Update tracking history
            if track.track_id not in self.track_history:
                self.track_history[track.track_id] = []
            self.track_history[track.track_id].append(center_point)
            
            # Draw tracking line
            if len(self.track_history[track.track_id]) > 2:
                points = np.array(self.track_history[track.track_id], np.int32)
                cv2.polylines(frame, [points], False, self.colors['yellow'], 2)
        
        # Draw zone and stats
        self.draw_zone(frame)
        self.draw_stats(frame)
        
        return frame

    def run(self):
        """Main run loop"""
        cap = cv2.VideoCapture(0)  # Use 0 for webcam or video file path
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame
            processed_frame = self.process_frame(frame)
            
            # Display frame
            cv2.imshow("Air Defense System", processed_frame)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Create and run the system
    defense_system = AirDefenseSystem()
    defense_system.run()