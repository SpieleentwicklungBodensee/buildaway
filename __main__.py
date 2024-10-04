import pygame
import time

from bitmapfont import BitmapFont
from generator import Generator

SCR_W = 320
SCR_H = 180

TW = 16
TH = 16

level_gen = Generator()

pygame.init()

TILES = {'#': pygame.image.load('gfx/wall.png'),
         '1': pygame.image.load('gfx/dissolve_01.png'),
         '2': pygame.image.load('gfx/dissolve_02.png'),
         '3': pygame.image.load('gfx/dissolve_03.png'),
         'F': pygame.image.load('gfx/floor.png'),
         'G': pygame.image.load('gfx/floor_g.png'),
         '~': pygame.image.load('gfx/water.png'),
         'O': pygame.image.load('gfx/rock.png'),

         'P': pygame.image.load('gfx/player_01.png'),
         'p': pygame.image.load('gfx/player_02.png'),
         }

level = level_gen.run(1, 20, 11);


class Player():
    def __init__(self, x, y):
        self.xpos = x
        self.ypos = y

    def getSprite(self):
        if int(time.time() * 1000) % 400 < 200:
            return TILES['P']
        else:
            return TILES['p']

class Game():
    def __init__(self):
        self.scrollx = 0

        # find player start position
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 'P':
                    self.player = Player(x * TW, y * TH)

                    # remove the 'P' from level data
                    self.setTile(x, y, ' ')

    def setTile(self, x, y, tile):
        level[y] = level[y][:x] + tile + level[y][x+1:]

    def drawTile(self, screen, tile, x, y):
        screen.blit(tile, (x * TW - self.scrollx, y * TH + 4))

    def drawSprite(self, screen, tile, x, y):
        screen.blit(tile, (x - self.scrollx, y + 4))

    def render(self, screen, font):
        # draw sky
        screen.fill((64,128,192))

        font.centerText(screen, 'ES SCROLLT...', y=5)

        # draw level
        for y in range(len(level)):
            for x in range(len(level[0])):
                tile = level[y][x]
                if tile in TILES:
                    self.drawTile(screen, TILES[tile], x, y)

        # draw player
        self.drawSprite(screen, self.player.getSprite(), self.player.xpos, self.player.ypos)

    def update(self):
        if self.scrollx >= len(level[0]) * TW - SCR_W:
            return
        self.scrollx += 0.5


class Application():
    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)

        self.font = BitmapFont('gfx/heimatfont.png', 8, 8, [(255, 255, 255)])

        self.clock = pygame.time.Clock()

    def controls(self):
        while True:
            e = pygame.event.poll()

            if not e:
                break

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            elif e.type == pygame.QUIT:
                self.running = False

    def run(self):
        self.game = Game()

        while self.running:
            self.game.render(self.screen, self.font)

            pygame.display.flip()

            self.controls()

            self.game.update()

            self.clock.tick(60)

        pygame.quit()

app = Application()
app.run()

