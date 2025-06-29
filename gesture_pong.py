import cv2
import numpy as np
import mediapipe as mp
import random

class GesturePong:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        
        # Game variables
        self.player_paddle_y = 300
        self.computer_paddle_y = 300
        self.ball_pos = [400, 300]
        self.ball_speed = [7, 7]
        self.score = [0, 0]
        
        # Window size
        self.width = 800
        self.height = 600
        
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.width, self.height))
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Get hand position
                    index_y = hand_landmarks.landmark[8].y
                    self.player_paddle_y = int(index_y * self.height)
            
            # Create game frame
            game_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            # Draw paddles
            cv2.rectangle(game_frame, (50, self.player_paddle_y - 50),
                         (70, self.player_paddle_y + 50), (255, 255, 255), -1)
            cv2.rectangle(game_frame, (self.width - 70, self.computer_paddle_y - 50),
                         (self.width - 50, self.computer_paddle_y + 50),
                         (255, 255, 255), -1)
            
            # Update ball position
            self.ball_pos[0] += self.ball_speed[0]
            self.ball_pos[1] += self.ball_speed[1]
            
            # Ball collisions
            # Top and bottom walls
            if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.height:
                self.ball_speed[1] *= -1
                
            # Paddles
            if self.ball_pos[0] <= 70 and abs(self.ball_pos[1] - self.player_paddle_y) < 50:
                self.ball_speed[0] *= -1
            elif (self.ball_pos[0] >= self.width - 70 and 
                  abs(self.ball_pos[1] - self.computer_paddle_y) < 50):
                self.ball_speed[0] *= -1
                
            # Scoring
            if self.ball_pos[0] <= 0:
                self.score[1] += 1
                self.reset_ball()
            elif self.ball_pos[0] >= self.width:
                self.score[0] += 1
                self.reset_ball()
                
            # Move computer paddle
            if self.computer_paddle_y < self.ball_pos[1]:
                self.computer_paddle_y += 5
            else:
                self.computer_paddle_y -= 5
                
            # Draw ball
            cv2.circle(game_frame, (int(self.ball_pos[0]), int(self.ball_pos[1])),
                      10, (255, 255, 255), -1)
            
            # Draw scores
            cv2.putText(game_frame, str(self.score[0]), (self.width//4, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.putText(game_frame, str(self.score[1]), (3*self.width//4, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            
            # Show frames
            cv2.imshow("Hand Detection", frame)
            cv2.imshow("Pong Game", game_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    def reset_ball(self):
        self.ball_pos = [self.width//2, self.height//2]
        self.ball_speed[0] = random.choice([-7, 7])
        self.ball_speed[1] = random.choice([-7, 7])
        
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Instructions:")
    print("- Move your hand up/down to control the paddle")
    print("- Use index finger for precise control")
    print("- Press 'q' to quit")
    
    game = GesturePong()
    try:
        game.run()
    finally:
        game.cleanup()