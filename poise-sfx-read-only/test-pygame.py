import sys
import pygame
from pygame.locals import *

pygame.init()

pygame.font.init()

screen = pygame.display.set_mode((640, 480))pygame.display.set_caption("POISE")

background = pygame.Surface(screen.get_size())background = background.convert()background.fill((250, 250, 250))

if pygame.font:    font = pygame.font.Font(None, 36)    text = font.render("testing pygame output", 1, (10, 10, 10))    textpos = text.get_rect()    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery    background.blit(text, textpos)
    
    
import numpy
a = numpy.zeros([48000,2],numpy.float)
snd = pygame.sndarray.make_sound(a)
snd.play()
    
clock = pygame.time.Clock()while True:
    clock.tick(60)    
    for event in pygame.event.get():        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):            sys.exit()
            
    screen.blit(background, (0, 0))    pygame.display.flip()
