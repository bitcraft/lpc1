from poise import *
from pyglet.media import Player

player = Player()

from PygletSource import PygletSource
source = PygletSource()

player.queue(source)
player.play()

sfx = osc.noise(gain=0 )
envsfx = envelope.adsr(sfx,attack=0.2,decay=0.2,sustain=0.2,release=2.0)
source.add(sfx, -1)

from pyglet import app
from pyglet import window

from pyglet import text

win = window.Window()

label = text.Label('testing pyglet playback',
                          font_name='Times New Roman',
                          font_size=24,
                          x=win.width//2, y=win.height//2,
                          anchor_x='center', anchor_y='center')

@win.event
def on_draw():
    win.clear()
    label.draw()

app.run()
