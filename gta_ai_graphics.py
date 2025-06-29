import pygame
import requests
import io
import base64
import random
import math
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import os
from dotenv import load_dotenv

class GTAWithAI:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("GTA AI Graphics")
        
        # Load environment variables for API keys
        load_dotenv()
        self.stability_key = os.getenv('STABILITY_KEY')
        
        # Initialize Stability AI client
        self.stability_api = client.StabilityInference(
            key=self.stability_key,
            verbose=True,
        )
        
        # Game states
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = {}
        self.player = None
        self.vehicles = []
        self.npcs = []
        self.buildings = []
        
        # Generate initial assets
        self.generate_game_assets()
        self.setup_game_world()
        
    def generate_ai_image(self, prompt, size=(512, 512)):
        try:
            answers = self.stability_api.generate(
                prompt=prompt,
                seed=random.randint(0, 1000000),
                steps=30,
                cfg_scale=7.0,
                width=size[0],
                height=size[1],
                samples=1,
                sampler=generation.SAMPLER_K_DPMPP_2M
            )
            
            for answer in answers:
                img_data = answer.artifacts[0].binary
                img = Image.open(io.BytesIO(img_data))
                return pygame.image.fromstring(
                    img.tobytes(), img.size, img.mode
                ).convert_alpha()
        except Exception as e:
            print(f"Error generating image: {e}")
            return self.create_fallback_surface(size)
            
    def create_fallback_surface(self, size):
        surface = pygame.Surface(size)
        surface.fill((100, 100, 100))
        return surface
        
    def generate_game_assets(self):
        print("Generating game assets with AI...")
        
        # Generate player character
        self.assets['player'] = self.generate_ai_image(
            "pixel art top-down view of a modern game character, GTA style"
        )
        
        # Generate vehicle
        self.assets['car'] = self.generate_ai_image(
            "pixel art top-down view of a modern car, GTA style"
        )
        
        # Generate building
        self.assets['building'] = self.generate_ai_image(
            "pixel art top-down view of a modern building, GTA style"
        )
        
        # Generate NPC
        self.assets['npc'] = self.generate_ai_image(
            "pixel art top-down view of a person walking, GTA style"
        )
        
        print("Asset generation complete!")
        
    def setup_game_world(self):
        # Player setup
        self.player = {
            'pos': [self.screen_width//2, self.screen_height//2],
            'speed': 5,
            'angle': 0,
            'in_vehicle': False
        }
        
        # Generate vehicles
        for _ in range(5):
            self.vehicles.append({
                'pos': [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                'angle': random.randint(0, 360),
                'speed': 0
            })
            
        # Generate NPCs
        for _ in range(10):
            self.npcs.append({
                'pos': [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                'angle': random.randint(0, 360),
                'type': random.choice(['civilian', 'enemy'])
            })
            
        # Generate buildings
        for _ in range(15):
            self.buildings.append({
                'pos': [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                'size': (random.randint(100, 200), random.randint(100, 200))
            })
            
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.player['in_vehicle']:
            # Walking controls
            if keys[pygame.K_w]: self.player['pos'][1] -= self.player['speed']
            if keys[pygame.K_s]: self.player['pos'][1] += self.player['speed']
            if keys[pygame.K_a]: self.player['pos'][0] -= self.player['speed']
            if keys[pygame.K_d]: self.player['pos'][0] += self.player['speed']
            
            # Enter vehicle
            if keys[pygame.K_e]:
                self.try_enter_vehicle()
        else:
            # Driving controls
            vehicle = self.get_player_vehicle()
            if vehicle:
                if keys[pygame.K_w]: vehicle['speed'] += 0.1
                if keys[pygame.K_s]: vehicle['speed'] -= 0.1
                if keys[pygame.K_a]: vehicle['angle'] -= 2
                if keys[pygame.K_d]: vehicle['angle'] += 2
                
                # Exit vehicle
                if keys[pygame.K_e]:
                    self.player['in_vehicle'] = False
                    
    def try_enter_vehicle(self):
        for vehicle in self.vehicles:
            dist = math.sqrt((vehicle['pos'][0] - self.player['pos'][0])**2 +
                           (vehicle['pos'][1] - self.player['pos'][1])**2)
            if dist < 50:
                self.player['in_vehicle'] = True
                break
                
    def get_player_vehicle(self):
        if self.player['in_vehicle']:
            return self.vehicles[0]
        return None
        
    def update(self):
        # Update vehicles
        for vehicle in self.vehicles:
            if vehicle == self.get_player_vehicle():
                angle_rad = math.radians(vehicle['angle'])
                vehicle['pos'][0] += math.cos(angle_rad) * vehicle['speed']
                vehicle['pos'][1] += math.sin(angle_rad) * vehicle['speed']
                vehicle['speed'] *= 0.98  # Friction
                
                # Update player position with vehicle
                self.player['pos'] = vehicle['pos'].copy()
                
        # Update NPCs
        for npc in self.npcs:
            if npc['type'] == 'civilian':
                npc['pos'][0] += math.cos(math.radians(npc['angle'])) * 1
                npc['pos'][1] += math.sin(math.radians(npc['angle'])) * 1
                
                if random.random() < 0.02:  # 2% chance to change direction
                    npc['angle'] = random.randint(0, 360)
                    
    def draw(self):
        self.screen.fill((50, 50, 50))  # Gray background
        
        # Draw buildings
        for building in self.buildings:
            scaled_building = pygame.transform.scale(
                self.assets['building'], building['size']
            )
            self.screen.blit(scaled_building, building['pos'])
            
        # Draw vehicles
        for vehicle in self.vehicles:
            rotated_car = pygame.transform.rotate(
                self.assets['car'], -vehicle['angle']
            )
            self.screen.blit(rotated_car, vehicle['pos'])
            
        # Draw NPCs
        for npc in self.npcs:
            rotated_npc = pygame.transform.rotate(
                self.assets['npc'], -npc['angle']
            )
            self.screen.blit(rotated_npc, npc['pos'])
            
        # Draw player if not in vehicle
        if not self.player['in_vehicle']:
            self.screen.blit(self.assets['player'], self.player['pos'])
            
        pygame.display.flip()
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = GTAWithAI()
    game.run()