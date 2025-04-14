import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10  # Game speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake with Power-ups")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()
    
    def reset_game(self):
        # Game state
        self.game_over = False
        self.score = 0
        
        # Snake initialization
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start in the middle
        self.direction = RIGHT
        self.next_direction = RIGHT
        
        # Food initialization
        self.food = self.generate_food()
        
        # Power-up initialization
        self.power_up = None
        self.power_up_timer = 0
        self.power_up_active = False
        self.power_up_type = None
        self.speed_boost = False
        self.next_power_up_time = random.randint(10, 20)  # Seconds until first power-up
        self.power_up_start_time = time.time()  # Initialize start time

        # Speed tracking
        self.current_fps = FPS
    
    def generate_food(self):
        # Generate food in a position not occupied by the snake
        while True:
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if position not in self.snake:
                return position
    
    def generate_power_up(self):
        # Types of power-ups:
        # 1. Speed boost - temporarily increases snake speed
        # 2. Double points - temporarily doubles point value of food
        # 3. Ghost mode - temporarily allows passing through walls
        power_up_type = random.choice(["speed", "double", "ghost"])
        
        # Generate power-up in a position not occupied by snake or food
        while True:
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if position not in self.snake and position != self.food:
                return position, power_up_type
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                elif event.key == pygame.K_UP and self.direction != DOWN:
                    self.next_direction = UP
                elif event.key == pygame.K_DOWN and self.direction != UP:
                    self.next_direction = DOWN
                elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                    self.next_direction = LEFT
                elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                    self.next_direction = RIGHT
    
    def update(self):
        if self.game_over:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Move snake
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        
        # Check for collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Check for collision with walls if ghost mode is not active
        if not (self.power_up_type == "ghost" and self.power_up_active):
            if (head_x + dx < 0 or head_x + dx >= GRID_WIDTH or 
                head_y + dy < 0 or head_y + dy >= GRID_HEIGHT):
                self.game_over = True
                return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check for food collision
        if new_head == self.food:
            self.food = self.generate_food()
            
            # Calculate points based on power-up
            points = 10
            if self.power_up_type == "double" and self.power_up_active:
                points = 20
                
            self.score += points
        else:
            # Remove tail only if no food was eaten
            self.snake.pop()
        
        # Handle power-ups
        current_time = time.time()
        
        # Generate new power-up if time has elapsed
        if self.power_up is None:
            if current_time - self.power_up_start_time > self.next_power_up_time:
                self.power_up, self.power_up_type = self.generate_power_up()
                self.next_power_up_time = random.randint(10, 20)
                self.power_up_start_time = current_time
        
        # Check for power-up collision
        elif new_head == self.power_up:
            self.power_up = None
            self.power_up_active = True
            self.power_up_timer = current_time
            
            # Apply immediate effects
            if self.power_up_type == "speed":
                self.current_fps = FPS * 1.5  # 50% faster
            
        # Check if active power-up has expired (5 seconds)
        if self.power_up_active and current_time - self.power_up_timer > 5:
            self.power_up_active = False
            self.power_up_type = None
            self.current_fps = FPS  # Reset speed
    
    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = GREEN
            
            # Change head color based on active power-up
            if i == 0 and self.power_up_active:
                if self.power_up_type == "speed":
                    color = BLUE
                elif self.power_up_type == "double":
                    color = GOLD
                elif self.power_up_type == "ghost":
                    color = PURPLE
            
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)  # Border
        
        # Draw food
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, RED, food_rect)
        
        # Draw power-up if available
        if self.power_up:
            power_up_rect = pygame.Rect(self.power_up[0] * GRID_SIZE, self.power_up[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            color = BLUE  # Default
            if self.power_up_type == "double":
                color = GOLD
            elif self.power_up_type == "ghost":
                color = PURPLE
                
            pygame.draw.rect(self.screen, color, power_up_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw active power-up status
        if self.power_up_active and self.power_up_type:
            power_text = ""
            color = WHITE
            
            if self.power_up_type == "speed":
                power_text = "SPEED BOOST!"
                color = BLUE
            elif self.power_up_type == "double":
                power_text = "DOUBLE POINTS!"
                color = GOLD
            elif self.power_up_type == "ghost":
                power_text = "GHOST MODE!"
                color = PURPLE
            
            # Only render if we have a valid power text
            if power_text:
                power_text_surface = self.font.render(power_text, True, color)
                self.screen.blit(power_text_surface, (WIDTH - power_text_surface.get_width() - 10, 10))
                
                # Show countdown
                time_left = int(5 - (time.time() - self.power_up_timer))
                if time_left >= 0:
                    timer_text = self.font.render(f"{time_left}s", True, color)
                    self.screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 40))
        
        # Game over screen
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.current_fps)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
