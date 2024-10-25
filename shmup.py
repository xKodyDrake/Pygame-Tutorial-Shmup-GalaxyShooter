# Shmup
import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')

from pygame.sprite import Group

# Window of game, game speed
WIDTH = 800
HEIGHT = 600
FPS = 60

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize pygame and create window
pygame.init()
pygame.mixer. init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooter Game")
clock = pygame.time.Clock()

# Create player character
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))   # Scales player model
        self.image.set_colorkey(BLACK)                              # Removes black box around graphic
        self.rect = self.image.get_rect()
        self.radius = 19
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # Draws red circle to test radius / hitbox
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):

        # Allows ship to stop after key release
        self.speedx = 0

        # Events for keypress
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx

        # Make walls of screen
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet= Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Class for mob (image_orig is used to rotate without losing pixels / data)
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # Draws red circle to test radius / hitbox
        
        # Random mob spawn
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -150)

        # Random speed
        self.speedy = random.randrange(3, 7)
        self.speedx = random.randrange(-3, 3)

        # Set rotation of mob, use clock / game ticks to decide when to turn again
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360    # Use modulus to loop back to 1 after reaching 360 degrees of rotation (360 % 360 = 0, 361 % 360 = 1, etc.)
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Randomize mob spawn when goes off bottom of screen or side
        if self.rect.top > HEIGHT + 10 or self.rect.left < -30 or self.rect.right > WIDTH + 30:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 7)
            self.speedx = random.randrange(-3, 3)

# Class for bullet to fire at enemy
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

    # Kill bullet if leave screen
        if self.rect.bottom < 0:
            self.kill()

# Load all game graphics
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_green.png")).convert()
# meteor_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png")).convert()  # Original meteor image (used only one image)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []  # List to store meteor images to randomly pick from
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png',
               'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png',]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())



# Sprites, add player to sprite group
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Initialize score and set to 0
score = 0

# Game loop
running = True
while running:

    # Set game speed
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():

        # Check for closing window
        if event.type == pygame.QUIT:
            running = False

        # If spacebar pressed, shoot
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()


    # Update
    all_sprites.update()

    # Check if bullet hit mob, respawns on hit
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # Check if mob hit player (player, group hit, False doesnt delete hit enemy, collide_circle changes hitbox type from the rectangle base setting to circles)
    # From Axis-aligned Bounding Box (AABB - Rectangle - Default) ---> Circular Bounding Box (CBB - Circle - declared in spritecollide)
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)

    # If hits anything, close program
    if hits:
        running = False

    # Draw / render
    screen.fill(BLACK)

    # Copy pixel of background to screen
    screen.blit(background, background_rect)

    all_sprites.draw(screen)

    # After drawing, flips screen
    pygame.display.flip()

pygame.quit()