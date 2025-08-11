import pygame
import random
import math
from sprites import Player, Spike, Wall

class Game:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera_x = 0
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.game_speed = 3
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.flat_walls = pygame.sprite.Group()
        self.angled_walls = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        
        # Initialize player
        self.player = Player(100, screen_height // 2)
        self.all_sprites.add(self.player)
        
        # Create walls and obstacles
        self.wall_segments = 20
        self.wall_segment_width = 200
        self.generate_walls()
        self.generate_spikes()
        
        # Set up fonts
        self.font = pygame.font.SysFont(None, 36)
        
        # Colors
        self.bg_color = (180, 0, 0)  # Dark red background
        self.wall_color = (255, 0, 0)  # Brighter red for walls
        self.text_color = (255, 255, 255)  # White text
        
        # Gameplay state
        self.last_wall_hit = "bottom"  # or "top"
        self.is_mouse_down = False
    
    def generate_walls(self):
        self.top_wall_points = []
        self.bottom_wall_points = []
        
        # Generate the zigzag patterns for top and bottom walls
        for i in range(self.wall_segments):
            x = i * self.wall_segment_width
            
            # Top wall
            top_y_start = random.randint(100, 200)
            top_points = self.generate_zigzag(x, top_y_start, self.wall_segment_width, 50, "top")
            self.top_wall_points.extend(top_points)
            
            # Bottom wall
            bottom_y_start = random.randint(self.screen_height - 200, self.screen_height - 100)
            bottom_points = self.generate_zigzag(x, bottom_y_start, self.wall_segment_width, 50, "bottom")
            self.bottom_wall_points.extend(bottom_points)
        
        # Create wall segments
        self.create_wall_segments(self.top_wall_points, "top")
        self.create_wall_segments(self.bottom_wall_points, "bottom")
    
    def create_wall_segments(self, points, wall_type):
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Check if this is a horizontal segment (flat)
            is_flat = abs(y2 - y1) < 5
            
            # Create a wall segment
            wall = Wall(x1, y1, x2, y2, is_flat, wall_type)
            self.walls.add(wall)
            self.all_sprites.add(wall)
            
            # Add wall to appropriate group
            if is_flat:
                self.flat_walls.add(wall)
            else:
                self.angled_walls.add(wall)
                self.obstacles.add(wall)  # Angled walls are obstacles
    
    def generate_zigzag(self, start_x, start_y, width, height, wall_type):
        points = []
        segments = 4
        segment_width = width / segments
        
        for i in range(segments + 1):
            x = start_x + i * segment_width
            
            # Alternate high and low points
            if i % 2 == 0:
                y = start_y
            else:
                if wall_type == "top":
                    y = start_y + height
                else:
                    y = start_y - height
            
            points.append((x, y))
        
        return points
    
    def generate_spikes(self):
        # Create some spike obstacles between the walls
        for i in range(10):
            x = random.randint(500, self.wall_segments * self.wall_segment_width - 500)
            
            # Find safe y range between walls
            top_y = 200  # Minimum safe distance from top
            bottom_y = self.screen_height - 200  # Minimum safe distance from bottom
            
            if bottom_y - top_y > 80:  # Make sure there's enough room
                y = random.randint(top_y, bottom_y)
                spike = Spike(x, y, 30)
                self.spikes.add(spike)
                self.obstacles.add(spike)
                self.all_sprites.add(spike)
    
    def update(self):
        if self.game_over:
            return
        
        # Update camera position - this controls the player's x movement
        self.camera_x += self.game_speed
        
        # Update player
        self.player.update()
        
        # Handle wall and obstacle collisions
        self.handle_wall_collisions()
        self.check_obstacle_collisions()
        
        # Keep player within reasonable horizontal bounds
        if self.player.rect.left < 50:
            self.player.rect.left = 50
            self.handle_game_over()  # Player too far left
        elif self.player.rect.right > self.screen_width - 50:
            self.player.rect.right = self.screen_width - 50
        
        # Update score
        self.score = int(self.camera_x / 10)
        
        # Update player angle based on mouse state
        self.update_player_angle()
    
    def handle_wall_collisions(self):
        player_adjusted_x = self.player.rect.centerx + self.camera_x
        
        # Check for collisions with flat walls
        for wall in self.flat_walls:
            if wall.x1 <= player_adjusted_x <= wall.x2:
                # Calculate wall y at player's x position
                if abs(wall.x2 - wall.x1) < 0.001:
                    wall_y = wall.y1
                else:
                    t = (player_adjusted_x - wall.x1) / (wall.x2 - wall.x1)
                    wall_y = wall.y1 + t * (wall.y2 - wall.y1)
                
                # Check if player is colliding with this wall
                if wall.wall_type == "top" and self.player.rect.top <= wall_y:
                    self.player.rect.top = wall_y + 1
                    self.player.bounce("top")
                    self.last_wall_hit = "top"
                    
                elif wall.wall_type == "bottom" and self.player.rect.bottom >= wall_y:
                    self.player.rect.bottom = wall_y - 1
                    self.player.bounce("bottom")
                    self.last_wall_hit = "bottom"
    
    def check_obstacle_collisions(self):
        # Check for collisions with spikes
        for spike in self.spikes:
            spike.screen_x = self.camera_x
            if spike.check_collision(self.player):
                self.handle_game_over()
                return
        
        # Check for collisions with angled walls
        for wall in self.angled_walls:
            wall.screen_x = self.camera_x
            if wall.check_collision(self.player):
                self.handle_game_over()
                return
    
    def handle_mouse_down(self):
        if self.game_over:
            return
        
        self.is_mouse_down = True
        self.update_player_angle()
    
    def handle_mouse_up(self):
        if self.game_over:
            return
        
        self.is_mouse_down = False
        self.update_player_angle()

    def update_player_angle(self):
        # Apply the new angle logic based on mouse state and last wall hit
        if self.last_wall_hit == "bottom":
            if self.is_mouse_down:
                # When clicking after hitting bottom wall, go up 60 degrees to the left
                self.player.change_angle(-60)
            else:
                # When releasing after hitting bottom wall, mirror the movement (go up 60 degrees to the right)
                self.player.change_angle(60)  # Mirror angle on the other side
        else:  # top wall
            if self.is_mouse_down:
                # When clicking after hitting top wall, go down 60 degrees to the left
                self.player.change_angle(120)  # 120° is down and to the left
            else:
                # When releasing after hitting top wall, go down 60 degrees to the right
                self.player.change_angle(60)  # 60° is down and to the right
    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)
        
        # Draw a grid pattern
        self.draw_grid_pattern(screen)
        
        # Draw walls (using the points)
        self.draw_walls(screen)
        
        # Draw spikes
        for spike in self.spikes:
            spike.draw(screen, self.camera_x)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw score
        score_text = self.font.render(f"{self.score}m", True, self.text_color)
        screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 20))
        
        # Draw high score
        high_score_text = self.font.render(f"highscore: {self.high_score}m", True, self.text_color)
        screen.blit(high_score_text, (self.screen_width - high_score_text.get_width() - 20, 20))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, self.text_color)
            screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, 
                                        self.screen_height // 2))
    
    def draw_grid_pattern(self, screen):
        # Draw a grid pattern
        grid_size = 20
        for x in range(0, self.screen_width, grid_size):
            for y in range(0, self.screen_height, grid_size):
                pygame.draw.line(screen, (150, 0, 0), (x, 0), (x, self.screen_height), 1)
                pygame.draw.line(screen, (150, 0, 0), (0, y), (self.screen_width, y), 1)
    
    def draw_walls(self, screen):
        # Draw top wall
        adjusted_top_wall = [(x - self.camera_x, y) for x, y in self.top_wall_points]
        if len(adjusted_top_wall) > 1:
            pygame.draw.lines(screen, self.wall_color, False, adjusted_top_wall, 3)
            
            # Fill the area above the top wall
            polygon_points = adjusted_top_wall.copy()
            polygon_points.insert(0, (adjusted_top_wall[0][0], 0))
            polygon_points.append((adjusted_top_wall[-1][0], 0))
            pygame.draw.polygon(screen, self.wall_color, polygon_points)
        
        # Draw bottom wall
        adjusted_bottom_wall = [(x - self.camera_x, y) for x, y in self.bottom_wall_points]
        if len(adjusted_bottom_wall) > 1:
            pygame.draw.lines(screen, self.wall_color, False, adjusted_bottom_wall, 3)
            
            # Fill the area below the bottom wall
            polygon_points = adjusted_bottom_wall.copy()
            polygon_points.insert(0, (adjusted_bottom_wall[0][0], self.screen_height))
            polygon_points.append((adjusted_bottom_wall[-1][0], self.screen_height))
            pygame.draw.polygon(screen, self.wall_color, polygon_points)
    
    def handle_game_over(self):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
    
    def reset(self):
        # Reset game state
        self.camera_x = 0
        self.score = 0
        self.game_over = False
        self.last_wall_hit = "bottom"
        self.is_mouse_down = False
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.obstacles.empty()
        self.walls.empty()
        self.flat_walls.empty()
        self.angled_walls.empty()
        self.spikes.empty()
        
        # Create new player
        self.player = Player(100, self.screen_height // 2)
        self.all_sprites.add(self.player)
        
        # Regenerate walls and spikes
        self.generate_walls()
        self.generate_spikes()