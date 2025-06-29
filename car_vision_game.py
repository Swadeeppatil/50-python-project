import cv2
import numpy as np
import random

class CarVisionGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.score = 0
        self.game_over = False
        
        # Car parameters
        self.car_pos = 320  # Center position
        self.car_width = 60
        self.car_height = 80
        
        # Road parameters
        self.road_width = 400
        self.road_start = 120  # Left boundary
        self.obstacles = []
        
        # Color detection for steering wheel
        self.lower_color = np.array([0, 100, 100])  # Red color range
        self.upper_color = np.array([10, 255, 255])
        
    def run(self):
        while not self.game_over:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            game_frame = self.process_frame(frame)
            
            # Display score
            cv2.putText(game_frame, f"Score: {self.score}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow("Car Vision Game", game_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        
    def process_frame(self, frame):
        # Draw road
        cv2.rectangle(frame, (self.road_start, 0), 
                     (self.road_start + self.road_width, 480),
                     (128, 128, 128), -1)
        
        # Detect steering wheel (red object)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        # Update car position based on steering wheel
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w//2
                
                # Move car based on steering wheel position
                if center_x < 213:  # Left third of screen
                    self.car_pos = max(self.road_start + self.car_width//2,
                                     self.car_pos - 5)
                elif center_x > 426:  # Right third of screen
                    self.car_pos = min(self.road_start + self.road_width - self.car_width//2,
                                     self.car_pos + 5)
                
        # Create obstacles
        if random.random() < 0.02 and len(self.obstacles) < 3:
            x = random.randint(self.road_start + 40,
                             self.road_start + self.road_width - 40)
            self.obstacles.append({'x': x, 'y': -50})
            
        # Update and draw obstacles
        for obstacle in self.obstacles[:]:
            obstacle['y'] += 5
            
            # Draw obstacle
            cv2.rectangle(frame,
                         (obstacle['x'] - 20, int(obstacle['y'])),
                         (obstacle['x'] + 20, int(obstacle['y']) + 40),
                         (0, 0, 255), -1)
            
            # Check collision
            if (abs(obstacle['x'] - self.car_pos) < 40 and
                abs(obstacle['y'] - 400) < 60):
                self.game_over = True
                cv2.putText(frame, "Game Over!", (200, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                
            # Remove off-screen obstacles
            if obstacle['y'] > 480:
                self.obstacles.remove(obstacle)
                self.score += 10
                
        # Draw player's car
        cv2.rectangle(frame,
                     (int(self.car_pos - self.car_width//2), 360),
                     (int(self.car_pos + self.car_width//2), 440),
                     (0, 255, 0), -1)
        
        return frame

if __name__ == "__main__":
    print("Instructions:")
    print("- Use a red object as steering wheel")
    print("- Move left/right to avoid obstacles")
    print("- Score points by surviving")
    print("- Press 'q' to quit")
    
    game = CarVisionGame()
    game.run()