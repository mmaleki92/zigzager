import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 10
        self.speed = 2
        self.angle = 0  # Starting angle (straight right)
        self.color = (255, 255, 255)  # White
        
        # Create surface and rect
        self.image = pygame.Surface((self.size * 3, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Movement components
        self.dx = self.speed  # Always move right at constant speed
        self.dy = 0  # Initial vertical movement is 0
        
        # Draw initial arrow
        self.update_image()
    
    def update(self):
        # Update position based on velocity
        self.rect.y += self.dy
        
        # Note: x position is not updated here, as the game handles this with camera movement
        
        # Basic boundary checks for screen edges (shouldn't be needed with walls, but just in case)
        if self.rect.top < 0:
            self.rect.top = 0
            self.angle = 0
            self.dy = 0
            self.update_image()
        elif self.rect.bottom > 600:
            self.rect.bottom = 600
            self.angle = 0
            self.dy = 0
            self.update_image()
    
    def change_angle(self, new_angle):
        # Change angle of movement
        self.angle = new_angle
        
        # Update only vertical velocity component
        # X velocity is constant and managed by the camera
        self.dy = math.sin(math.radians(self.angle)) * self.speed
        
        # Update arrow image to match new angle
        self.update_image()
    
    def bounce(self, wall_type):
        # Reset angle to 0 when hitting any wall
        self.angle = 0
        self.dy = 0
        self.update_image()
    
    def update_image(self):
        # Clear previous image
        self.image.fill((0, 0, 0, 0))
        
        # Calculate arrow points based on current angle
        center_x, center_y = self.rect.width // 2, self.rect.height // 2
        
        # Calculate direction vector - always pointing right with the y component varying
        direction_x = math.cos(math.radians(self.angle))
        direction_y = math.sin(math.radians(self.angle))
        
        # Calculate triangle points for the arrow
        p1 = (center_x + direction_x * self.size,
              center_y + direction_y * self.size)  # Tip
        p2 = (center_x - direction_x * self.size - direction_y * self.size/2,
              center_y - direction_y * self.size + direction_x * self.size/2)  # Left wing
        p3 = (center_x - direction_x * self.size + direction_y * self.size/2,
              center_y - direction_y * self.size - direction_x * self.size/2)  # Right wing
        
        # Draw the arrow
        pygame.draw.polygon(self.image, self.color, [p1, p2, p3])
    
    def draw(self, screen):
        # Draw the sprite at its current position
        screen.blit(self.image, self.rect)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, is_flat, wall_type):
        super().__init__()
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_flat = is_flat
        self.wall_type = wall_type  # "top" or "bottom"
        self.color = (255, 0, 0)
        self.width = 3
        self.screen_x = 0  # Will be adjusted for camera
        
        # For collision detection
        self.x = (x1 + x2) / 2  # Center point
        self.y = (y1 + y2) / 2
        
        # Calculate length and angle
        self.length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        self.angle = math.atan2(y2 - y1, x2 - x1)
        
        # Create hitbox (not used for drawing, just for collision)
        thickness = 5 if is_flat else 3
        self.image = pygame.Surface((int(self.length), thickness), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def check_collision(self, player):
        # Only check collision if this is not a flat wall (we handle flat walls separately)
        if not self.is_flat:
            # Adjust for camera position
            adjusted_x1 = self.x1 - self.screen_x
            adjusted_x2 = self.x2 - self.screen_x
            
            # Line segment collision with circle (player)
            return self.line_circle_collision(
                adjusted_x1, self.y1,
                adjusted_x2, self.y2,
                player.rect.centerx, player.rect.centery, player.size
            )
        return False
    
    def line_circle_collision(self, line_x1, line_y1, line_x2, line_y2, circle_x, circle_y, radius):
        # Calculate vector from line start to circle center
        dx = circle_x - line_x1
        dy = circle_y - line_y1
        
        # Calculate line segment vector
        line_dx = line_x2 - line_x1
        line_dy = line_y2 - line_y1
        
        # Calculate length of line segment squared
        length_squared = line_dx**2 + line_dy**2
        if length_squared == 0:
            return False  # Line segment is actually a point
        
        # Calculate dot product
        dot_product = dx*line_dx + dy*line_dy
        
        # Calculate projection ratio (how far along the line the closest point is)
        t = max(0, min(1, dot_product / length_squared))
        
        # Calculate closest point on line to circle center
        closest_x = line_x1 + t * line_dx
        closest_y = line_y1 + t * line_dy
        
        # Calculate distance from circle center to closest point
        distance = math.sqrt((circle_x - closest_x)**2 + (circle_y - closest_y)**2)
        
        # Return True if distance is less than circle radius
        return distance <= radius
    
    def draw(self, screen, camera_x):
        # Walls are drawn by the game class using lines
        pass

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.color = (255, 0, 0)  # Red
        self.outline_color = (255, 255, 255)  # White
        self.screen_x = 0  # Will be adjusted for camera
        
        # Create surface and rect for spike
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Draw spike on the surface
        self.draw_spike_on_surface()
    
    def draw_spike_on_surface(self):
        # Draw spike as a triangle with a circle in the middle
        spike_points = [
            (self.size, 0),  # Top
            (0, self.size * 2),  # Bottom left
            (self.size * 2, self.size * 2)  # Bottom right
        ]
        
        # Draw spike outline
        pygame.draw.polygon(self.image, self.outline_color, spike_points, 3)
        
        # Draw inner circle
        pygame.draw.circle(self.image, (255, 0, 0), (self.size, self.size), self.size // 2)
        pygame.draw.circle(self.image, self.outline_color, (self.size, self.size), self.size // 2, 2)
    
    def check_collision(self, player):
        # Adjust x for camera position
        screen_pos_x = self.x - self.screen_x
        
        # Only check collision if on screen or within a reasonable distance
        if -self.size * 2 <= screen_pos_x <= 800 + self.size * 2:
            # Distance-based collision check
            dx = screen_pos_x - player.rect.centerx
            dy = self.y - player.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            return distance < self.size * 0.7 + player.size
        return False
    
    def draw(self, screen, camera_x):
        # Calculate on-screen position
        screen_x = self.x - camera_x
        
        # Only draw if on screen
        if -self.size*2 <= screen_x <= screen.get_width() + self.size*2:
            # Draw spike at correct position
            spike_rect = self.rect.copy()
            spike_rect.centerx = screen_x
            screen.blit(self.image, spike_rect)