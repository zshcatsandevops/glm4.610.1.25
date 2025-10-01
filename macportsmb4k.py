import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
JUMP_STRENGTH = -15
MAX_VEL_X = 8  # Maximum horizontal velocity to prevent out-of-bounds values

# Colors
WHITE = (255, 255, 255)
BLUE = (80, 80, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (165, 42, 42)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.acc_x = 0

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Handle horizontal movement with friction
        self.vel_x += self.acc_x
        # Fixed friction calculation - should be (1 + PLAYER_FRICTION) since PLAYER_FRICTION is negative
        self.vel_x *= (1 + PLAYER_FRICTION)
        
        # Clamp velocity to prevent out-of-bounds values
        self.vel_x = max(-MAX_VEL_X, min(MAX_VEL_X, self.vel_x))
        
        # Update position
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Keep player on screen (horizontal)
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0  # Stop velocity when hitting screen edge
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x = 0  # Stop velocity when hitting screen edge
            
        # Check if player fell off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

    def respawn(self):
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.vel_x = 0
        self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Level:
    def __init__(self, world_num, level_num):
        self.world_num = world_num
        self.level_num = level_num
        self.platforms = []
        self.goal = None
        self.background_color = (135, 206, 235)  # Default sky blue
        
        # Set theme based on world number
        self.set_theme()
        self.generate_level()

    def set_theme(self):
        # Different colors/themes for different worlds
        theme_colors = {
            1: (135, 206, 235),  # Sky Blue - Grassland
            2: (100, 149, 237),  # Cornflower Blue - Water
            3: (210, 180, 140),  # Tan - Desert
            4: (176, 224, 230),  # Powder Blue - Ice
            5: (119, 136, 153),  # Light Slate Gray - Mountain
            6: (147, 112, 219),  # Medium Purple - Magic
            7: (255, 165, 0),    # Orange - Fire
            8: (50, 205, 50),    # Lime Green - Forest
            9: (75, 0, 130)      # Indigo - Space
        }
        self.background_color = theme_colors.get(self.world_num, (135, 206, 235))

    def generate_level(self):
        # Always start with ground
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, BROWN))
        
        # Generate level layout based on world and level number
        base_height = SCREEN_HEIGHT - 40
        
        # Different platform patterns for each level in the world
        level_patterns = [
            self._pattern_easy_platforms,
            self._pattern_stairs,
            self._pattern_gaps,
            self._pattern_high_platforms,
            self._pattern_final_challenge
        ]
        
        pattern_func = level_patterns[(self.level_num - 1) % len(level_patterns)]
        pattern_func(base_height)
        
        # Place goal at the end
        goal_x = SCREEN_WIDTH - 100
        goal_y = base_height - 100
        self.goal = Goal(goal_x, goal_y)

    def _pattern_easy_platforms(self, base_height):
        # Simple platforms for beginner levels
        self.platforms.append(Platform(200, base_height - 100, 100, 20, self._get_world_color()))
        self.platforms.append(Platform(400, base_height - 150, 100, 20, self._get_world_color()))
        self.platforms.append(Platform(600, base_height - 100, 100, 20, self._get_world_color()))

    def _pattern_stairs(self, base_height):
        # Staircase pattern
        for i in range(4):
            self.platforms.append(Platform(200 + i * 150, base_height - 80 - (i * 60), 100, 20, self._get_world_color()))

    def _pattern_gaps(self, base_height):
        # Platforms with gaps
        self.platforms.append(Platform(150, base_height - 120, 80, 20, self._get_world_color()))
        self.platforms.append(Platform(300, base_height - 180, 80, 20, self._get_world_color()))
        self.platforms.append(Platform(450, base_height - 120, 80, 20, self._get_world_color()))
        self.platforms.append(Platform(600, base_height - 180, 80, 20, self._get_world_color()))

    def _pattern_high_platforms(self, base_height):
        # High platforms requiring precise jumps
        self.platforms.append(Platform(100, base_height - 200, 60, 20, self._get_world_color()))
        self.platforms.append(Platform(250, base_height - 250, 60, 20, self._get_world_color()))
        self.platforms.append(Platform(400, base_height - 300, 60, 20, self._get_world_color()))
        self.platforms.append(Platform(550, base_height - 250, 60, 20, self._get_world_color()))
        self.platforms.append(Platform(700, base_height - 200, 60, 20, self._get_world_color()))

    def _pattern_final_challenge(self, base_height):
        # Most challenging pattern for final level in each world
        self.platforms.append(Platform(150, base_height - 150, 50, 20, self._get_world_color()))
        self.platforms.append(Platform(300, base_height - 220, 50, 20, self._get_world_color()))
        self.platforms.append(Platform(450, base_height - 290, 50, 20, self._get_world_color()))
        self.platforms.append(Platform(600, base_height - 220, 50, 20, self._get_world_color()))
        self.platforms.append(Platform(750, base_height - 150, 50, 20, self._get_world_color()))

    def _get_world_color(self):
        # Different platform colors for different worlds
        world_colors = {
            1: GREEN,
            2: BLUE,
            3: ORANGE,
            4: CYAN,
            5: GRAY,
            6: PURPLE,
            7: RED,
            8: DARK_GREEN,
            9: PINK
        }
        return world_colors.get(self.world_num, GREEN)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Forever - 9 Worlds, 5 Levels Each")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.current_world = 1
        self.current_level = 1
        self.total_worlds = 9
        self.levels_per_world = 5
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        
        self.load_level()

    def load_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        
        # Create current level
        self.current_level_obj = Level(self.current_world, self.current_level)
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Add platforms
        for platform in self.current_level_obj.platforms:
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        
        # Add goal
        if self.current_level_obj.goal:
            self.all_sprites.add(self.current_level_obj.goal)
            self.goals.add(self.current_level_obj.goal)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                # Debug keys for testing
                if event.key == pygame.K_n:
                    self.next_level()
                if event.key == pygame.K_p:
                    self.previous_level()
        
        # Continuous key press handling
        keys = pygame.key.get_pressed()
        self.player.acc_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.acc_x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.acc_x = PLAYER_ACC
            
        return True

    def update(self):
        # Update all sprites
        self.all_sprites.update()
        
        # Check for collisions between player and platforms
        self.player.on_ground = False
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        for hit in hits:
            # Vertical collisions
            if self.player.vel_y > 0:  # Falling down
                self.player.rect.bottom = hit.rect.top
                self.player.vel_y = 0
                self.player.on_ground = True
            elif self.player.vel_y < 0:  # Moving up
                self.player.rect.top = hit.rect.bottom
                self.player.vel_y = 0

        # Check for goal collision
        goal_hits = pygame.sprite.spritecollide(self.player, self.goals, False)
        if goal_hits:
            self.next_level()

    def next_level(self):
        self.current_level += 1
        if self.current_level > self.levels_per_world:
            self.current_level = 1
            self.current_world += 1
            if self.current_world > self.total_worlds:
                self.current_world = 1  # Loop back to world 1 after completing all worlds
        self.load_level()

    def previous_level(self):
        self.current_level -= 1
        if self.current_level < 1:
            self.current_level = self.levels_per_world
            self.current_world -= 1
            if self.current_world < 1:
                self.current_world = self.total_worlds
        self.load_level()

    def draw(self):
        # Draw background with level theme
        self.screen.fill(self.current_level_obj.background_color)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw UI
        world_text = self.font.render(f"World {self.current_world}-{self.current_level}", True, WHITE)
        self.screen.blit(world_text, (10, 10))
        
        progress_text = self.font.render(f"Progress: {self.current_world}-{self.current_level}/{self.total_worlds}-{self.levels_per_world}", True, WHITE)
        self.screen.blit(progress_text, (10, 50))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
