import os
import pygame

BASE_IMG_PATH = 'data/images/'

def foo(sprite_sheet, x, y, width=8, height=8):
    return sprite_sheet.subsurface(x,y,width,height)



def load_image(path):
    try:
        img = pygame.image.load(BASE_IMG_PATH + path).convert()
        img.set_colorkey((3,1,0))
    except:
        img = pygame.image.load(BASE_IMG_PATH + path + '/0.png').convert()
        img.set_colorkey((3,1,0))
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
        
    return images


class Animation:
    def __init__(self, images, img_dur=30, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        
    def play(self):
        self.done = False
        self.frame = 0


    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]

