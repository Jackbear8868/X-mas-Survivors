import pygame
from pygame.locals import * # CONSTS
from .config import width,height
from random import randrange, random
from numpy import array 
from numpy.linalg import norm

class Enemy(pygame.sprite.Sprite):

    def __init__(self, pos, player,
        max_hp=10, atk=1, speed=20, amr=0, xp=1):
        super().__init__()
        self.image = pygame.Surface([15,15])
        self.image.fill("#ff0000")
        self.rect = self.image.get_rect()
        self.pos = array(pos)
        self.player = player

        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.speed = speed
        self.amr = amr
        self.xp = xp


    def update(self, dt):
        if self.hp == 0:
            self.player.xp += self.xp
            self.kill()
            return
        drct = self.player.pos-self.pos
        drct /= norm(drct)
        self.pos += self.speed*dt*drct
        self.rect.center = self.pos

    def avoid(self, knockback=20):
        drct = self.pos - self.player.pos
        drct /= norm(drct)
        self.pos += drct*knockback

    @classmethod
    def spawn_enemy(cls, player, type='test', amt=1):
        spawn_pos = (random()*width, random()*height)
        while norm(spawn_pos-player.pos) < 200 :
            # respawn if too near player
            spawn_pos = (random()*width, random()*height)            
        
        enemies = []
        for i in range(amt):
            enemies.append(Enemy(spawn_pos, player=player))

        return enemies

    @staticmethod
    def nearest_enemy(player_pos, enemies):
        return min(enemies, key=lambda enemy: norm(enemy.pos-player_pos))