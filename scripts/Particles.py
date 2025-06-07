import pygame

class Color_Particle:
     def __init__(self, game, pos, colors=[(255,255,255,5)]):
         self.game = game
         self.pos = pos
         self.colors = colors
         self.current = [0,0] # time, color
         
     def render(self, surf, offset=(0,0)):
         rect = pygame.Rect(*self.pos, 1,1)
         c = self.colors[self.current[1]][:3]
         pygame.draw.rect(surf,c,rect)
         # surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
         
         
     def update(self):
        self.current[0] += 1
        if self.current[0] >= self.colors[self.current[1]][3]:
            self.current[0] = 0
            self.current[1] += 1
            if self.current[1] >= len(self.colors):
                return True 
        
        return False

class Particle:
    def __init__(self, game, p_type, pos, velocity=[0,0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame
        
    def update(self):
        kill = False
        if self.animation.done:
            kill = True
            
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        self.animation.update()
        
        return kill
    

    def render(self, surf, offset=(0,0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
        
