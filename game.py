"""Some simple skeleton code for a pygame game/animation

This skeleton sets up a basic 800x600 window, an event loop, and a
redraw timer to redraw at 30 frames per second.

Author: Archin Wadhwa; All rights reserved
"""
from __future__ import division
import math
import sys
import pygame

MARGIN = 10
INITIAL_LIVES = 3
PLAYER_SPEED = 20

class MyGame(object):
    
    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        
        self.loseLifeSound = pygame.mixer.Sound('LoseLife.wav')
        self.gameOverSound = pygame.mixer.Sound('GameOver.wav')
        self.playSound = pygame.mixer.Sound('GamePlay.wav')
        self.gunShotSound = pygame.mixer.Sound('gunshot.wav')
        
        self.loseLifeMsg = pygame.font.SysFont("comicsansms", 60).render("You Lose a life", True, (0,0,0))
        self.gameMsg = pygame.font.Font("OLDENGL.ttf", 80).render("Zombie Game", True, (0,0,0))
        self.gameMsg2 = pygame.font.Font("OLDENGL.ttf", 30).render("Press Space to Start", True, (0,0,0))
        self.gameMsg3 = pygame.font.Font("OLDENGL.ttf", 30).render("Press Space to Retry", True, (0,0,0))

        # set up a 640 x 480 window
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))

        # use a black background
        self.bg_img = pygame.image.load("bg.png")

        # Load zombie image
        self.zombie_img = pygame.image.load("zombie.png")
        # Load player image
        self.player_img = pygame.image.load("soldier.png")
        
        self.started = False
        # restart game
        self.restart()
        
        # Setup a timer to refresh the display FPS times per second
        self.FPS = 30
        self.REFRESH = pygame.USEREVENT+1
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)
    
    def reset(self):
        self.zombie_x = 0
        self.zombie_y = self.height - self.zombie_img.get_height()
        self.bullet_shot = False
        self.bullet_x = 0
        self.bullet_y = 0
        self.player_x = self.width - self.player_img.get_width()
        self.player_y = self.height - self.player_img.get_height()
        self.jumping = False
        self.counter = 0
        if self.started:
            self.playSound.play(-1)
        
    def restart(self):
        if self.started:
            self.gameMsg = pygame.font.Font("OLDENGL.ttf", 80).render("Game Over", True, (0,0,0))
            self.gameOver = False
            self.playing = True
        else:
            self.gameOver = True
            self.playing = False
        self.lives = INITIAL_LIVES
        self.score = 0
        self.level = 1
        self.reset()

    def run(self):
        """Loop forever processing events"""
        running = True
        while running:
            event = pygame.event.wait()

            # player is asking to quit
            if event.type == pygame.QUIT:
                running = False

            # time to draw a new frame
            elif event.type == self.REFRESH:
                #checking pressed keys
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.playing and not self.gameOver:
                    self.player_x -= PLAYER_SPEED
                    if self.player_x < 0:
                        self.player_x = 0
                if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.playing and not self.gameOver:  
                    self.player_x += PLAYER_SPEED
                    if self.player_x > self.width - self.player_img.get_width():
                        self.player_x = self.width - self.player_img.get_width()
                if keys[pygame.K_UP] or keys[pygame.K_w] and self.playing and not self.jumping and not self.gameOver:
                    self.jumping = True
                    self.counter = 0
                if self.gameOver and keys[pygame.K_SPACE]:
                    self.started = True
                    # restart the whole game
                    self.restart()
                self.draw()
                self.checkZombieShot()
                self.checkCollision()
                self.checkNextRound()
                self.counter += 1
            # gun shot
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.bullet_shot:
                self.bullet_shot = True
                self.bullet_x = int(self.player_x) + self.player_img.get_width()
                self.bullet_y = int(self.player_y) + 25
                self.gunShotSound.play()
            else:
                pass # an event type we don't handle
                
    def checkZombieShot(self):
        if self.bullet_shot:
            if abs(self.bullet_x - (self.zombie_x + self.zombie_img.get_width() / 2)) < self.zombie_img.get_width() / 2 \
                    and abs(self.bullet_y - (self.zombie_y + self.zombie_img.get_height() / 2)) < self.zombie_img.get_height() / 2:
                # zombie is shot
                self.score += self.level * 10
                self.level += 1
                self.zombie_x = -self.zombie_img.get_width()
                self.bullet_shot = False
                
    def checkCollision(self):
        if self.playing and abs(self.player_x - self.zombie_x) < 50 and abs(self.player_y - self.zombie_y) < 200:
            self.playing = False
            self.counter = 0
            # decrease lives and check game over
            self.lives -= 1
            self.playSound.stop()
            if self.lives <= 0:
                self.gameOver = True
                self.gameOverSound.play()
            else:
                self.loseLifeSound.play()
            
    def checkNextRound(self):
        if not self.playing and not self.gameOver and self.counter > 3 * self.FPS:
            self.playing = True
            self.reset()

    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        self.screen.blit(self.bg_img, (0, 0))
        
        if self.started:
            # display current lives
            lifeMsg = pygame.font.SysFont("comicsansms", 20).render("Lives: " + str(self.lives), True, (0,0,0))
            self.screen.blit(lifeMsg, (MARGIN, MARGIN))
            # display current score
            scoreMsg = pygame.font.SysFont("comicsansms", 20).render("Score: " + str(self.score), True, (0,0,0))
            self.screen.blit(scoreMsg, (self.width - scoreMsg.get_width() - MARGIN, MARGIN))
        
        if not self.gameOver and self.playing:
            # zombie move
            self.zombie_x += int(math.sqrt(self.level) * 5)
            if self.zombie_x > self.width:
                self.zombie_x = -self.zombie_img.get_width()
            
            # player move
            if self.jumping:
                self.player_y -= 170 * (self.counter/30) - 1 / 2 * 500 * (self.counter/30) ** 2
                if self.player_y > self.height - self.player_img.get_height():
                    self.player_y = self.height - self.player_img.get_height()
                    self.jumping = False
            
            # move bullet
            if self.bullet_shot:
                pygame.draw.circle(self.screen, (0,0,0), (self.bullet_x, self.bullet_y), 3)
                self.bullet_x += 40
                if self.bullet_x > self.width:
                    self.bullet_shot = False
            # display zombie and player
            self.screen.blit(self.zombie_img, (self.zombie_x, self.zombie_y))
            self.screen.blit(self.player_img, (self.player_x, self.player_y))
        # lose one round
        if not self.gameOver and not self.playing:
            self.screen.blit(self.loseLifeMsg, ((self.width - self.loseLifeMsg.get_width())//2, (self.height - self.loseLifeMsg.get_height())//2))
        # game is over
        if self.gameOver:
            self.screen.blit(self.gameMsg, ((self.width - self.gameMsg.get_width())//2, (self.height - self.gameMsg.get_height())//2))
            if self.started == False:
                self.screen.blit(self.gameMsg2, (((self.width - self.gameMsg2.get_width())//2), ((self.height - self.gameMsg2.get_height())//2)+100))
            else:
                self.screen.blit(self.gameMsg3, (((self.width - self.gameMsg2.get_width())//2), ((self.height - self.gameMsg2.get_height())//2)+100))
        # flip buffers so that everything we have drawn gets displayed
        pygame.display.flip()

MyGame().run()
pygame.quit()
sys.exit()

