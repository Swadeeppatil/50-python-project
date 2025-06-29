import cv2
import numpy as np
import mediapipe as mp
import random
import time

class AirplaneGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        
        # Game variables
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.score = 0
        self.game_over = False
        self.last_update = time.time()
        
        # Airplane parameters
        self.plane_x = 100
        self.plane_y = self.height // 2
        self.plane_size = 40
        
        # Obstacles
        self.obstacles = []
        self.obstacle_speed = 5
        self.obstacle_interval = 2.0  # seconds
        
        # Clouds
        self.clouds = []
        self.create_clouds()
        
    def create_clouds(self):
        for _ in range(5):
            self.clouds.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(15, 30)
            })
            
    def move_clouds(self):
        for cloud in self.clouds:
            cloud['x'] -= 1
            if cloud['x'] < -50:
                cloud['x'] = self.width + 50
                cloud['y'] = random.randint(0, self.height)
                
    def draw_game(self, frame, game_frame):
        # Draw sky background
        game_frame[:] = (135, 206, 235)
        
        # Draw clouds
        for cloud in self.clouds:
            cv2.circle(game_frame, 
                      (cloud['x'], cloud['y']), 
                      cloud['size'], 
                      (255, 255, 255), -1)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            cv2.rectangle(game_frame, 
                         (int(obstacle['x']), 0),
                         (int(obstacle['x'] + 50), obstacle['top_height']),
                         (0, 255, 0), -1)
            cv2.rectangle(game_frame,
                         (int(obstacle['x']), obstacle['bottom_height']),
                         (int(obstacle['x'] + 50), self.height),
                         (0, 255, 0), -1)
        
        # Draw airplane
        points = np.array([
            [self.plane_x, self.plane_y],
            [self.plane_x + self.plane_size, self.plane_y],
            [self.plane_x + self.plane_size//2, self.plane_y - self.plane_size//2]
        ], np.int32)
        cv2.fillPoly(game_frame, [points], (255, 0, 0))
        
        # Draw score
        cv2.putText(game_frame, f"Score: {self.score}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                   
        return game_frame
        
    def update_game_state(self):
        current_time = time.time()
        
        # Update clouds
        self.move_clouds()
        
        # Create new obstacles
        if current_time - self.last_update > self.obstacle_interval:
            height = random.randint(100, self.height - 200)
            self.obstacles.append({
                'x': self.width,
                'top_height': height - 100,
                'bottom_height': height + 100
            })
            self.last_update = current_time
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle['x'] -= self.obstacle_speed
            if obstacle['x'] < -50:
                self.obstacles.remove(obstacle)
                self.score += 1
                
    def check_collision(self):
        for obstacle in self.obstacles:
            if (self.plane_x + self.plane_size > obstacle['x'] and 
                self.plane_x < obstacle['x'] + 50):
                if (self.plane_y < obstacle['top_height'] or 
                    self.plane_y > obstacle['bottom_height']):
                    return True
        return False
        
    def run(self):
        while not self.game_over:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(rgb_frame)
            game_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                self.plane_y = int(hand_landmarks.landmark[8].y * self.height)
                self.plane_y = max(50, min(self.height - 50, self.plane_y))
            
            # Update game state
            self.update_game_state()
            
            # Draw game
            game_frame = self.draw_game(frame, game_frame)
            
            # Check collisions
            if self.check_collision():
                self.game_over = True
                cv2.putText(game_frame, "Game Over!", (self.width//3, self.height//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            # Show frames
            cv2.imshow("Hand Control", frame)
            cv2.imshow("Airplane Game", game_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cleanup()
        
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Instructions:")
    print("- Use your index finger to control the airplane")
    print("- Avoid the green obstacles")
    print("- Move up/down to navigate through gaps")
    print("- Press 'q' to quit")
    
    game = AirplaneGame()
    game.run()