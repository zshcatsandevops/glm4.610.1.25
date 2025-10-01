import pygame
import sys
import os
import json

# Initialize Pygame
pygame.init()

# Constants optimized for 60 FPS Famicom-style gameplay
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5  # SMB-style gravity
PLAYER_ACC = 0.6  # SMB-style acceleration
PLAYER_FRICTION = -0.12  # SMB-style friction
JUMP_STRENGTH = -12  # SMB-style jump
MAX_VEL_X = 6  # SMB-style max speed
MAX_VEL_Y = 12  # Terminal velocity

# Colors - NES palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
DARK_RED = (136, 0, 0)
GREEN = (0, 168, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 104, 216)
DARK_BLUE = (0, 0, 168)
BROWN = (152, 104, 56)
YELLOW = (232, 216, 0)
ORANGE = (248, 136, 0)
PURPLE = (104, 0, 168)
CYAN = (0, 216, 216)
GRAY = (120, 120, 120)
PINK = (248, 120, 88)

class AssetLoader:
    def __init__(self):
        self.assets_loaded = False
        self.engine_data = {}
        self.sprites = {}
        self.levels = {}
        self.config = {}
        
    def load_engine_files(self, engine_path="smb1_engine"):
        """Load SMB1 engine files from external directory"""
        try:
            # Load configuration file
            config_path = os.path.join(engine_path, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            # Load physics settings
            physics_path = os.path.join(engine_path, "physics.json")
            if os.path.exists(physics_path):
                with open(physics_path, 'r') as f:
                    physics = json.load(f)
                    # Apply physics settings
                    global GRAVITY, PLAYER_ACC, PLAYER_FRICTION, JUMP_STRENGTH, MAX_VEL_X, MAX_VEL_Y
                    GRAVITY = physics.get("gravity", GRAVITY)
                    PLAYER_ACC = physics.get("player_acc", PLAYER_ACC)
                    PLAYER_FRICTION = physics.get("player_friction", PLAYER_FRICTION)
                    JUMP_STRENGTH = physics.get("jump_strength", JUMP_STRENGTH)
                    MAX_VEL_X = physics.get("max_vel_x", MAX_VEL_X)
                    MAX_VEL_Y = physics.get("max_vel_y", MAX_VEL_Y)
            
            # Load level data
            levels_path = os.path.join(engine_path, "levels.json")
            if os.path.exists(levels_path):
                with open(levels_path, 'r') as f:
                    self.levels = json.load(f)
            
            # Load sprite data
            sprites_path = os.path.join(engine_path, "sprites.json")
            if os.path.exists(sprites_path):
                with open(sprites_path, 'r') as f:
                    sprite_data = json.load(f)
                    self.load_sprites(engine_path, sprite_data)
            
            self.assets_loaded = True
            return True
        except Exception as e:
            print(f"Error loading engine files: {e}")
            return False
    
    def load_sprites(self, engine_path, sprite_data):
        """Load sprite images and data"""
        for sprite_name, sprite_info in sprite_data.items():
            sprite_path = os.path.join(engine_path, sprite_info.get("file", ""))
            if os.path.exists(sprite_path):
                try:
                    sprite_image = pygame.image.load(sprite_path).convert_alpha()
                    self.sprites[sprite_name] = {
                        "image": sprite_image,
                        "frames": sprite_info.get("frames", 1),
                        "width": sprite_info.get("width", sprite_image.get_width()),
                        "height": sprite_info.get("height", sprite_image.get_height())
                    }
                except Exception as e:
                    print(f"Error loading sprite {sprite_name}: {e}")
    
    def get_level_data(self, world, level):
        """Get level data from loaded files"""
        level_key = f"{world}-{level}"
        return self.levels.get(level_key, {})
    
    def get_sprite(self, sprite_name):
        """Get sprite data"""
        return self.sprites.get(sprite_name, None)

class Player(pygame.sprite.Sprite):
    def __init__(self, asset_loader):
        super().__init__()
        self.asset_loader = asset_loader
        self.size = 32  # SMB-style character size
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.acc_x = 0
        self.facing_right = True
        self.jump_count = 0
        self.max_jumps = 1  # SMB-style single jump
        self.animation_frame = 0
        self.animation_timer = 0
        self.state = "idle"  # idle, running, jumping
        self.create_mario_sprite()
        
    def create_mario_sprite(self):
        """Create Mario sprite from engine files or fallback to pixel art"""
        mario_sprite = self.asset_loader.get_sprite("mario")
        
        if mario_sprite:
            # Use sprite from engine files
            self.sprite_image = mario_sprite["image"]
            self.sprite_frames = mario_sprite["frames"]
            self.sprite_width = mario_sprite["width"]
            self.sprite_height = mario_sprite["height"]
            self.update_sprite_frame()
        else:
            # Fallback to pixel art
            self.sprite_image = None
            self.draw_pixel_mario()
    
    def draw_pixel_mario(self):
        """Draw pixel art Mario as fallback"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparent color
        # Hat
        pygame.draw.rect(self.image, RED, (4, 2, 24, 8))
        # Face
        pygame.draw.rect(self.image, (255, 184, 120), (8, 10, 16, 8))
        # Eyes
        pygame.draw.rect(self.image, BLACK, (10, 12, 4, 4))
        pygame.draw.rect(self.image, BLACK, (18, 12, 4, 4))
        # Mustache
        pygame.draw.rect(self.image, BLACK, (8, 16, 16, 2))
        # Shirt
        pygame.draw.rect(self.image, RED, (8, 18, 16, 10))
        # Overalls
        pygame.draw.rect(self.image, BLUE, (8, 24, 16, 8))
        # Arms
        pygame.draw.rect(self.image, RED, (4, 20, 4, 8))
        pygame.draw.rect(self.image, RED, (24, 20, 4, 8))
        # Legs
        pygame.draw.rect(self.image, BLUE, (10, 28, 4, 4))
        pygame.draw.rect(self.image, BLUE, (18, 28, 4, 4))
    
    def update_sprite_frame(self):
        """Update sprite animation frame"""
        if self.sprite_image:
            frame_x = (self.animation_frame % self.sprite_frames) * self.sprite_width
            frame_rect = pygame.Rect(frame_x, 0, self.sprite_width, self.sprite_height)
            self.image = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            self.image.blit(self.sprite_image, (0, 0), frame_rect)
            self.rect = self.image.get_rect()
            
            # Flip sprite if facing left
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
    
    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_VEL_Y:  # Terminal velocity
            self.vel_y = MAX_VEL_Y
        
        # Handle horizontal movement with friction
        self.vel_x += self.acc_x
        self.vel_x *= (1 + PLAYER_FRICTION)
        
        # Clamp velocity
        self.vel_x = max(-MAX_VEL_X, min(MAX_VEL_X, self.vel_x))
        
        # Update position
        self.rect.x += self.vel_x
        self.collide_with_platforms(platforms, 'horizontal')
        
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_with_platforms(platforms, 'vertical')
        
        # Update animation
        self.update_animation()
        
        # Update sprite direction
        if self.vel_x > 0 and not self.facing_right:
            self.facing_right = True
            self.update_sprite_frame()
        elif self.vel_x < 0 and self.facing_right:
            self.facing_right = False
            self.update_sprite_frame()
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = max(0, self.vel_x)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x = min(0, self.vel_x)
            
        # Respawn if fell off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

    def update_animation(self):
        """Update animation based on player state"""
        # Update animation timer
        self.animation_timer += 1
        if self.animation_timer >= 10:  # Change frame every 10 ticks
            self.animation_timer = 0
            self.animation_frame += 1
            
            # Update state
            if not self.on_ground:
                self.state = "jumping"
            elif abs(self.vel_x) > 0.5:
                self.state = "running"
            else:
                self.state = "idle"
            
            # Update sprite frame
            if self.sprite_image:
                self.update_sprite_frame()
            else:
                self.draw_pixel_mario()

    def flip_sprite(self):
        # Flip the sprite horizontally
        if self.sprite_image:
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.transform.flip(self.image, True, False)

    def collide_with_platforms(self, platforms, direction):
        if direction == 'horizontal':
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                    self.vel_x = 0
                    
        elif direction == 'vertical':
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.vel_y = 0
                        self.jump_count = 0  # Reset jump count when landing
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0

    def respawn(self):
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.vel_x = 0
        self.vel_y = 0
        self.jump_count = 0

    def jump(self):
        if self.on_ground and self.jump_count < self.max_jumps:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jump_count += 1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREEN, platform_type="normal", asset_loader=None):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.platform_type = platform_type
        self.asset_loader = asset_loader
        self.create_platform(color)
        
    def create_platform(self, color):
        # Try to load platform sprite from engine files
        if self.asset_loader:
            platform_sprite = self.asset_loader.get_sprite(f"platform_{self.platform_type}")
            if platform_sprite:
                # Use sprite from engine files
                sprite_image = platform_sprite["image"]
                # Tile the sprite across the platform
                for x in range(0, self.rect.width, platform_sprite["width"]):
                    for y in range(0, self.rect.height, platform_sprite["height"]):
                        self.image.blit(sprite_image, (x, y))
                return
        
        # Fallback to generated platform
        if self.platform_type == "ground":
            # Create SMB-style ground with bricks
            brick_width = 32
            brick_height = 16
            for y in range(0, self.rect.height, brick_height):
                for x in range(0, self.rect.width, brick_width):
                    # Draw brick
                    pygame.draw.rect(self.image, BROWN, (x, y, brick_width, brick_height))
                    # Draw brick border
                    pygame.draw.rect(self.image, BLACK, (x, y, brick_width, brick_height), 1)
                    # Draw brick detail
                    pygame.draw.line(self.image, BLACK, (x, y + brick_height//2), 
                                    (x + brick_width, y + brick_height//2), 1)
        else:
            # Regular platform
            self.image.fill(color)
            # Add border for NES-style look
            pygame.draw.rect(self.image, BLACK, (0, 0, self.rect.width, self.rect.height), 1)

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_loader=None):
        super().__init__()
        self.size = 32
        self.image = pygame.Surface((self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.asset_loader = asset_loader
        self.create_flag_sprite()
        
    def create_flag_sprite(self):
        # Try to load flag sprite from engine files
        if self.asset_loader:
            flag_sprite = self.asset_loader.get_sprite("flag")
            if flag_sprite:
                # Use sprite from engine files
                self.image = flag_sprite["image"]
                return
        
        # Fallback to generated flag
        self.image.fill(BLACK)  # Clear with transparent color
        # Pole
        pygame.draw.rect(self.image, GRAY, (14, 0, 4, 32))
        # Flag
        pygame.draw.rect(self.image, GREEN, (18, 2, 10, 8))
        # Set transparent color
        self.image.set_colorkey(BLACK)

class Level:
    def __init__(self, world_num, level_num, asset_loader=None):
        self.world_num = world_num
        self.level_num = level_num
        self.platforms = []
        self.goal = None
        self.background_color = (135, 206, 235)
        self.asset_loader = asset_loader
        
        self.set_theme()
        self.generate_level()

    def set_theme(self):
        # Try to load theme from engine files
        if self.asset_loader and self.asset_loader.assets_loaded:
            level_data = self.asset_loader.get_level_data(self.world_num, self.level_num)
            if "background_color" in level_data:
                self.background_color = tuple(level_data["background_color"])
                return
        
        # Fallback to default themes
        theme_colors = {
            1: (92, 148, 252),  # Sky Blue
            2: (0, 0, 168),      # Night Blue
            3: (0, 168, 0),      # Green
            4: (168, 0, 0),      # Red
            5: (168, 168, 0),    # Yellow
            6: (168, 0, 168),    # Purple
            7: (0, 168, 168),    # Cyan
            8: (168, 84, 0),     # Brown
            9: (0, 84, 168)      # Dark Blue
        }
        self.background_color = theme_colors.get(self.world_num, (92, 148, 252))

    def generate_level(self):
        # Try to load level from engine files
        if self.asset_loader and self.asset_loader.assets_loaded:
            level_data = self.asset_loader.get_level_data(self.world_num, self.level_num)
            if "platforms" in level_data:
                for platform_data in level_data["platforms"]:
                    x = platform_data.get("x", 0)
                    y = platform_data.get("y", 0)
                    width = platform_data.get("width", 100)
                    height = platform_data.get("height", 20)
                    color = tuple(platform_data.get("color", GREEN))
                    platform_type = platform_data.get("type", "normal")
                    self.platforms.append(Platform(x, y, width, height, color, platform_type, self.asset_loader))
                
                if "goal" in level_data:
                    goal_data = level_data["goal"]
                    x = goal_data.get("x", SCREEN_WIDTH - 50)
                    y = goal_data.get("y", SCREEN_HEIGHT - 100)
                    self.goal = Goal(x, y, self.asset_loader)
                return
        
        # Fallback to generated level
        # Ground platform with SMB-style bricks
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, BROWN, "ground", self.asset_loader))
        
        base_height = SCREEN_HEIGHT - 40
        
        # Level patterns
        level_patterns = [
            self._pattern_easy_platforms,
            self._pattern_stairs,
            self._pattern_gaps,
            self._pattern_high_platforms,
            self._pattern_final_challenge
        ]
        
        pattern_func = level_patterns[(self.level_num - 1) % len(level_patterns)]
        pattern_func(base_height)
        
        # Place goal on last platform
        if self.platforms:
            last_platform = self.platforms[-1]
            goal_x = last_platform.rect.x + (last_platform.rect.width - 32) // 2
            goal_y = last_platform.rect.y - 40
            self.goal = Goal(goal_x, goal_y, self.asset_loader)

    def _pattern_easy_platforms(self, base_height):
        self.platforms.append(Platform(150, base_height - 100, 120, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(350, base_height - 150, 120, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(550, base_height - 100, 120, 20, self._get_world_color(), "normal", self.asset_loader))

    def _pattern_stairs(self, base_height):
        for i in range(5):
            self.platforms.append(Platform(150 + i * 130, base_height - 60 - (i * 50), 100, 20, self._get_world_color(), "normal", self.asset_loader))

    def _pattern_gaps(self, base_height):
        self.platforms.append(Platform(100, base_height - 120, 100, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(250, base_height - 180, 100, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(400, base_height - 120, 100, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(550, base_height - 180, 100, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(700, base_height - 120, 100, 20, self._get_world_color(), "normal", self.asset_loader))

    def _pattern_high_platforms(self, base_height):
        self.platforms.append(Platform(80, base_height - 200, 70, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(200, base_height - 250, 70, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(320, base_height - 300, 70, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(440, base_height - 250, 70, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(560, base_height - 200, 70, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(680, base_height - 150, 70, 20, self._get_world_color(), "normal", self.asset_loader))

    def _pattern_final_challenge(self, base_height):
        self.platforms.append(Platform(120, base_height - 150, 60, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(240, base_height - 220, 60, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(360, base_height - 290, 60, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(480, base_height - 220, 60, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(600, base_height - 150, 60, 20, self._get_world_color(), "normal", self.asset_loader))
        self.platforms.append(Platform(720, base_height - 80, 60, 20, self._get_world_color(), "normal", self.asset_loader))

    def _get_world_color(self):
        # Try to get world color from engine files
        if self.asset_loader and self.asset_loader.assets_loaded:
            level_data = self.asset_loader.get_level_data(self.world_num, self.level_num)
            if "platform_color" in level_data:
                return tuple(level_data["platform_color"])
        
        # Fallback to default colors
        world_colors = {
            1: GREEN, 2: DARK_GREEN, 3: ORANGE, 4: RED, 5: YELLOW,
            6: PURPLE, 7: CYAN, 8: BROWN, 9: DARK_BLUE
        }
        return world_colors.get(self.world_num, GREEN)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros - NES Style")
        self.clock = pygame.time.Clock()
        
        # Initialize asset loader
        self.asset_loader = AssetLoader()
        self.engine_loaded = self.asset_loader.load_engine_files("smb1_engine")
        
        # Game state
        self.current_world = 1
        self.current_level = 1
        self.total_worlds = 9
        self.levels_per_world = 5
        
        # Font for UI - use a pixel-style font if available
        try:
            self.font = pygame.font.Font("PressStart2P.ttf", 24)
            self.small_font = pygame.font.Font("PressStart2P.ttf", 16)
        except:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        # Level transition
        self.level_transition_timer = 0
        self.level_transition_delay = 60
        
        # Performance tracking
        self.frame_count = 0
        self.fps_text = "60"
        self.last_fps_update = pygame.time.get_ticks()
        
        self.load_level()

    def load_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        
        # Create level
        self.current_level_obj = Level(self.current_world, self.current_level, self.asset_loader)
        
        # Create player
        self.player = Player(self.asset_loader)
        self.all_sprites.add(self.player)
        
        # Add platforms and goal
        for platform in self.current_level_obj.platforms:
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        
        if self.current_level_obj.goal:
            self.all_sprites.add(self.current_level_obj.goal)
            self.goals.add(self.current_level_obj.goal)
            
        self.level_transition_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.jump()
                # Debug keys
                if event.key == pygame.K_n:
                    self.next_level()
                if event.key == pygame.K_p:
                    self.previous_level()
                if event.key == pygame.K_r:
                    self.load_level()  # Quick restart
        
        # Movement keys
        keys = pygame.key.get_pressed()
        self.player.acc_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.acc_x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.acc_x = PLAYER_ACC
            
        return True

    def update(self):
        # Update FPS counter
        self.frame_count += 1
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_update > 500:  # Update FPS every 500ms
            self.fps_text = str(int(self.clock.get_fps()))
            self.last_fps_update = current_time
        
        # Update player with platforms for collision detection
        self.player.update(self.current_level_obj.platforms)
        
        # Check for goal collision
        goal_hits = pygame.sprite.spritecollide(self.player, self.goals, False)
        if goal_hits and self.level_transition_timer == 0:
            self.level_transition_timer = self.level_transition_delay
            
        # Handle level transition
        if self.level_transition_timer > 0:
            self.level_transition_timer -= 1
            if self.level_transition_timer == 0:
                self.next_level()

    def next_level(self):
        self.current_level += 1
        if self.current_level > self.levels_per_world:
            self.current_level = 1
            self.current_world += 1
            if self.current_world > self.total_worlds:
                self.current_world = 1
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
        # Draw background
        self.screen.fill(self.current_level_obj.background_color)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # UI
        world_text = self.font.render(f"WORLD {self.current_world}-{self.current_level}", True, WHITE)
        self.screen.blit(world_text, (10, 10))
        
        total_levels = self.total_worlds * self.levels_per_world
        current_level_global = (self.current_world - 1) * self.levels_per_world + self.current_level
        progress_text = self.small_font.render(f"PROGRESS: {current_level_global}/{total_levels}", True, WHITE)
        self.screen.blit(progress_text, (10, 50))
        
        # FPS counter
        fps_display = self.small_font.render(f"FPS: {self.fps_text}", True, WHITE)
        self.screen.blit(fps_display, (SCREEN_WIDTH - 100, 10))
        
        # Engine status
        engine_status = "LOADED" if self.engine_loaded else "NOT FOUND"
        engine_text = self.small_font.render(f"ENGINE: {engine_status}", True, WHITE)
        self.screen.blit(engine_text, (SCREEN_WIDTH - 150, 40))
        
        # Controls hint
        controls_text = self.small_font.render("ARROW/WASD: MOVE | SPACE/W: JUMP", True, WHITE)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30))
        
        # Level complete message
        if self.level_transition_timer > 0:
            level_complete_text = self.font.render("LEVEL COMPLETE!", True, WHITE)
            text_rect = level_complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(level_complete_text, text_rect)
        
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
