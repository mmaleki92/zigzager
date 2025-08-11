import pygame
import sys
from game import Game

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Zigzag Arrow Game")
    
    # Create game instance
    game = Game(screen_width, screen_height)
    
    # Game loop
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_mouse_down()
            elif event.type == pygame.MOUSEBUTTONUP:
                game.handle_mouse_up()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.reset()
        
        # Update game
        game.update()
        
        # Draw everything
        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()