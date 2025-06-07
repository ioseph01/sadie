import math
import random
import pygame
from globals import *
from scripts.Particles import Color_Particle, Particle
from scripts.utils import Animation, load_images


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def calculate_bullet_vector(target, pos=(488.0, 328.0), speed=10):
    player_pos = pos  # Use floats
    mpos = target
    # Keep everything as floats
    dx = float(mpos[0] - 4) - player_pos[0]
    dy = float(mpos[1] - 4) - player_pos[1]
    
    distance = math.sqrt(dx*dx + dy*dy)
    if distance > 0:
        dx = (dx / distance) * speed
        dy = (dy / distance) * speed
    return [dx, dy, speed]

def wander_(tilemap, pos, speed):
    x, y = random.randint(-8, 8), random.randint(-8, 8)
    tiles = tilemap.tiles_around(pos)
    for i in range(len(tiles)):
        c = random.choice(tiles)
        tiles.remove(c)
        if c['type'] not in PHYSICS_TILES:
            break

    return calculate_bullet_vector([c['pos'][0], c['pos'][1] + y], pos, speed)
    


class Entity:
    def __init__(self, game, e_type, pos, size, velocity, hp=1, wander=False):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.flip = False
        self.velocity = list(velocity)
        self.hp = hp
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}
        self.kb = [0,0]
        self.last_movement = [0,0]
        
        if wander:
            self.velocity = wander_(self.game.tilemap, self.pos, self.velocity[2])

    def hitbox_detect_x(self, rect, movement):
        for e in self.game.enemies:
            if e is not self and e.rect().colliderect(rect):
                if movement[0] > 0:
                    rect.right = e.rect().left
                if movement[0] < 0:
                    rect.left = e.rect().right
                    
        return rect
    

    def hitbox_detect_y(self, rect, movement):
        for e in self.game.enemies:
            if e is not self and e.rect().colliderect(rect):
                if movement[1] > 0:
                    rect.bottom = e.rect().top
                if movement[1] < 0:
                    rect.top = e.rect().bottom
                    
        return rect
    
    def interact(self, var, movement=(0,0)):
        pass
        
    def x_axis(self, tilemap, frame_movement):
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect[1]):
                if rect[0] == "interact":
                    self.interact(rect[2], (frame_movement[0],0))
                else:
                    rect = rect[1]
                    if frame_movement[0] > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True

                    if frame_movement[0] < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = True
                    
                    self.pos[0] = entity_rect.x
                
    def y_axis(self, tilemap, frame_movement):
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect[1]):
                if rect[0] == "interact":
                    self.interact(rect[2], (0,frame_movement[1]))
                else:
                    rect = rect[1]
                    if frame_movement[1] > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True

                    if frame_movement[1] < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                    
                    self.pos[1] = entity_rect.y
                
        
    def update(self, tilemap, movement=(0,0)):
        if self.hp <= 0:
            return 
        
        self.kb[0] = min([sign(self.kb[0]), self.kb[0] * 0.8], key=abs)
        self.kb[1] = min([sign(self.kb[1]), self.kb[1] * 0.8], key=abs) 
        
        if abs(self.kb[0]) < 0.001:
            self.kb[0] = 0
        if abs(self.kb[1]) < 0.001:
            self.kb[1] = 0
            
           
        self.collisions = {'up':False, 'down':False,'right':False,'left':False}
        if movement[0] == 0 and movement[1] == 0:
           frame_movement = [self.last_movement[0] * .85 + self.kb[0], self.last_movement[1] * .85 + self.kb[1]]
           if abs(frame_movement[0]) < 0.01:
                frame_movement[0] = 0
           if abs(frame_movement[1]) < 0.01:
                frame_movement[1] = 0
        else:
            m0, m1 = movement[0] * self.velocity[0] + self.kb[0], movement[1] * self.velocity[1] + self.kb[1]
            frame_movement = (min([m0,sign(m0) * self.velocity[2]], key=abs), min([m1,sign(m1) * self.velocity[2]], key=abs))
        # frame_movement = (movement[0] * self.velocity[0] + self.kb[0], self.kb[1] + movement[1] * self.velocity[1])
        
        # move_vec = pygame.math.Vector2(frame_movement[0], frame_movement[1])
        # if move_vec.x != 0 or move_vec.y != 0:
        #     move_vec.scale_to_length(self.velocity[2])
        #     frame_movement = [move_vec.x, move_vec.y]
                        
        self.x_axis(tilemap, frame_movement=frame_movement)
        self.y_axis(tilemap, frame_movement=frame_movement)
        
        self.last_movement = frame_movement  
            
        
    def player_detect(self):
        if self.game.level % 26 == 0:
            return
        if math.dist(self.rect().center, self.game.player.rect().center) < max(self.size[0], self.game.player.size[0]) and (self.game.player.inv_ticks == 0 or self.game.player.inv_ticks > 40):
            if self.game.player.inv_ticks == 0:
                self.game.hp[0] -= 1
                self.game.sfx['hurt'].play()
            self.game.screenshake = max(16, self.game.screenshake)
            if self.game.player.inv_ticks <= 0:
                self.game.player.inv_ticks = 50
            return True
        return False
    
    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def render(self, surface, offset):
        try:
        
            surface.blit(pygame.transform.flip(self.game.assets[(self.type,self.var)], self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        except:
            pygame.draw.rect(surface, (255,255,255), (self.pos[0] - offset[0], self.pos[1] - offset[1], *self.size))
        

    def knock_back(self, other, speed=2): # the other knocksback the self
        # angle = calculate_bullet_vector(self.rect().center, pos=other.rect().center, speed=speed)
        # self.kb = [angle[0] + self.kb[0], angle[1] + self.kb[1]]
        dx,dy = other.velocity[0], other.velocity[1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = (dx / distance) * speed
            dy = (dy / distance) * speed
        self.kb = [dx + self.kb[0], dy + self.kb[1]]
        

class Catch(Entity):
    def __init__(self, game, pos):
        super().__init__(game,"person",pos,(8,8),(0,0,0),hp=100)
        self.throw_tick = [0,60]
        self.throws = 0
        self.animation = self.game.assets[self.type]
        
    def render(self, surf, offset=None):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def update(self, tilemap=None, movement=None):
        self.animation.update()
        if self.game.player.pos[0] > self.pos[0]:
            self.flip = False
        else:
            self.flip = True
        for b in self.game.player_bullets.copy():
            if b.rect().colliderect(self.rect()):
                self.game.player_bullets.remove(b)
                x,y = self.game.player.pos
                if random.randint(0,2) > 0 and self.game.level == 0:
                    self.throws += 1
                    self.game.enemy_bullets.append(Disk_Projectile_Red(self.game,self.rect().center, calculate_bullet_vector([200, y + random.randint(-self.throws,self.throws)], self.pos, (self.throws + 1) * .5),spawn=True))
                else:
                    self.game.enemy_bullets.append(Disk_Projectile_Red(self.game,self.rect().center, calculate_bullet_vector([x, y + random.randint(-self.throws,self.throws)], self.pos, (self.throws + 1) * .5),spawn=True))
                    self.throws = min(self.throws + 1, 8) 
        
      
class Heart(Entity):
    
    def __init__(self, game, pos, e_type="heart"):
        super().__init__(game, e_type, pos, (8,8), (0,0,0))
        
    def render(self,surface,offset=(0,0)):
        surface.blit(self.game.assets[self.type], self.pos)

    def update(self, tilemap=None, movement=None):
        if math.dist(self.rect().center, self.game.player.rect().center) < max(self.size[0], self.game.player.size[0]):
            self.game.hp[0] += 1
            self.game.sfx['heart'].play()
            self.hp -= 1
            
class Disk(Entity):
    
    def __init__(self, game, pos, var=0):
        super().__init__(game, "disk", pos, (8,8), (0,0,0))
        self.var = var

    def update(self, tilemap=None):
        if math.dist(self.rect().center, self.game.player.rect().center) < max(self.size[0], self.game.player.size[0]):
            self.game.inventory[self.var] += 1
            self.hp -= 1
            
        if len(self.game.enemies) <= 0:
            self.velocity = calculate_bullet_vector(self.game.player.pos, self.pos, speed=.5)
            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]
            

    def render(self, surface, offset):
        try:
            surface.blit(pygame.transform.flip(self.game.assets[self.type][self.var], self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        except:
            super().render(surface, offset)

class Bullet(Entity):
    def __init__(self, game, e_type, pos, size, velocity, hp=1, bounces=1, descendant=0, children=0, max_distance=None, var=0, spawn_disk=False):
        super().__init__(game, e_type, pos, size, velocity, hp=hp) 
        self.bounces = bounces
        self.children = children
        self.descendant = descendant
        self.max_distance = [0, max_distance]
        self.var = var
        self.spawn = spawn_disk
        self.particle = [0,2]
        
    def render(self, surface, offset):
        try:
            surface.blit(pygame.transform.flip(self.game.assets[self.type][self.var], self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        except:
            super().render(surface, offset)
            
            
    def update(self, tilemap, movement=(0,0)):
        if self.bounces <= -1:
            self.hp = 0
        super().update(tilemap=tilemap, movement=(1,1))
        # if self.max_distance[1] is not None:
        #     self.max_distance[0] += 1
        #     if self.max_distance[0] >= self.max_distance[1]:
        #         self.bounces = -1
        #         return

        if self.collisions['up'] or self.collisions['down']:
                self.velocity[1] *= -1

                self.bounces -= 1
        if self.collisions['right'] or self.collisions['left']:
            self.velocity[0] *= -1

            self.bounces -= 1
        
            
    def player_detect(self):
        if super().player_detect():
            self.hp -= 1
            
class Disk_Projectile_Red(Bullet):
    def __init__(self, game, pos, velocity, spawn=False):
        super().__init__(game, "bullet", pos, (2,2), velocity, hp=1, bounces=0, var=0,spawn_disk=spawn) 
        
    def particle_(self, offset=0):
        self.game.particles.append(Color_Particle(self.game, [self.rect().centerx + random.randint(-1 - offset,1 + offset), random.randint(-1 - offset,1 + offset) + self.rect().centery], [(255,0,7, 15), (100,0,0,15)]))
        
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        if self.particle[0] == 0:
            self.particle_()
        self.particle[0] = (self.particle[0] + 1) % self.particle[1]
        if self.game.level % 26 == 0 and self in self.game.enemy_bullets:
            if self.rect().colliderect(self.game.player.rect()):
                self.hp = 0


class Disk_Projectile_Blue(Bullet):
    def __init__(self, game, pos, velocity):
        super().__init__(game, "bullet", pos, (2,2), velocity, hp=1000, bounces=0, var=1) 
        
    def particle_(self, offset=0):
        self.game.particles.append(Color_Particle(self.game, [self.rect().centerx + random.randint(-1 - offset,1 + offset), random.randint(-1 - offset,1 + offset) + self.rect().centery], [(255,236,49, 15), (100,92,15,15)]))
        
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        if self.particle[0] == 0:
            self.particle_()
        self.particle[0] = (self.particle[0] + 1) % self.particle[1]
        
class Disk_Projectile_Yellow(Bullet):
    def __init__(self, game, pos, velocity):
        super().__init__(game, "bullet", pos, (2,2), velocity, hp=2, bounces=6, var=2, max_distance=16) 
      
    def particle_(self, offset=0):
        self.game.particles.append(Color_Particle(self.game, [self.rect().centerx + random.randint(-1 - offset,1 + offset), random.randint(-1 - offset,1 + offset) + self.rect().centery], [(41,173,255, 15), (16,69,98,15)]))
        

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        if self.particle[0] == 0:
            self.particle_()
        self.particle[0] = (self.particle[0] + 1) % self.particle[1]
        
        if self.max_distance[0] >= 16:
            if self.rect().colliderect(self.game.player.rect()):
                self.pos = self.game.player.rect().center
                self.hp = 0
        else:
            self.max_distance[0] += 1

class Disk_Projectile_Enemy(Bullet):
    def __init__(self, game, pos, velocity, var=3, bounces=0, hp=1, spawn=False):
        super().__init__(game, "bullet", pos, (6,6), velocity, hp=hp, bounces=bounces, var=var, max_distance=16,spawn_disk=spawn) 
        var = (var % 3) + 3
        self.color = {
            3:[(126,37,28, 15), (49,34,42,15)],
            4:[(68,37,126,15),(26,14,49,15)],
            5:[(255,241,232,15),(100,94,91,15)],
            }[var]
        
    def particle_(self, offset=0):
        self.game.particles.append(Color_Particle(self.game, [self.rect().centerx + random.randint(-2 - offset,2 + offset), random.randint(-2 - offset,2 + offset) + self.rect().centery], self.color))
        

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        if self.particle[0] == 0:
            self.particle_()
        self.particle[0] = (self.particle[0] + 1) % self.particle[1]
        

    def player_detect(self):
        if super().player_detect():
            self.particle_(offset=3)
        

class Enemy(Entity):
    def __init__(self, game, e_type, pos, size, velocity=1, hp=1, step=4, var=0, animation=True):
        super().__init__(game, e_type, pos, size, velocity, hp=hp)
        self.step = [0, step]
        self.var = var
        self.tracking = [0, random.randint(15,80)]
        self.anim = animation
        if animation:
            self.animation = self.game.assets[(self.type, self.var)]    
        

    def update(self, tilemap, movement=(0,0)):
        self.bullet_detect()
        self.step[0] = (self.step[0] + 1) % self.step[1]
        dist = math.dist(self.game.player.pos, self.pos)
        if (min(self.size[0], self.game.player.size[0]) - 1 < dist <= 56) and self.step[0] == 0:
            self.velocity = calculate_bullet_vector([self.game.player.pos[0] + random.randint(-8,8), self.game.player.pos[1] + random.randint(-8,8)], pos=self.pos, speed=self.velocity[2])
            self.tracking[0] = self.tracking[1]
        
            # self.velocity = calculate_bullet_vector([self.pos[0] + random.randint(-8,8), self.pos[1] + random.randint(-8,8)], pos=self.pos, speed=self.velocity[2])
        if self.step[0] == 0:
            movement = (1,1)
            self.tracking[0] = max(self.tracking[0] - 1, 0)
            
        super().update(tilemap, movement=movement)
        if self.collisions['left']:
            self.collisions['left'] = False
            self.velocity[0] *= -1
            self.kb[0] += 1
            
        if self.collisions['right']:
            self.velocity[0] *= -1
            self.collisions['right'] = False
            self.kb[0] -= 1
            
        if self.collisions['up']:
            self.velocity[1] *= -1
            self.collisions['up'] = False
            self.kb[1] += 1
            
        if self.collisions['down']:
            self.collisions['down'] = False
            self.velocity[1] *= -1
            self.kb[1] -= 1
        if self.velocity[0] > 0:
            self.flip = False
        else:
            self.flip = True
        self.player_detect()
        if self.anim:
            self.animation.update()
        # for e in self.game.enemies:
        #     if e is not self and max(max(self.size), max(e.size)) + 2 >= math.dist(e.rect().center, self.rect().center):
        #         e.knock_back(e, speed=.1)
        #         movement = (0,0)
                
            
    def render(self, surface, offset=(0,0)):
        try:
            if self.anim:
                surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
            else:
                surface.blit(pygame.transform.flip(self.game.assets[self.type][self.var], self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        except:
            super().render(surface, offset)

    def bullet_detect(self):
        for b in self.game.player_bullets:
            if math.dist(self.rect().center, b.rect().center) < max(self.size[0], b.size[0]) and b.hp > 0:
                self.knock_back(b, speed=b.velocity[2])
                self.hp -= 1
                self.game.sfx['hit'].play()
                b.hp -= 1
                self.velocity = calculate_bullet_vector(self.game.player.pos,self.pos,self.velocity[2])
                for i in range(5):
                    b.particle_(offset=4)
                if b.var == 2:
                    b.velocity[0] *= -1
                    b.velocity[1] *= -1
                    b.bounces -= 1
                elif b.var == 1:
                    self.hp -= 1
                return True
        return False
                
class Shooter(Enemy):
    def __init__(self, game, e_type, pos, size, velocity=1, hp=1, step=4, cooldown=15, var=0):
        super().__init__(game, e_type, pos, size, velocity, hp=hp, var=var, step=step)
        self.cooldown = [0, cooldown]
        
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap)
        if math.dist(self.pos, self.game.player.pos) <= 48 and self.cooldown[0] == 0:
            self.shoot()
            self.cooldown[0] = 1
        self.cooldown[0] = (self.cooldown[0] + 1) % self.cooldown[1]

    def shoot(self):
        self.game.enemy_bullets.append(Disk_Projectile_Enemy(self.game, self.rect().center, calculate_bullet_vector(self.game.player.pos, pos=self.pos, speed=1), var=self.var+3))


class Totem(Entity):
    def __init__(self, game, e_type, pos, size, velocity=0, hp=10):
        super().__init__(game, e_type, pos, size, velocity, hp=hp)
        self.animation = self.game.assets[self.type]
        
    def spawn(self, b=None):
        self.game.sfx['spawn'].play()
        _ = random.randint(0,5)
        if _ == 0:
            spawner = {'pos':self.rect().center,'type':'hood', 'variant':random.randint(0,2)}
            self.game.assets[(spawner['type'], spawner['variant'])] = Animation(load_images(f"enemies/{spawner['type']}/{spawner['variant']}/"), img_dur=20)
            self.game.enemies.append( Shooter(self.game, spawner['type'], spawner['pos'], (6,7), [0,0,1], cooldown=60, step=30, hp=3, var=spawner['variant']))
        elif _ == 1:
            spawner = {'pos':self.rect().center,'type':'slime', 'variant':random.randint(0,2)}
            self.game.assets[(spawner['type'], spawner['variant'])] = Animation(load_images(f"enemies/{spawner['type']}/{spawner['variant']}/"),img_dur=30)
            self.game.enemies.append( Enemy(self.game, spawner['type'], spawner['pos'], (6,7), [0,0,2], step=30, hp=4, var=spawner['variant']))
        elif _ <= 4:
            spawner = {'pos':self.rect().center,'type':'misc', 'variant':random.randint(0,4)}
            self.game.enemies.append( Enemy(self.game, spawner['type'], spawner['pos'], (6,5), [0,0,1.5], step=15, hp=2, var=spawner['variant'], animation=False))
        else:
            spawn = True if b is not None else False
            var = random.randint(3,5) if not spawn else b.var
            self.game.enemy_bullets.append(Disk_Projectile_Enemy(self.game, self.rect().center, calculate_bullet_vector(self.game.player.pos, self.pos,.5),spawn=spawn,var=var))
            if spawn:
                self.game.player_bullets.remove(b)

    def update(self, tilemap, movement=(0,0)):
        if not self.animation.done:
            self.animation.update()
        if math.dist(self.pos, self.game.player.pos) <= 32:
            self.spawn()
            self.animation.play()
            self.hp -= 1
            
        for b in self.game.player_bullets.copy():
            if b.rect().colliderect(self.rect()) and b.hp > 0:
                self.hp -= 1
                self.game.sfx['hit'].play()
                b.hp -= 1
                b.velocity[0] *= -1
                b.velocity[1] *= -1
                b.bounces -= 1
                self.animation.play()
                self.spawn(b)


    def render(self, surf, offset=(0,0)):
        if self.animation.done:
            surf.blit(self.game.assets[self.type + '/idle'], (self.pos[0] - offset[0], self.pos[1] - offset[1])) 
        else:
            surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))

class Player(Entity):
    def __init__(self, game, e_type, pos, size, hp=1):
        super().__init__(game, e_type, pos, size, (1,1,1), hp=hp)
        self.stamina = 100
        self.inv_ticks = 0
        self.current = 0
        self.animation = self.game.assets['player']
        # self.gun = Gun(self, 2, 1, {'velocity':lambda : [2,2,random.randint(1,16)], 'size':lambda : random.randint(1, 22), 'lifetime':10, 
        #                             'max_distance': lambda: random.randint(5, 40), 'bounces':1, 'children':1})
        # self.gun = Gun_Dragon(self.game, 60, 4, 4, 60,1,40)
        # self.gun = Spin_Gun(self.game, 1, 1.5, 4, 0, bullet_hp=1, angle=math.pi / 13)
        self.last_movement = [0,0]
        self.rolling = False
        self.current = 0
        self.shoot_time = 0
        
    def render(self, surface, offset=(0,0)):
        # surface.blit(self.game.assets[self.type], (self.pos[0] - offset[0], self.pos[1] - offset[1])) 
        if self.inv_ticks % 2 == 0:
            surface.blit(pygame.transform.flip(self.game.assets[self.type], self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
    def interact(self, var, movement=(0,0)):
        if self.game.hp[0] > 0:
            if var < 3:
                if self.game.player.inv_ticks == 0:
                    self.game.hp[0] -= 1
                    self.game.sfx['hurt'].play()
                    self.inv_ticks = 50
                self.game.screenshake = max(16, self.game.screenshake)
            elif var <= 5:
                self.pos[0] -= movement[0] / 8
                self.pos[1] -= movement[1] / 8
                if movement[0] != 0 or movement[1] != 0:
                    dx = random.randint(-4,4)
                    self.game.particles.append(Color_Particle(self.game,[self.rect().centerx + dx, self.rect().bottom ],[(41,173,255,5)]))
            elif var == 6:
                self.game.level -= 1
                self.game.hp[1] = self.game.hp[0]
                self.game.hp[0] = 0
            elif var == 7:
                self.game.hp[1] = self.game.hp[0]
                self.game.level += 1
                self.game.hp[0] = 0
                self.game.win = True

            

    def update(self, tilemap, movement=(0,0)):
        if movement[0] > 0 and self.shoot_time == 0:
            self.flip = False
        elif movement[0] < 0 and self.shoot_time == 0:
            self.flip = True
        self.stamina = min(100, self.stamina + 1)
        if movement[0] != 0 or movement[1] != 0:
            self.last_movement = list(movement)
        # if self.rolling:
        #     movement_x = movement[0] + 2 * (abs(self.last_movement[0]) / self.last_movement[0])  if self.last_movement[0] != 0 else 0
        #     movement_y = movement[1] + 2 * (abs(self.last_movement[1]) / self.last_movement[1])  if self.last_movement[1] != 0 else 0
        #     if self.stamina == 40:
        #         self.rolling = False
        #         self.velocity[2] /= 1.5
                
        self.inv_ticks = max(self.inv_ticks - 1, 0)
        self.shoot_time = max(self.shoot_time - 1, 0)
        
        if  self.inv_ticks > 0:
            movement = (0,0)
        super().update(tilemap, movement)
        self.animation.update()
        
        

    def render(self, surface, offset=(0,0)):
        try:
            surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        except:
            super().render(surface, offset)
            
    def roll(self):
        if self.stamina >= 65:
            self.stamina = 0
            self.rolling = True
            self.velocity[2] *= 1.5



    def shoot(self, offset):
        # self.gun.shoot( self.rect().center, target=[pygame.mouse.get_pos()[0] - offset[0], pygame.mouse.get_pos()[1] - offset[1]])
        # self.guns[self.current].shoot(target=pygame.mouse.get_pos(),rect=self.rect().topleft)
        if self.game.inventory[self.current] > 0:
            self.game.sfx['shoot'].play()
            self.game.inventory[self.current] -= 1
            mpos = pygame.mouse.get_pos()
            
            if self.current == 0:
                v = calculate_bullet_vector((mpos[0] + offset[0], mpos[1] + offset[1]), pos=[RATIO * self.rect().center[0],self.rect().center[1] * RATIO], speed=2)
                self.game.player_bullets.append(Disk_Projectile_Red(self.game, self.rect().center, v))
            elif self.current == 1:
                v = calculate_bullet_vector((mpos[0] + offset[0], mpos[1] + offset[1]), pos=[RATIO * self.rect().center[0],self.rect().center[1] * RATIO], speed=8)
                self.game.player_bullets.append(Disk_Projectile_Blue(self.game, self.rect().center, v))
            else:
                v = calculate_bullet_vector((mpos[0] + offset[0], mpos[1] + offset[1]), pos=[RATIO * self.rect().center[0],self.rect().center[1] * RATIO], speed=4)
                self.game.player_bullets.append(Disk_Projectile_Yellow(self.game, self.rect().center, v))
                # self.game.player_bullets.append(Bullet(self.game, "bullet", self.rect().center, (2,2),  v, bounces=8, hp=8, var=2))
            if mpos[0] < RATIO * self.rect().center[0] and not self.flip:
                self.flip = True
                self.shoot_time = 10
                
            elif self.flip:
                self.flip = False
                self.shoot_time = 10
                
