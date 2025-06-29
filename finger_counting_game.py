import cv2
import numpy as np
import mediapipe as mp
import random
import time

class FingerCountingGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils
        
        self.score = 0
        self.target_number = 0
        self.game_time = 30
        self.start_time = time.time()
        self.game_over = False
        
        # Generate first target
        self.new_target()
        
    def new_target(self):
        self.target_number = random.randint(1, 5)
        
    def count_fingers(self, hand_landmarks):
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Little
        thumb_tip = 4
        count = 0
        
        # Check thumb
        if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
            count += 1
            
        # Check other fingers
        for tip in finger_tips:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                count += 1
                
        return count
        
    def run(self):
        while not self.game_over:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Draw game info
            remaining_time = max(0, int(self.game_time - (time.time() - self.start_time)))
            cv2.putText(frame, f"Score: {self.score}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Time: {remaining_time}s", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Show {self.target_number} fingers", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(frame, hand_landmarks,
                                             self.mp_hands.HAND_CONNECTIONS)
                    
                    # Count fingers
                    finger_count = self.count_fingers(hand_landmarks)
                    
                    # Check if correct
                    if finger_count == self.target_number:
                        self.score += 1
                        self.new_target()
                        time.sleep(0.5)  # Brief delay to prevent multiple counts
                        
            # Check if game is over
            if remaining_time <= 0:
                self.game_over = True
                cv2.putText(frame, "Game Over!", (200, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.putText(frame, f"Final Score: {self.score}", (200, 300),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            cv2.imshow("Finger Counting Game", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Instructions:")
    print("- Show the requested number of fingers")
    print("- Score points for correct counts")
    print("- Game lasts 30 seconds")
    print("- Press 'q' to quit")
    
    game = FingerCountingGame()
    game.run()