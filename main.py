import sys
import pygame
import random
import asyncio
from scripts.custom_entities import *
from scripts.utils import *
from scripts.entities import *
from scripts.tilemap import Tilemap
from globals import *



class Game:
    def __init__(self):
        

        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN)
        self.particles = []
        self.clock = pygame.Clock()
        self.display = pygame.Surface(DISPLAY, pygame.SRCALPHA)
        self.screenshake = 0
        self.assets = {
            'tiles':load_images('tiles'),
            'walls':load_images('walls'),
            'decor':load_images('decor'),
            'player':Animation(load_images('player')),
            'bat':Animation(load_images('enemies/bat')),
            'hood':Animation(load_images('enemies/hood/')),
            'slime':Animation(load_images('enemies/slime/')),
            'bullet':load_images("disks_projectile"),
            'disk':load_images("disks"),
            'misc':load_images('enemies/misc'),
            'heart':load_image('heart.png'),
            'ui':load_images('ui'),
            'interact':load_images('interactive'),
            'totem':Animation(load_images('totem'), loop=False),
            'totem/idle':load_images('totem')[0],
            'person':Animation(load_images('him'),img_dur=30),
            'text':load_image('text.png')
            }
        
        self.tilemap = Tilemap(self, tile_size=8)
        
        self.win = False
        self.scroll = [0,0] 
        self.movement = [0,0] # N E S W
        
        self.right_click = False
        self.left_click = False

        self.offset = [0,0]
        
        self.level = FILENAME
        self.hp = [5,5]
        self.inventory = [0,0,0]
        self.inventory_copy = self.inventory.copy()
        self.load_level()
        
    def swap_color(self, surface, old_color, new_color):
        image = surface.copy()
        px_array = pygame.PixelArray(image)
        px_array.replace(old_color, new_color)
        del px_array
        return image
    
    def reset(self):
        self.level = 0
        self.inventory = [0,0,0]
        self.inventory_copy = [0,0,0]
        self.hp = [5,5]
        self.load_level()
        
    def in_check(self, e):
        if int(e.pos[0]) in range(0,DISPLAY[0]) and int(e.pos[1]) in range(0,DISPLAY[1]):
            return True
        return False

    def load_level(self):
        if self.level == 26:
            self.inventory = [0,0,0]
            self.inventory_copy = [0,0,0]
        self.disks = []
            
        self.sfx = {
            'hurt':pygame.mixer.Sound('data/sfx/hurt.wav'),
            'shoot':pygame.mixer.Sound('data/sfx/shoot.wav'),
            'hit':pygame.mixer.Sound('data/sfx/hit.wav'),
            'spawn':pygame.mixer.Sound('data/sfx/spawn.wav'),
            'heart':pygame.mixer.Sound('data/sfx/life.wav')
            }
        self.sfx['spawn'].set_volume(0.4)
        if self.level == 1:
            self.inventory[0] = 0
            self.inventory_copy[0] = 0
        elif self.level == 0:
            self.disks.append(Heart(self,(2, 50),e_type="text"))

        if self.win:
            for i in range(3):
                self.inventory_copy[i] = max(self.inventory_copy[i], self.inventory[i])
        if self.level != 0 and self.level % 2 == 0:
            self.hp[1] = min(5, self.hp[1] + 1)
        self.win = False
        self.inventory = self.inventory_copy.copy()
        self.hp[0] = self.hp[1]
        try:
            self.tilemap.load(LVL_PREFIX + str(self.level) + ".json")
        except:
            self.tilemap.load(LVL_PREFIX + '0' + ".json")
            
        self.player = Entity(self, "player", (32, 70), (8,5), [1,1,1], hp=1000)
        self.enemy_bullets = []
        self.player_bullets = []
        self.particles = []
        self.enemies = [ ]
        
        

        for spawner in self.tilemap.extract(['hood', 'slime', 'player', 'bat', 'misc', 'totem', 'disk','person']):
                spawner['pos'] = spawner['pos'][:2]
                if spawner['type'] == 'hood':
                    self.assets[(spawner['type'], spawner['variant'])] = Animation(load_images(f"enemies/{spawner['type']}/{spawner['variant']}/"), img_dur=20)
                    
                    self.enemies.append( Shooter(self, spawner['type'], spawner['pos'], (6,7), [0,0,1], cooldown=60, step=45, hp=3, var=spawner['variant']))
                elif spawner['type'] == 'slime':
                    self.assets[(spawner['type'], spawner['variant'])] = Animation(load_images(f"enemies/{spawner['type']}/{spawner['variant']}/"),img_dur=30)
                    
                    self.enemies.append( Enemy(self, spawner['type'], spawner['pos'], (6,7), [0,0,2], step=45, hp=4, var=spawner['variant']))
                elif spawner['type'] == 'player':
                    self.player = Player(self, "player", spawner['pos'], (8,5), hp=1000)
                elif spawner['type'] == 'bat':
                    self.assets[(spawner['type'], spawner['variant'])] = Animation(load_images(f"enemies/{spawner['type']}/{spawner['variant']}/"),img_dur=15)
                    self.enemies.append( Enemy(self, spawner['type'], spawner['pos'], (6,7), [0,0,1], step=20, hp=2, var=spawner['variant']))
                elif spawner['type'] == 'totem':
                    self.enemies.append(Totem(self,spawner['type'], spawner['pos'],(5,5),(0,0,0),hp=4))
                elif spawner['type'] == 'disk':
                    self.disks.append(Disk(self,spawner['pos'],var=spawner['variant']))
                elif spawner['type'] == 'person':
                    self.enemies.append(Catch(self,spawner['pos']))
                else:
                    self.enemies.append( Enemy(self, spawner['type'], spawner['pos'], (6,5), [0,0,1], step=15, hp=1, var=spawner['variant'], animation=False))
                    
 
            

    async def run(self):
        while True:
            self.hp[0] = min(5,self.hp[0])
            for i in range(3):
                self.inventory[i] = min(5, self.inventory[i])
            if self.hp[0] <= 0:
                
                self.load_level()
                continue
            self.display.fill((0,0,0))
            
            # self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            # self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            # self.offset = render_scroll
            self.tilemap.render(self.display, render_scroll)
            self.tilemap.render(self.display, render_scroll, layer=1)
            pygame.draw.rect(self.display, (194,195,199),(0,0,9 * 4 + 1, 10))
            pygame.draw.rect(self.display, (0,0,0),(0,0,9 * 4, 9))
            self.display.blit(self.assets['heart'], (0,1))
            img = self.assets['ui'][self.hp[0]]
            if self.screenshake != 0:
                img = self.swap_color(img, (255,241,232),(255,0,0))
            self.display.blit(img, (5,4))
            
            self.display.blit(self.assets['disk'][0],(11,1))
            img = self.assets['ui'][self.inventory[0]]
            if self.player.current == 0:
                img = self.swap_color(img, (255,241,232),(255,236,49))
            self.display.blit(img, (14,4))
            
            self.display.blit(self.assets['disk'][1],(20,1))
            img = self.assets['ui'][self.inventory[1]]
            if self.player.current == 1:
                img = self.swap_color(img, (255,241,232),(255,236,49))
            self.display.blit(img, (23,4))
            
            # self.display.blit(self.assets['ui'][self.inventory[1]], (23,4))
            img = self.assets['ui'][self.inventory[2]]
            if self.player.current == 2:
                img = self.swap_color(img, (255,241,232),(255,236,49))
            self.display.blit(self.assets['disk'][2],(29,1))
            self.display.blit(img, (32,4))
            for disk in self.disks[::-1]:
                if disk.hp <= 0:
                    self.disks.remove(disk)
                else:
                    disk.update(self.tilemap)
                    disk.render(self.display, render_scroll)
                    
            for enemy in self.enemies[::-1]:
                if enemy.hp <= 0 or not self.in_check(enemy):
                    self.enemies.remove(enemy)
                    if random.randint(0,15) == 0:
                        self.disks.append(Heart(self,enemy.pos))
                else:
                    enemy.update(self.tilemap)
                    enemy.render(self.display, render_scroll)
                    
            for bullet in self.enemy_bullets[::-1]:
                if bullet.hp <= 0 or not self.in_check(bullet):
                    self.enemy_bullets.remove(bullet)
                    if bullet.spawn:
                        self.disks.append(Disk(self, bullet.pos, bullet.var % 3))
                else:
                    bullet.player_detect()
                    bullet.update(self.tilemap)
                    bullet.render(self.display, render_scroll)
                    
            for bullet in self.player_bullets[::-1]:
                if bullet.hp <= 0 or not self.in_check(bullet):
                    self.player_bullets.remove(bullet)
                    self.disks.append(Disk(self, bullet.pos, bullet.var))
                else:
                    bullet.update(self.tilemap)
                    bullet.render(self.display, render_scroll)

            if len(self.enemies) <= 0 and len(self.enemy_bullets) <= 0:
                self.tilemap.extract_pairs([('walls', 1)])

            self.player.update(self.tilemap, self.movement)
            for particle in self.particles[::-1]:
                 if particle.update():
                     self.particles.remove(particle)
                 else:
                    particle.render(self.display)
            if self.right_click:
                offset = [self.player.rect().centerx - self.scroll[0] - self.display.get_width() / 2, self.player.rect().centery - self.scroll[1] - self.display.get_height() / 2]
                self.player.shoot( (0,0))
                self.right_click = False
            if self.left_click:
                self.player.current = (self.player.current + 1) % 3
                self.left_click = False
            self.player.render(self.display, render_scroll)
            
            self.screenshake = max(0, self.screenshake - 1)
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.player.current = 0
                        if event.key == pygame.K_2:
                            self.player.current = 1
                        if event.key == pygame.K_3:
                            self.player.current = 2
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.movement[0] =  max (-1,  self.movement[0] - 1)
                        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.movement[0] = min (1, self.movement[0] + 1)
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            self.movement[1] = min(1, self.movement[1] + 1)
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.movement[1] = max (-1, self.movement[1] - 1)
                        if event.key == pygame.K_r:
                            self.reset()
                            self.load_level()
                            self.sfx['spawn'].play()
                            continue
                     
                    if event.type == pygame.MOUSEWHEEL:
                        if event.y == 1:
                            self.player.current = (self.player.current - 1) % 3
                        if event.y == -1:
                            self.player.current = (self.player.current + 1) % 3
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.right_click = True
                        if event.button == 3:
                            self.left_click = True
                        
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.right_click = False
                        if event.button == 3:
                            self.left_click = False
                            

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.movement[0] = min(self.movement[0] + 1, 1)
                        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.movement[0] = max(self.movement[0] - 1, -1)
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            self.movement[1] = max(-1, self.movement[1] - 1)
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.movement[1] = min (self.movement[1] + 1, 1)
                
                            
                        


            
            # self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()))
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)
            await asyncio.sleep(0)
            
Game().run()

async def main():
    game = Game()
    await game.run()
    
if __name__ == "__main__":
    asyncio.run(main())
