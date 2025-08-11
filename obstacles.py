import pygame
import math

class Wall:
    def __init__(self, points, color=(255, 0, 0)):
        self.points = points
        self.color = color
    
    def draw(self, screen, camera_x):
        # Adjust points for camera position
        adjusted_points = [(x - camera_x, y) for x, y in self.points]
        pygame.draw.lines(screen, self.color, False, adjusted_points, 3)

class Spike:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.color = (255, 0, 0)  # Red
        self.outline_color = (255, 255, 255)  # White
    
    def draw(self, screen, camera_x):
        # Adjust x for camera position
        screen_x = self.x - camera_x
        
        # Only draw if on screen
        if -self.size <= screen_x <= screen.get_width() + self.size:
            # Draw spike as a triangle with a circle in the middle like in the image
            spike_points = [
                (screen_x, self.y - self.size),  # Top
                (screen_x - self.size, self.y + self.size),  # Bottom left
                (screen_x + self.size, self.y + self.size)   # Bottom right
            ]
            
            # Draw spike outline
            pygame.draw.polygon(screen, self.outline_color, spike_points, 3)
            
            # Draw inner circle
            pygame.draw.circle(screen, (255, 0, 0), (screen_x, self.y), self.size // 2)
            pygame.draw.circle(screen, self.outline_color, (screen_x, self.y), self.size // 2, 2)
    
    def check_collision(self, player):
        # Simple distance-based collision check
        dx = self.x - (player.x + player.dx)
        dy = self.y - (player.y + player.dy)
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance < self.size + player.size