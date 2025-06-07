
import sys
import pygame
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, foo
from globals import *

RENDER_SCALE = SCREEN[0] / DISPLAY[0]



class Editor:
    def __init__(self):
        

        pygame.init()
        pygame.display.set_caption("Editor")
        self.screen = pygame.display.set_mode(SCREEN)
        self.clock = pygame.Clock()
        self.display = pygame.Surface(DISPLAY, pygame.SRCALPHA)
        
        self.assets = {
            
            'tiles':load_images('tiles'),
            'walls':load_images('walls'),
            'decor':load_images('decor'),
            'bat':load_images('enemies/bat/'),
            'hood':load_images('enemies/hood/'),
            'slime':load_images('enemies/slime/'),
            'player':load_images('player'),
            'misc':load_images('enemies/misc'),
            'ui':load_images('ui'),
            'interact':load_images('interactive'),
            'totem':load_images('totem'),
            'disk':load_images("disks"),
            'person':load_images("him")
            }
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.z = 0
        self.movement = [False, False, False, False]
        
        self.tilemap = Tilemap(self, tile_size=8, editor=True)
        self.ongrid = True
        self.scroll = [0,0]
        self.fileName =  LVL_PREFIX + str(FILENAME) + '.json'
        try:
            self.tilemap.load(self.fileName)
            print(self.assets.keys())
        except:
            pass

        
        self.z = 0
        
        pygame.font.init()
        self.my_font = pygame.font.SysFont('Comic Sans MS', 10)
        
    def text(self, x, y, z):
        
        return self.my_font.render(f'({x}, {y}, {z})', False, (255,255,255))


    def run(self):
        while True:
            self.display.fill((0,0,0))
            
            
            
            self.scroll[0] += 2 *(self.movement[1] - self.movement[0])
            self.scroll[1] += 2 *(self.movement[3] - self.movement[2])

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))            
            self.tilemap.render(self.display, offset=render_scroll, layer=0)
            self.tilemap.render(self.display, offset=render_scroll, layer=1)
            
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(150)
            self.display.blit(current_tile_img, (5,5))
            

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size), self.z)
            
           
            self.display.blit(self.text(*tile_pos), (5, 25))
            
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)
            if self.clicking and self.ongrid:
               self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1]) + ';' + str(self.z)] = {'type':self.tile_list[self.tile_group], 'variant':self.tile_variant,'pos':tile_pos}
            
                    
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1]) + ';' + str(self.z)
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type':self.tile_list[self.tile_group], 'variant':self.tile_variant,'pos':(mpos[0] + self.scroll[0], mpos[1] + self.scroll[1], 0)})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4 or pygame.key == pygame.K_UP:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button ==  3:
                        self.right_clicking = False
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_UP:
                        self.z += 1
                    if event.key == pygame.K_DOWN:
                        self.z = max(0, self.z - 1)
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        print("SAVED!!!!")
                        self.tilemap.save(self.fileName)
        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
    


game = Editor()
game.run()

