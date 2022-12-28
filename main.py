import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame.locals import * # CONSTS
import sys
from bin.player import Player
from bin.weapon import Weapon
from bin.enemy import Enemy
from bin.config import *
from bin.backend import Backend
from bin.ui import *

pygame.init()
 

clock = pygame.time.Clock()

screen = pygame.display.set_mode((width, height))
manager = pygame_gui.UIManager((width,height))
for theme_file_path in theme_paths:
    manager.get_theme().load_theme(theme_file_path)

backend = Backend()

def gaming():

    player = Player(pos=(200,200))
    players = pygame.sprite.Group()
    players.add(player)
    player.weapons.append(Weapon('test', player=player, b_amt=7))
    player.weapons.append(Weapon('autoaim', player=player, b_speed=125, b_hp=2))

    # level_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(5,2,50,16), text='init',
    #     manager=manager, parent_element=xp_bar,
    #     anchors={'top':xp_bar, 'left':xp_bar}
    # )

    bullets, enemies, drops = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    enemy_timer = enemy_cooldown
    #gui init
    xp_bar_width = width-2*xp_bar_margin
    xp_bar = pygame_gui.elements.UIStatusBar(relative_rect=pygame.Rect(xp_bar_margin,xp_bar_margin,xp_bar_width,20), manager=manager,
        sprite=player, follow_sprite=False, anchors={'top':'top', 'left':'left', 'right':'right'},
        percent_method=player.get_xp_percent ,object_id=ObjectID('#xp_bar','@player_bar'),visible=0)
    xp_bar.status_text = lambda : f'Level {player.level}'
        
    hp_bar = pygame_gui.elements.UIStatusBar(relative_rect=(0,0,51,10), manager=manager,
        sprite=player, follow_sprite=True, anchors={'centerx':'left'},
        percent_method=player.get_health_percent, object_id=ObjectID('#hp_bar','@player_bar'))
    clock.tick() ##init call

    while True:
        xp_bar.visible = 1
        for event in pygame.event.get():
            manager.process_events(event=event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_p and not backend.paused:
                    backend.paused = True
                    ui_reload = 1
                    ui_cooldown = 1
                    resume_game =  pygame_gui.elements.UITextBox(html_text="resume",relative_rect=pygame.Rect((0,150), (100, 50)),
                            manager=manager,anchors={'centerx': 'centerx'},object_id=ObjectID(class_id='@selected'))
                    settings =  pygame_gui.elements.UITextBox(html_text="settings",relative_rect=pygame.Rect((0,225), (100, 50)),
                            manager=manager,anchors={'centerx': 'centerx'},object_id=ObjectID(class_id='@selected'))
                    quit_game =  pygame_gui.elements.UITextBox(html_text="quit",relative_rect=pygame.Rect((0,300), (100, 50)),
                            manager=manager,anchors={'centerx': 'centerx'},object_id=ObjectID(class_id='@selected'))
                    pause = [resume_game,settings,quit_game]
                    selected = 0
                    ds = 0

                if backend.paused:
                    if event.key == K_UP and selected>0:
                        selected-=1
                    if event.key == K_DOWN and selected<len(pause)-1:
                        selected+=1
                    if event.key == K_RETURN:
                        if pause[selected] == resume_game:
                            for option in pause:
                                option.kill()
                            backend.paused = False
                        else:
                            if pause[selected] == settings:
                                chosen = 'settings'
                            if pause[selected] == quit_game:
                                chosen = 'main_page'
                            for option in pause:
                                option.kill()
                                xp_bar.kill()
                                hp_bar.kill()
                            backend.paused = False
                            return chosen,False

        dt = clock.tick(FPS)/1000
        ds = clock.tick(FPS)/1000*3

        if backend.paused : 
            dt = 0
            ui_reload -= ds
            if ui_reload <= 0:
                pause[selected].visible = 0
                ui_reload += ui_cooldown
            else:
                pause[selected].visible = 1
            for i in range(len(pause)):
                if i == selected:
                    pass
                else:
                    pause[i].visible = 1


        keys = pygame.key.get_pressed()
        if keys[K_a] and not keys[K_d]:
            player.move('left', dt)
        if keys[K_d] and not keys[K_a]:
            player.move('right', dt)
        if keys[K_s] and not keys[K_w]:
            player.move('down', dt)
        if keys[K_w] and not keys[K_s]:
            player.move('up', dt)
        
        for weapon in player.weapons:
            weapon.reload -= 1*dt
            if weapon.reload <= 0:
                weapon.reload += weapon.cooldown
                bullets.add(weapon.shoot(player.rect.center, enemies))

        enemy_timer-= 1*dt
        if enemy_timer <= 0 : 
            enemy_timer = enemy_cooldown
            enemies.add(Enemy.spawn_enemy(player=player))


        #update position
        player.update(dt) 
        for bullet in bullets:
            bullet.update(dt)
        for enemy in enemies:
            drops.add(enemy.update(dt))
        for drop in drops:
            drop.update(dt)

        #collision code
        b_e_collide = pygame.sprite.groupcollide(bullets, enemies, False, False)

        for bullet, hit_enemies in b_e_collide.items():
            for enemy in hit_enemies: #bullet will have at least 1 health
                if enemy.hp == 0 :              
                    continue
                enemy.hp -= bullet.atk
                bullet.hp -= 1 


                if bullet.hp <= 0 : break

        enemies_atked = pygame.sprite.spritecollide(player, enemies, dokill=False)

        for enemy in enemies_atked:
            player.hp -= enemy.atk
            enemy.avoid()
            
        drops_absorbed = pygame.sprite.spritecollide(player, drops, dokill=False)
        
        for drop in drops_absorbed:
            drop.absorbed()

        # gui updates
        # level_text.set_text(f'{player.level} Levels')

        manager.update(dt)

        # draw zone
        screen.fill('#000000')
        bullets.draw(screen)
        drops.draw(screen)
        enemies.draw(screen)
        players.draw(screen) #player is always at the top
        manager.draw_ui(screen)

        pygame.display.flip()


        #print(clock.get_fps(), len(enemies), len(bullets))
    


while True:
    if backend.main_page:
        next_stage,backend.main_page = main_page(screen,manager)
    if backend.start_game:
        next_stage,backend.start_game = gaming()
    if next_stage == 'main_page':
        backend.main_page = True
    elif next_stage == 'start':
        backend.start_game = True