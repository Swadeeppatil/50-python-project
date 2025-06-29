import pygame
import random
import math
import json

class GTAGame:
    def __init__(self):
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("2D GTA")
        
        # Game states
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_vehicle = False
        self.money = 1000
        self.health = 100
        self.current_weapon = None
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Player properties
        self.player_pos = [self.screen_width//2, self.screen_height//2]
        self.player_speed = 5
        self.player_size = 20
        self.player_angle = 0
        
        # Vehicle properties
        self.vehicles = []
        self.generate_vehicles(5)  # Generate 5 vehicles
        
        # NPC properties
        self.npcs = []
        self.generate_npcs(10)  # Generate 10 NPCs
        
        # Buildings
        self.buildings = []
        self.generate_buildings(15)  # Generate 15 buildings
        
        # Missions
        self.missions = [
            {"type": "delivery", "start": (100, 100), "end": (700, 700), "reward": 500},
            {"type": "chase", "target": (500, 500), "reward": 750},
        ]
        self.current_mission = None
        
    def generate_vehicles(self, count):
        for _ in range(count):
            self.vehicles.append({
                "pos": [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                "color": (random.randint(0, 255), random.randint(0, 255), 
                         random.randint(0, 255)),
                "speed": 0,
                "angle": 0
            })
    
    def generate_npcs(self, count):
        for _ in range(count):
            self.npcs.append({
                "pos": [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                "color": (random.randint(0, 255), random.randint(0, 255), 
                         random.randint(0, 255)),
                "type": random.choice(["civilian", "enemy", "mission_giver"])
            })
    
    def generate_buildings(self, count):
        for _ in range(count):
            self.buildings.append({
                "pos": [random.randint(0, self.screen_width),
                       random.randint(0, self.screen_height)],
                "size": (random.randint(50, 150), random.randint(50, 150)),
                "color": (random.randint(100, 200), random.randint(100, 200), 
                         random.randint(100, 200))
            })
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Player movement
        if not self.in_vehicle:
            if keys[pygame.K_w]:
                self.player_pos[1] -= self.player_speed
            if keys[pygame.K_s]:
                self.player_pos[1] += self.player_speed
            if keys[pygame.K_a]:
                self.player_pos[0] -= self.player_speed
            if keys[pygame.K_d]:
                self.player_pos[0] += self.player_speed
        else:
            # Vehicle controls
            if keys[pygame.K_w]:
                self.vehicles[0]["speed"] += 0.1
            if keys[pygame.K_s]:
                self.vehicles[0]["speed"] -= 0.1
            if keys[pygame.K_a]:
                self.vehicles[0]["angle"] -= 2
            if keys[pygame.K_d]:
                self.vehicles[0]["angle"] += 2
                
            # Update player position with vehicle
            self.player_pos = self.vehicles[0]["pos"]
            
        # Enter/exit vehicle
        if keys[pygame.K_e]:
            self.try_enter_vehicle()
            
        # Attack
        if keys[pygame.K_SPACE]:
            self.attack()
    
    def try_enter_vehicle(self):
        if not self.in_vehicle:
            for vehicle in self.vehicles:
                dist = math.sqrt((vehicle["pos"][0] - self.player_pos[0])**2 + 
                               (vehicle["pos"][1] - self.player_pos[1])**2)
                if dist < 50:  # Vehicle entry range
                    self.in_vehicle = True
                    vehicle["pos"] = self.player_pos.copy()
                    break
        else:
            self.in_vehicle = False
    
    def attack(self):
        # Simple attack mechanism
        for npc in self.npcs:
            dist = math.sqrt((npc["pos"][0] - self.player_pos[0])**2 + 
                           (npc["pos"][1] - self.player_pos[1])**2)
            if dist < 30 and npc["type"] == "enemy":  # Attack range
                self.health -= 5  # Take damage from enemy
                self.money += 50  # Reward for hitting enemy
    
    def update(self):
        # Update vehicle positions
        for vehicle in self.vehicles:
            if self.in_vehicle and vehicle == self.vehicles[0]:
                angle_rad = math.radians(vehicle["angle"])
                vehicle["pos"][0] += math.cos(angle_rad) * vehicle["speed"]
                vehicle["pos"][1] += math.sin(angle_rad) * vehicle["speed"]
                vehicle["speed"] *= 0.99  # Friction
        
        # Update NPCs
        for npc in self.npcs:
            if npc["type"] == "civilian":
                # Random movement
                npc["pos"][0] += random.randint(-2, 2)
                npc["pos"][1] += random.randint(-2, 2)
        
        # Check mission completion
        if self.current_mission:
            if self.current_mission["type"] == "delivery":
                dist = math.sqrt((self.current_mission["end"][0] - self.player_pos[0])**2 + 
                               (self.current_mission["end"][1] - self.player_pos[1])**2)
                if dist < 20:
                    self.money += self.current_mission["reward"]
                    self.current_mission = None
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw buildings
        for building in self.buildings:
            pygame.draw.rect(self.screen, building["color"], 
                           (building["pos"][0], building["pos"][1], 
                            building["size"][0], building["size"][1]))
        
        # Draw vehicles
        for vehicle in self.vehicles:
            pygame.draw.rect(self.screen, vehicle["color"], 
                           (vehicle["pos"][0]-15, vehicle["pos"][1]-25, 30, 50))
        
        # Draw NPCs
        for npc in self.npcs:
            color = self.RED if npc["type"] == "enemy" else self.GREEN
            pygame.draw.circle(self.screen, color, 
                             (int(npc["pos"][0]), int(npc["pos"][1])), 10)
        
        # Draw player
        pygame.draw.circle(self.screen, self.BLUE, 
                         (int(self.player_pos[0]), int(self.player_pos[1])), 
                         self.player_size)
        
        # Draw HUD
        self.draw_hud()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Health bar
        pygame.draw.rect(self.screen, self.RED, (10, 10, 100, 20))
        pygame.draw.rect(self.screen, self.GREEN, 
                        (10, 10, self.health, 20))
        
        # Money display
        font = pygame.font.Font(None, 36)
        money_text = font.render(f"${self.money}", True, self.WHITE)
        self.screen.blit(money_text, (10, 40))
        
        # Mission objective
        if self.current_mission:
            mission_text = font.render(
                f"Mission: {self.current_mission['type']}", True, self.WHITE
            )
            self.screen.blit(mission_text, (10, 70))
    
    def run(self):
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:  # Start mission
                        if not self.current_mission and self.missions:
                            self.current_mission = self.missions[0]
            
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = GTAGame()
    game.run()