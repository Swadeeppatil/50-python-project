import cv2
import numpy as np
import random
import time

class CricketVisionGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.score = 0
        self.balls = 0
        self.wickets = 0
        self.game_over = False
        
        # Ball parameters
        self.ball_pos = [320, 50]
        self.ball_speed = 5
        self.ball_active = False
        
        # Bat detection parameters
        self.lower_color = np.array([0, 100, 100])  # Red color range
        self.upper_color = np.array([10, 255, 255])
        
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            game_frame = self.process_frame(frame)
            
            # Show game stats
            cv2.putText(game_frame, f"Score: {self.score}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(game_frame, f"Balls: {self.balls}/6", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(game_frame, f"Wickets: {self.wickets}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow("Cricket Vision Game", game_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q') or self.game_over:
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        
    def process_frame(self, frame):
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Find bat contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bat_detected = False
        
        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Minimum area threshold
                bat_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Check bat collision with ball
                if self.ball_active:
                    if (x < self.ball_pos[0] < x+w and 
                        y < self.ball_pos[1] < y+h):
                        self.handle_hit()
        
        # Ball logic
        if not self.ball_active:
            self.start_new_ball()
        else:
            self.update_ball_position(frame)
            
        # Draw ball
        cv2.circle(frame, (int(self.ball_pos[0]), int(self.ball_pos[1])),
                  10, (0, 0, 255), -1)
        
        return frame
        
    def start_new_ball(self):
        if self.balls < 6 and self.wickets < 3:
            self.ball_pos = [random.randint(100, 540), 50]
            self.ball_active = True
            self.balls += 1
        else:
            self.game_over = True
            
    def update_ball_position(self, frame):
        self.ball_pos[1] += self.ball_speed
        
        # Ball missed
        if self.ball_pos[1] > frame.shape[0] - 10:
            self.wickets += 1
            self.ball_active = False
            
    def handle_hit(self):
        self.ball_active = False
        run_scored = random.choice([1, 2, 4, 6])
        self.score += run_scored
        
        # Display run scored
        cv2.putText(self.cap.read()[1], f"{run_scored} RUNS!", (250, 250),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.waitKey(500)

if __name__ == "__main__":
    print("Hold a red object as bat. Press 'q' to quit.")
    print("Game Rules:")
    print("- Use red colored object as bat")
    print("- Hit the moving ball")
    print("- Score runs: 1, 2, 4, or 6")
    print("- 6 balls per game")
    print("- 3 wickets limit")
    
    game = CricketVisionGame()
    game.run()