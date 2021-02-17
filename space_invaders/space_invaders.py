#Author: Rosario Moscato
#Title: New Space Invaders
#Features: Playe Vs CPU, Explosions and Sounds

import pygame
from pygame import mixer
from pygame.locals import *
import random

pygame.init()


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

#define fps
clock = pygame.time.Clock()
fps = 60 

screen_width = 600
screen_height = 780 #800

#FONTS
font30 = pygame.font.SysFont('z003',30)
font40 = pygame.font.SysFont('z003',40)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("New Space Invaders")

#load sounds
explosion1_sound = pygame.mixer.Sound("img/explosion1.wav")
explosion1_sound.set_volume(0.25)

explosion2_sound = pygame.mixer.Sound("img/explosion2.wav")
explosion2_sound.set_volume(0.25)

laser_sound = pygame.mixer.Sound("img/laser.wav")
laser_sound.set_volume(0.25)


#define game variables
rows = 5
cols = 5

alien_cooldown = 1000 #alien bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()

countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 #0=game not started, 1=player wins, -1=player lost

#Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255,255,255)
YELLOW = (240,240,0)

#load image 
bg = pygame.image.load("img/bg.png") 


def draw_bg():
    screen.blit(bg, (0,0))


#Fuction to draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

'''
Spaceship Class
'''
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.health_start = health
        self.health_remaining = health

        self.last_shot = pygame.time.get_ticks()


    def update(self):
        #set movement speed
        speed = 8

        cooldown = 250 #milliseconds
        game_over = 0

        #get key pressed
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left >0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        #record current time
        time_now = pygame.time.get_ticks()

        
        #shooting
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_sound.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        
        #manage mask
        self.mask = pygame.mask.from_surface(self.image)


        #draw health bar
        pygame.draw.rect(screen, RED, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, GREEN, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <=0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over



'''
Bullet Class
'''
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion1_sound.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)



'''
Alien Class
'''
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1,5)) +".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


'''
Alien Bullet Class
'''
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):              
            self.kill()
            explosion2_sound.play()
            #decrease spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion) 

'''
Explosion Class
'''
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for n in range(1,6):
            img = pygame.image.load(f"img/exp{n}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20,20))
            if size == 2:
                img = pygame.transform.scale(img, (40,40))
            if size == 3:
                img = pygame.transform.scale(img, (160,160))
            #add images to the list
            self.images.append(img)
            self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3 #for exploion persistency
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #at the end of the animation, we cancel the explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()




#Create Sprite Group
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()



def create_aliens():
    '''
    this function creates am matrix (rows, cols) of aliens
    '''
    for row in range(rows):
        for i in range(cols):
            alien = Aliens(100 + i * 100, 100 + row * 70)
            alien_group.add(alien)



create_aliens()

#Create Player
spaceship = Spaceship(int(screen_width/2), screen_height - 100, 3)
spaceship_group.add(spaceship)


#Game Loop
run = True
while run:

    clock.tick(fps) 

    #draw background
    draw_bg() 

    if countdown == 0:

        #create random alien's bullets
        #record current time
        time_now = pygame.time.get_ticks()
        #alien shoot
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = AlienBullet(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now


        #all aliens killed
        if len(alien_group) == 0:
            game_over = 1

        if game_over ==0:
            #Update Spaceship
            game_over = spaceship.update()

            #update sprite group
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()

        else:
            if game_over == -1:
                draw_text("GAME OVER", font40, RED, int(screen_width / 2 - 100), int(screen_height / 2 + 70))
            if game_over == 1:
                draw_text("CONGRATULATIONS!", font40, YELLOW, int(screen_width / 2 - 200), int(screen_height / 2 + 20))
                draw_text("YOU WIN!!", font40, YELLOW, int(screen_width / 2 - 100), int(screen_height / 2 + 50))


    if countdown > 0:
        draw_text("SPACE INVADERS", font40, RED, int(screen_width / 2 - 160), int(screen_height / 2 + 40))
        draw_text("Get Ready!", font40, YELLOW, int(screen_width / 2 - 90), int(screen_height / 2 + 90))
        draw_text(str(countdown), font40, YELLOW, int(screen_width / 2 - 10), int(screen_height / 2 + 140))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    #explosion group    
    explosion_group.update()
 

    #Draw Sprite Groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)


    #event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update() 



pygame.quit()