import json
import pygame
from globals import *

AUTOTILE_MAP = {
    tuple(sorted([(1,0), (0,1)])) : 0,
    tuple(sorted([(1,0), (0,1), (-1,0)])) : 1,
    tuple(sorted([(-1,0), (0,1)])) : 2,
    tuple(sorted([(-1,0), (0,-1),(0,1)])) : 3,
    tuple(sorted([(-1,0), (0,-1)])) : 4,
    tuple(sorted([(-1,0),(0,-1),(1,0)])) : 5,
    tuple(sorted([(1,0),(0,-1)])) : 6,
    tuple(sorted([(1,0),(0,-1),(0,1)])) : 7,
    tuple(sorted([(1,0),(-1,0),(0,1),(0,-1)])) : 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

class Tilemap:
    
    def __init__(self, game, tile_size=16, editor=False):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.editor = editor

    def extract_pairs(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
        for loc in list(self.tilemap.keys()):
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
                    
                    
        return matches

    def extract(self, ids, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            
            if tile['type'] in ids:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
        for loc in list(self.tilemap.keys()):
            tile = self.tilemap[loc]
            if tile['type'] in ids:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
                    
                    
        return matches
        
  
    def render(self, surface, offset=(0,0), layer=0):
        
        # for loc in self.tilemap:
        #     tile = self.tilemap[loc]
        #     surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        
        for x in range(offset[0] // self.tile_size, (offset[0] + surface.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surface.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y) + ';' + str(layer)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] != 'interact' or (tile['variant'] != 6 and tile['variant'] != 7):
                        surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
                    elif tile['type'] == 'interact' and (tile['variant'] == 6 or tile['variant'] == 7) and self.editor:
                        surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
                        

        for tile in self.offgrid_tiles:
            surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))


    def tiles_around(self, pos):
        tiles = []
        for i in range(2):
            tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size), i)
            for offset in NEIGHBOR_OFFSETS:
                check_loc = str(tile_loc[0] + offset[0]) + ";" + str(tile_loc[1] + offset[1]) + ';' + str(i)
                if check_loc in self.tilemap:
                    tiles.append(self.tilemap[check_loc])
                
        return tiles
    

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                # rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
                rects.append(("physics", pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)))
            elif tile['type'] in INTERACT_TILES:
                rects.append(("interact", pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), tile['variant']))
        return rects


    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap':self.tilemap, 'tile_size':self.tile_size,'offgrid':self.offgrid_tiles}, f)
        f.close()
        

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        

    # def autotile(self):
    #     for loc in self.tilemap:
    #         tile = self.tilemap[loc]
    #         neighbors = set()
    #         for shift in [(1,0), (-1,0), (0,-1),(0,1)]:
    #             check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
    #             if check_loc in self.tilemap:
    #                 if self.tilemap[check_loc]['type'] == tile['type']:
    #                     neighbors.add(shift)
                        
    #         neighbors = tuple(sorted(neighbors))
    #         if tile['type'] in AUTOTILE_TYPES and neighbors in AUTOTILE_MAP:
    #             tile['variant'] = AUTOTILE_MAP[neighbors]
                

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
            
        return None
