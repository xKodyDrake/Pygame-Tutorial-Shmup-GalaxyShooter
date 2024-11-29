# Shmup
# Frozen Jam by Copyright 2008 Elle Trudgett | https://github.com/elle-trudgett - Licensed under CC BY 3.0 https://creativecommons.org/licenses/by/3.0/ | edited by qubodup
# Art from Kenney.nl
import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

from pygame.sprite import Group

# Window of game, game speed
WIDTH = 800
HEIGHT = 600
FPS = 90
POWERUP_TIME = 5000

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize pygame, sounds, clock and create window
pygame.init()
pygame.mixer. init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooter Game")
clock = pygame.time.Clock()

# Pygame searches computer for closest thinng to 'arial' font
font_name = pygame.font.match_font('arial bold')

# Draw score to screen
def draw_text(surf, text, size, x, y):

    # Create font object using name and size
    font = pygame.font.Font(font_name, size)

    # Create surface to render pixels on to (True = anti-aliasing (less jagged pixels))
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Define function to spawn new mob
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Define draw shield bar using a percentage 
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 212
    BAR_HEIGHT = 12
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

"""
    SPRITES
"""

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
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 4      # Displays 3, the ships is the 4th
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()


    def update(self):

        # timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # Unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        # Allows ship to stop after key release
        self.speedx = 0

        # Events for keypress
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx

        # Make walls of screen
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
            
            self.power += 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):

        now = pygame.time.get_ticks()

        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
    

    def hide(self):

        # Hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

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

# Class for powerup
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'bolt'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy

    # Kill bullet if leave screen
        if self.rect.top > HEIGHT:
            self.kill()

# Class for explosions
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def show_go_screen():

    # Copy pixel of background to screen
    screen.blit(background, background_rect)

    draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

"""
    LOAD ALL GRAPHICS
"""
# Load all game graphics
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_green.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
# meteor_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png")).convert()  # Original meteor image (used only one image)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []  # List to store meteor images to randomly pick from
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png',
               'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png',]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

# Explosion animation images
# Go through list, load explosion image in, scale it to size, append to large or small list
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []

for i in range(9):                                                      # loop through the 8 images
    filename = 'regularExplosion0{}.png'.format(i)                      # filename updates to correct file
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir,'shield_gold.png')).convert()
powerup_images['bolt'] = pygame.image.load(path.join(img_dir,'bolt_gold.png')).convert()

# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'Laser.wav'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'Shield.wav'))
bolt_sound = pygame.mixer.Sound(path.join(snd_dir, 'Pow_laser.wav'))
expl_sounds = []
for snd in ['Expl1.wav', 'Expl2.wav', 'Expl3.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'Death_expl.wav'))

"""
    LOAD ALL SOUNDS
"""

# Background music
pygame.mixer.music.load(path.join(snd_dir, 'frozenjam-seamlessloop.ogg'))
pygame.mixer.music.set_volume(0.3)


"""
    RUN GAME LOOP
"""

# Initialize score, set 0
score = 0

# Start music (loop everytime song ends)
pygame.mixer.music.play(loops = -1)

# Game loop
game_over = True
running = True

while running:
    if game_over:

        show_go_screen()
        game_over = False

        # Sprites, add player to sprite group
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)

        for i in range(8):
            newmob()


    # Set game speed
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():

        # Check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # Check if bullet hit mob, respawns on hit
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius     # Get more points for smaller meteors (radius = 8 == 42 pts)
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # Check if mob hit player (player, group hit, False doesnt delete hit enemy, collide_circle changes hitbox type from the rectangle base setting to circles)
    # From Axis-aligned Bounding Box (AABB - Rectangle - Default) ---> Circular Bounding Box (CBB - Circle - declared in spritecollide)
    # Changed to true so hitting with shield continues game
    # If hits anything, close program
    # Changed to for hit in hits: to list every hit and take away shield until hp = 0 then close
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
            # player.kill()       # Deletes player sprite on death
            # running = False

    # If hit powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:

        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            shield_sound.play()
            if player.shield >= 100:
                player.shield = 100
        
        if hit.type == 'bolt':
            player.powerup()
            bolt_sound.play()

    # If player died and explosion is finished
    if player.lives == 0 and not death_explosion.alive():
        game_over = True
        

    # Draw / render
    screen.fill(BLACK)

    # Copy pixel of background to screen
    screen.blit(background, background_rect)

    all_sprites.draw(screen)

    # Location, what to print, font size, x, y
    draw_text(screen, str(score), 18, WIDTH / 2, 10)

    # Draw shield bar in top left displaying player shield
    draw_shield_bar(screen, 5, 5, player.shield)

    # Draw lives
    draw_lives(screen, WIDTH - 100, 5, player.lives - 1, player_mini_img)

    # After drawing, flips screen
    pygame.display.flip()

pygame.quit()