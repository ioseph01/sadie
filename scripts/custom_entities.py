# from scripts.entities import *

# class Drone_Nest_Builder(Drone):
#     def __init__(self, game, hp=5):
#         super().__init__(game, "enemy", (25,25), [4,4], [2,2,.5], chase_factor=2, hp=hp, accuracy=random.randint(0,132),guns = [Gun(self, 150, 0, {'velocity':[2,2,.25], 'size':lambda:random.randint(4, 16), 'hp':100,  'max_velocity':4, 'lifetime':40,
#       'bounces':1, 'children': 2, 'descendants':2})])
        
    
# class Drone_Queen1(Drone):
#     def __init__(self, game, size=32, hp=200):
#         self.phase = 0
#         super().__init__(game, "enemy", (25,25), [size, size], [2,2,.5], chase_factor=1, hp=hp, accuracy=random.randint(0,132),
#                          guns = [Gun(self, 150, 0, {'velocity':[2,2,.25], 'size':lambda:random.randint(4, 16), 'hp':100,  'max_velocity':4, 'lifetime':40,
#       'bounces':1, 'children': 2, 'descendants':2}), Gun(self, 250, 0, {'velocity':[0,0,8], 'size': 16})])
        
#     def shoot(self):
#         if 50 > len(self.game.enemies):
#             super().shoot()

#     def update(self, tilemap):
#         super().update(tilemap)
#         if self.hp < 100 and self.phase < 1:
#             self.phase += 1
#             self.velocity[2] *= 3
#             self.chasing[0] /= 2
#             self.chase_factor = 2
            
#     def update(self, tilemap):
#         super().update(tilemap)
#         if 30 > len(self.game.enemies) and random.randint(0,100) < 10:
#                 self.game.enemies.append(Drone(self.game, "enemy", self.rect().center, [4,4], [2,2,.5], chase_factor=2, hp=25, accuracy=random.randint(0,132),guns = [Gun(self, 150, 0, {'velocity':[2,2,.25], 'size':lambda:random.randint(4, 16), 'hp':100,  'max_velocity':4, 'max_distance':lambda:random.randint(60,200),
#                                   'bounces':1, 'children': 2, 'descendants':2})]))
            

# class Drone_Queen2(Drone):
#     def __init__(self, game, size=32, hp=200):
#         self.phase = 0
#         super().__init__(game, "enemy", (25,25), [size,size], [2,2,1], chase_factor=1, accuracy=random.randint(0,132), chase_cooldown=400, hp=hp,
#                          guns=[Gun_Drone(self, 6,0,{'lifetime':250, 'velocity':[0,0,2], 'size':4, 'hp':1, 'chase_cooldown':1, 'chase_factor':1})
#                                ])
        
#     def shoot(self):
#         if self.guns is not None:
#             for gun in self.guns:
#                 if isinstance(gun, Gun_Drone):
#                     if 40 > len(self.game.enemies):
#                         gun.shoot(target=self.game.player.rect().center, rect=self.rect().center)
#                 elif isinstance(gun, Gun_Spin):
#                     gun.shoot(target=self.game.player.rect().center, rect=self.rect().center)
#                 elif self.target is not None:
#                     gun.shoot(target=self.game.player.rect().center, rect=self.rect().center)

#     def update(self, tilemap):
#         super().update(tilemap)
#         print(self.velocity)
#         if self.hp < 100 and self.phase < 1:
#             self.phase += 1
#             self.velocity[2] = 2
#             self.chasing[0] = 10
#             self.chase_factor = 2
#             self.guns[0].bullet_settings['velocity'] = [0,0,1]
#             self.guns[0].bullet_settings['chase_factor'] = 4
#             self.guns[0].bullet_settings['chase_cooldown'] = 200
            
#         if self.phase >= 1:
#             self.hp = max(self.hp + 3, 200) if random.randint(0,10) == 1 and self.hp % 5 != 0 else self.hp
