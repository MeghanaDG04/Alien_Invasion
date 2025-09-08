#py game
import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Game settings
screen_width = 800
screen_height = 600
bg_color = (0, 0, 0)  # Black background

# Screen setup
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Alien Invasion")

# Colors
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

# Load sounds
pygame.mixer.init()
# Removed shoot_sound
#explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
#  powerup_sound = pygame.mixer.Sound('sounds/powerup.wav')

# Create sounds directory if it doesn't exist
import os

if not os.path.exists('sounds'):
    os.makedirs('sounds')

# Create placeholder sound files if they don't exist
# Removed shoot.wav from the list
for sound_file in ['explosion.wav', 'powerup.wav']:
    if not os.path.exists(f'sounds/{sound_file}'):
        with open(f'sounds/{sound_file}', 'wb') as f:
            f.write(b'')


# Ship class
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, green, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 50)
        self.speed = 5
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.bullet_power = 1
        self.power_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed

        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Handle power-up timer
        if self.bullet_power > 1:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.bullet_power = 1

    def make_invincible(self, duration=180):  # 3 seconds at 60 FPS
        self.invincible = True
        self.invincible_timer = duration

    def power_up(self, duration=300):  # 5 seconds at 60 FPS
        self.bullet_power = 2
        self.power_timer = duration


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, power=1):
        super().__init__()
        self.power = power
        if power == 1:
            self.image = pygame.Surface((5, 10))
            self.image.fill(white)
        else:
            self.image = pygame.Surface((8, 15))
            self.image.fill(yellow)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


# Alien class
class Alien(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.level = level
        self.health = level
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)

        if level == 1:
            color = red
        elif level == 2:
            color = (255, 165, 0)  # Orange
        else:
            color = (128, 0, 128)  # Purple

        pygame.draw.rect(self.image, color, [0, 0, 40, 40])
        pygame.draw.rect(self.image, white, [5, 5, 30, 30], 2)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - 40)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 2) + (level - 1)

        # Chance to shoot
        self.shoot_chance = 0.005 * level

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.rect.x = random.randint(0, screen_width - 40)
            self.rect.y = random.randint(-100, -40)
            return True  # Alien escaped

        # Random chance to shoot
        if random.random() < self.shoot_chance:
            return "shoot"
        return False


# Alien Bullet class
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()


# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type  # 'health', 'shield', 'power'
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)

        if type == 'health':
            color = green
            pygame.draw.rect(self.image, color, [0, 0, 25, 25])
            pygame.draw.line(self.image, white, (12, 5), (12, 20), 3)
            pygame.draw.line(self.image, white, (5, 12), (20, 12), 3)
        elif type == 'shield':
            color = blue
            pygame.draw.rect(self.image, color, [0, 0, 25, 25])
            pygame.draw.circle(self.image, white, (12, 12), 8, 2)
        elif type == 'power':
            color = yellow
            pygame.draw.rect(self.image, color, [0, 0, 25, 25])
            pygame.draw.polygon(self.image, white, [(12, 5), (5, 20), (20, 20)], 2)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()


# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for size in range(5, 30, 5):
            img = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(img, yellow, (size, size), size)
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 4:  # Speed of animation
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]


# Group to manage all sprites
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
alien_bullets = pygame.sprite.Group()
aliens = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Create ship
ship = Ship()
all_sprites.add(ship)

# Create aliens
for i in range(10):
    alien = Alien(random.randint(1, 2))
    all_sprites.add(alien)
    aliens.add(alien)

# Game variables
clock = pygame.time.Clock()
score = 0
level = 1
game_over = False
game_paused = False
alien_spawn_timer = 0
wave_cleared = False
wave_timer = 0

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not game_paused:
                # Removed shoot_sound.play()
                if ship.bullet_power == 1:
                    bullet = Bullet(ship.rect.centerx, ship.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                else:
                    # Triple shot for powered up ship
                    for offset in [-15, 0, 15]:
                        bullet = Bullet(ship.rect.centerx + offset, ship.rect.top, ship.bullet_power)
                        all_sprites.add(bullet)
                        bullets.add(bullet)
            elif event.key == pygame.K_p:
                game_paused = not game_paused
            elif event.key == pygame.K_r and game_over:
                # Reset game
                all_sprites = pygame.sprite.Group()
                bullets = pygame.sprite.Group()
                alien_bullets = pygame.sprite.Group()
                aliens = pygame.sprite.Group()
                powerups = pygame.sprite.Group()
                explosions = pygame.sprite.Group()

                ship = Ship()
                all_sprites.add(ship)

                for i in range(10):
                    alien = Alien(random.randint(1, 2))
                    all_sprites.add(alien)
                    aliens.add(alien)

                score = 0
                level = 1
                game_over = False
                alien_spawn_timer = 0
                wave_cleared = False
                wave_timer = 0

    if game_over or game_paused:
        # Display game over or paused message
        font = pygame.font.Font(None, 72)
        if game_over:
            text = font.render("GAME OVER", True, red)
            subtext = pygame.font.Font(None, 36).render("Press R to restart", True, white)
        else:
            text = font.render("PAUSED", True, yellow)
            subtext = pygame.font.Font(None, 36).render("Press P to continue", True, white)

        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 20))
        subtext_rect = subtext.get_rect(center=(screen_width // 2, screen_height // 2 + 30))

        screen.blit(text, text_rect)
        screen.blit(subtext, subtext_rect)
        pygame.display.flip()
        continue

    # Update
    all_sprites.update()

    # Check for wave cleared
    if len(aliens) == 0:
        if not wave_cleared:
            wave_cleared = True
            wave_timer = 180  # 3 seconds at 60 FPS

        if wave_timer > 0:
            wave_timer -= 1

        if wave_timer == 0 and wave_cleared:
            wave_cleared = False
            level += 1
            # Spawn new wave of aliens
            for i in range(10 + level * 2):
                alien_level = min(3, 1 + level // 2)
                alien = Alien(random.randint(1, alien_level))
                all_sprites.add(alien)
                aliens.add(alien)

    # Alien spawn timer
    alien_spawn_timer += 1
    if alien_spawn_timer >= 180 and len(aliens) < 20 + level * 2:  # Spawn new alien every 3 seconds
        alien_spawn_timer = 0
        alien_level = min(3, 1 + level // 2)
        alien = Alien(random.randint(1, alien_level))
        all_sprites.add(alien)
        aliens.add(alien)

    # Check for alien actions
    for alien in aliens:
        result = alien.update()
        if result == "shoot":
            alien_bullet = AlienBullet(alien.rect.centerx, alien.rect.bottom)
            all_sprites.add(alien_bullet)
            alien_bullets.add(alien_bullet)
        elif result:  # Alien escaped
            if not game_over:
                ship.lives -= 1
                if ship.lives <= 0:
                    game_over = True

    # Check for bullet collisions with aliens
    for bullet in bullets:
        alien_hits = pygame.sprite.spritecollide(bullet, aliens, False)
        for alien in alien_hits:
            alien.health -= bullet.power
            if alien.health <= 0:
                explosion_sound.play()
                score += 10 * alien.level

                # Create explosion
                explosion = Explosion(alien.rect.centerx, alien.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

                # Chance to drop power-up
                if random.random() < 0.2:  # 20% chance
                    power_type = random.choice(['health', 'shield', 'power'])
                    powerup = PowerUp(alien.rect.centerx, alien.rect.centery, power_type)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

                alien.kill()
            bullet.kill()
            break

    # Check for ship collision with alien bullets
    if not ship.invincible:
        bullet_hits = pygame.sprite.spritecollide(ship, alien_bullets, True)
        if bullet_hits:
            ship.lives -= 1
            ship.make_invincible()
            if ship.lives <= 0:
                game_over = True
            else:
                # Create explosion
                explosion = Explosion(ship.rect.centerx, ship.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

    # Check for ship collision with aliens
    # Check for ship collision with aliens
    if not ship.invincible:
        alien_crashes = pygame.sprite.spritecollide(ship, aliens, True)
        if alien_crashes:
            ship.lives -= 1
            ship.make_invincible()
            if ship.lives <= 0:
                game_over = True
            else:
                # Create explosion
                explosion = Explosion(ship.rect.centerx, ship.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

    # Check for ship collision with powerups
    powerup_hits = pygame.sprite.spritecollide(ship, powerups, True)
    for powerup in powerup_hits:
        powerup_sound.play()
        if powerup.type == 'health':
            ship.lives += 1
        elif powerup.type == 'shield':
            ship.make_invincible(300)  # 5 seconds of invincibility
        elif powerup.type == 'power':
            ship.power_up(600)  # 10 seconds of power-up

    # Draw everything
    screen.fill(bg_color)

    # Draw stars in the background
    for i in range(100):
        x = random.randint(0, screen_width)
        y = (random.randint(0, screen_height) + pygame.time.get_ticks() // 50) % screen_height
        pygame.draw.circle(screen, white, (x, y), 1)

    # Draw all sprites
    all_sprites.draw(screen)

    # Display score and level
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, white)
    level_text = font.render(f"Level: {level}", True, white)
    lives_text = font.render(f"Lives: {ship.lives}", True, white)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(lives_text, (10, 90))

    # Display power-up status if active
    if ship.bullet_power > 1:
        power_text = font.render(f"Power-up: {ship.power_timer // 60}s", True, yellow)
        screen.blit(power_text, (screen_width - 200, 10))

    # Display invincibility status if active
    if ship.invincible:
        invincible_text = font.render(f"Shield: {ship.invincible_timer // 60}s", True, blue)
        screen.blit(invincible_text, (screen_width - 200, 50))

    # Display wave cleared message
    if wave_cleared:
        wave_text = font.render(f"Wave Cleared! Next Level: {wave_timer // 60}", True, green)
        wave_rect = wave_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(wave_text, wave_rect)

    # Visual indicator for ship invincibility
    if ship.invincible:
        if pygame.time.get_ticks() % 200 < 100:  # Blinking effect
            pygame.draw.circle(screen, blue, ship.rect.center, 30, 2)

    # Refresh the screen
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

