import pygame
import time

from bitmapfont import BitmapFont
from generator import Generator
from pygame.image import load
SCR_W = 320
SCR_H = 180

TW = 16
TH = 16

MAX_GRAVITY = 2

level_gen = Generator()

pygame.init()
surf = load('gfx/cursor.png')
cursor = pygame.cursors.Cursor((0,0), surf)
pygame.mouse.set_cursor(cursor)

TILES = {'#': pygame.image.load('gfx/wall.png'),
         '1': pygame.image.load('gfx/dissolve_01.png'),
         '2': pygame.image.load('gfx/dissolve_02.png'),
         '3': pygame.image.load('gfx/dissolve_03.png'),
         'F': pygame.image.load('gfx/floor.png'),
         'G': pygame.image.load('gfx/floor_g.png'),
         '~': pygame.image.load('gfx/water.png'),
         'O': pygame.image.load('gfx/rock.png'),

         'Pi': pygame.image.load('gfx/player_idle.png'),
         'P1': pygame.image.load('gfx/player_walk_01.png'),
         'P2': pygame.image.load('gfx/player_walk_02.png'),
         'P3': pygame.image.load('gfx/player_walk_03.png'),
         'P4': pygame.image.load('gfx/player_walk_04.png'),
         'P5': pygame.image.load('gfx/player_walk_05.png'),
         }

level = level_gen.run(1, 200, 11);


def getTile(x, y):
    if x >= len(level[0]):
        return '#'          # outside (to the right) of level area is always 'solid'
    if y >= len(level):
        return ' '          # outside (below) of level area is always 'empty'

    return level[y][x]

def setTile(x, y, tile):
    if x >= len(level[0]) or y >= len(level):
        return

    level[y] = level[y][:x] + tile + level[y][x+1:]


SCROLL_SPEED = 0.5

DEBUG_STRINGS = []

def debugPrint(stuff):
    global DEBUG_STRINGS
    DEBUG_STRINGS.append(str(stuff).upper())


class Player():
    def __init__(self, x, y):
        self.xpos = x
        self.ypos = y

        self.xdir = 0
        self.ydir = 0

        self.onGround = False
        self.shouldJump = False

        self.dead = False

    def getSprite(self):
        if self.xdir == 0:
            return TILES['Pi']
        else:
            if int(time.time() * 1000) % 500 < 100:
                return TILES['P1']
            if 100 <= int(time.time() * 1000) % 500 < 200:
                return TILES['P2']
            if 200 <= int(time.time() * 1000) % 500 < 300:
                return TILES['P3']
            if 300 <= int(time.time() * 1000) % 500 < 400:
                return TILES['P4']
            if 400 <= int(time.time() * 1000) % 500 < 500:
                return TILES['P5']
            else:
                return TILES['P1']

    def jump(self, state):
        self.shouldJump = state

    def update(self):
        if self.shouldJump:
            if self.onGround:
                self.ydir = -3
                self.shouldJump = False

        # gravity part 1
        tilex = int(self.xpos / TW + 0.5)
        tiley = int((self.ypos + TH * 0.9999) / TH)
        oldy = tiley
        if getTile(tilex, tiley) == ' ':
            overground = True
        else:
            overground = False

        debugPrint('overground: %s' % overground)

        self.ydir += 0.125
        self.onGround = False

        if self.ydir > MAX_GRAVITY:
            self.ydir = MAX_GRAVITY

        # update position
        self.xpos += self.xdir
        self.ypos += self.ydir

        # gravity part 2
        tilex = int(self.xpos / TW + 0.5)
        tiley = int((self.ypos + TH * 0.9999) / TH)
        if getTile(tilex, tiley) not in [' ', '~']:
            if overground and tiley > oldy:
                self.ydir = 0
                self.ypos = int(self.ypos / TH) * TH
                self.onGround = True

        debugPrint('onground: %s' % self.onGround)

        # horizontal collision (to the right)
        if self.xdir > 0:
            tilex = int(self.xpos / TW + 0.9999)
            tiley = int(self.ypos / TH)
            if getTile(tilex, tiley) not in [' ', '~']:
                self.xpos = int(self.xpos / TW) * TW
                self.xdir = 0

        # horizontal collision (to the left)
        if self.xdir < 0:
            tilex = int(self.xpos / TW)
            tiley = int(self.ypos / TH)
            if getTile(tilex, tiley) not in [' ', '~']:
                self.xpos = int(self.xpos / TW + 0.9999) * TW
                self.xdir = 0

        # fall into water
        if self.ypos > len(level) * TH + 50:
            self.dead = True

class Game():
    def __init__(self):
        self.scrollx = 0

        # find player start position
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 'P':
                    self.player = Player(x * TW, y * TH)

                    # remove the 'P' from level data
                    setTile(x, y, ' ')

    def drawTile(self, screen, tile, x, y):
        screen.blit(tile, (x * TW - self.scrollx, y * TH + 4))

    def drawSprite(self, screen, tile, x, y):
        screen.blit(tile, (x - self.scrollx, y + 4))

    def playerLeft(self, state):
        if state:
            self.player.xdir = -1
        else:
            if self.player.xdir < 0:
                self.player.xdir = 0

    def playerRight(self, state):
        if state:
            self.player.xdir = 1
        else:
            if self.player.xdir > 0:
                self.player.xdir = 0

    def playerJump(self, state):
        self.player.jump(state)

    def render(self, screen, font):
        # draw sky
        screen.fill((64,128,192))

        font.centerText(screen, 'F12 = TOGGLE SCROLL', y=10)

        # draw level
        for y in range(len(level)):
            for x in range(len(level[0])):
                tile = level[y][x]
                if tile in TILES:
                    self.drawTile(screen, TILES[tile], x, y)

        # draw player
        self.drawSprite(screen, self.player.getSprite(), self.player.xpos, self.player.ypos)

    def update(self):
        if self.scrollx < len(level[0]) * TW - SCR_W:
            self.scrollx += SCROLL_SPEED

        self.player.update()

        if self.player.dead:
            # respawn (for debug)
            self.player.ypos = -TH
            self.player.xpos = self.scrollx + 5 * TW
            self.player.ydir = 0
            self.player.dead = False

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

                elif e.key == pygame.K_F12:
                    global SCROLL_SPEED
                    if SCROLL_SPEED == 0:
                        SCROLL_SPEED = 0.5
                    else:
                        SCROLL_SPEED = 0

                elif e.key == pygame.K_LEFT:
                    self.game.playerLeft(True)

                elif e.key == pygame.K_RIGHT:
                    self.game.playerRight(True)

                elif e.key == pygame.K_UP:
                    self.game.playerJump(True)

            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                setTile(int(pos[0]/TW + self.game.scrollx/TW) ,int(pos[1]/TH),'G')


            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT:
                    self.game.playerLeft(False)

                elif e.key == pygame.K_RIGHT:
                    self.game.playerRight(False)

                elif e.key == pygame.K_UP:
                    self.game.playerJump(False)

            elif e.type == pygame.QUIT:
                self.running = False

    def run(self):
        self.game = Game()

        while self.running:
            self.game.render(self.screen, self.font)

            self.font.locate(0, 0)
            for string in DEBUG_STRINGS:
                self.font.drawText(self.screen, string)
            DEBUG_STRINGS.clear()

            pygame.display.flip()

            self.controls()

            self.game.update()

            self.clock.tick(60)

        pygame.quit()

app = Application()
app.run()

