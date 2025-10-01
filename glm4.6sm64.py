# Filename: sm64_ursina_demo.py

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import atan2

# --- Application Setup ---
app = Ursina(size=(600, 400), title='Peach\'s Castle - SM64 Physics & Camera Demo')

# --- Global Settings ---
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# --- Physics and Camera Constants ---
GRAVITY = -0.5
WALK_SPEED = 8
JUMP_HEIGHT = 10
CAMERA_DISTANCE = 12
CAMERA_HEIGHT = 6
CAMERA_SMOOTHING_SPEED = 6.0
PLAYER_TURN_SPEED = 8.0

# --- Scene Creation ---
# Ground
ground = Entity(
    model='cube',
    color=color.lime,
    scale=(100, 1, 100),
    texture='white_cube',
    collider='box',
    texture_scale=(100, 100)
)

# A simple representation of Peach's Castle
castle_base = Entity(
    model='cube',
    color=color.red.tint(-0.2),
    scale=(20, 15, 30),
    position=(0, 7.5, -20),
    collider='box'
)
castle_roof = Entity(
    model='cube',
    color=color.red,
    scale=(22, 1, 32),
    position=(0, 15.5, -20),
    collider='box'
)
# Towers to test camera collision
tower_left = Entity(
    model='cube',
    color=color.orange,
    scale=(5, 20, 5),
    position=(-12, 10, -25),
    collider='box'
)
tower_right = Entity(
    model='cube',
    color=color.orange,
    scale=(5, 20, 5),
    position=(12, 10, -25),
    collider='box'
)

# Sky
Sky()

# --- Player Class with SM64-style Physics ---
class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', # Using a simple capsule model would be better
            color=color.azure,
            origin_y=-.5,
            scale=(1, 2, 1),
            collider='box',
            **kwargs
        )
        self.velocity = Vec3(0,0,0)
        self.camera_pivot = Entity(parent=self, y=1) # Point for camera to look at

    def update(self):
        # --- Input and Movement ---
        direction = Vec3(
            self.camera_pivot.right * (held_keys['d'] - held_keys['a']) +
            self.camera_pivot.forward * (held_keys['w'] - held_keys['s'])
        ).normalized()

        # Apply horizontal movement with momentum
        self.velocity.x = direction.x * WALK_SPEED
        self.velocity.z = direction.z * WALK_SPEED

        # --- Physics ---
        # Apply gravity
        self.velocity.y += GRAVITY * time.dt

        # Ground check using raycast
        hit_info = raycast(self.world_position + Vec3(0,0.5,0), Vec3(0, -1, 0), distance=1, ignore=[self])
        if hit_info.hit:
            if self.velocity.y < 0:
                self.velocity.y = 0
            self.y = hit_info.point.y # Snap to ground
            if held_keys['space']:
                self.velocity.y = JUMP_HEIGHT
        
        # Apply velocity to position
        self.position += self.velocity * time.dt

        # --- Player Model Rotation ---
        # Smoothly rotate the player model to face the movement direction
        if direction.length() > 0:
            self.rotation_y = lerp(self.rotation_y, atan2(direction.x, direction.z), PLAYER_TURN_SPEED * time.dt)

# --- Lakitu Camera Controller ---
class LakituCamera(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # This pivot will orbit around the player
        self.pivot = Entity()
        self.player = None # Will be set later

    def update(self):
        if not self.player:
            return

        # --- User Camera Control ---
        # Rotate the pivot around the player
        self.pivot.rotation_y += (held_keys['e'] - held_keys['q']) * 60 * time.dt
        
        # --- Camera Position Calculation ---
        # 1. Make the pivot follow the player
        self.pivot.position = self.player.position

        # 2. Define the IDEAL camera position (where it wants to be)
        ideal_camera_pos = self.pivot.world_position + (self.pivot.back * CAMERA_DISTANCE) + Vec3(0, CAMERA_HEIGHT, 0)

        # 3. Collision Avoidance using Raycast
        # Cast a ray from a point above the player towards the ideal camera position
        ray_start = self.player.position + Vec3(0, 2, 0)
        ray_direction = (ideal_camera_pos - ray_start).normalized()
        hit_info = raycast(ray_start, ray_direction, distance=CAMERA_DISTANCE, ignore=[self.player, self.pivot])
        
        # If the ray hits something, move the camera to the hit point. Otherwise, use the ideal position.
        target_camera_pos = hit_info.point if hit_info.hit else ideal_camera_pos
        
        # 4. Smoothly move the camera to the target position
        camera.position = lerp(camera.position, target_camera_pos, CAMERA_SMOOTHING_SPEED * time.dt)
        
        # 5. Make the camera look at the player
        camera.look_at(self.player.camera_pivot.world_position)


# --- Instantiate Player and Camera ---
player = Player(position=(0, 5, 10))
lakitu_camera = LakituCamera()
lakitu_camera.player = player # Link the camera to the player

# --- Instructions ---
Text(
    text='''
WASD: Move
SPACE: Jump
Q/E: Rotate Camera
    ''',
    position=window.top_left,
    scale=0.8,
    background=color.black66
)

# --- Run the Application ---
app.run()
