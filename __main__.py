import pygame
import time
import random

from bitmapfont import BitmapFont
from generator import Generator
from pygame.image import load
SCR_W = 320
SCR_H = 180

TW = 16
TH = 16

MAX_GRAVITY = 2
COYOTE_JUMP_TOLERANCE = 4

TILECOOLDOWN=150
CURRENTCOOLDOWN=150

SCROLL_SPEED = 0.5

DISSOLVE_SPEED = 6

level_gen = Generator()

pygame.init()
surf = load('gfx/cursor.png')
cursor = pygame.cursors.Cursor((0,0), surf)
pygame.mouse.set_cursor(cursor)
pygame.mixer.init()
pygame.mixer.music.load('sfx/NichtEinFlohWalzerWeitEntfernt.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play()

PLACESOUND = pygame.mixer.Sound('sfx/Plop.mp3')
DENYSOUND = pygame.mixer.Sound('sfx/Deny.wav')
DEATHSOUND = pygame.mixer.Sound('sfx/Death_Scream.mp3')

TILES = {'#': pygame.image.load('gfx/wall.png'),
         '1': pygame.image.load('gfx/dissolve_01.png'),
         '2': pygame.image.load('gfx/dissolve_02.png'),
         '3': pygame.image.load('gfx/dissolve_03.png'),
         'F': pygame.image.load('gfx/floor.png'),
         'G': pygame.image.load('gfx/floor_g.png'),
         '~': pygame.image.load('gfx/water.png'),
         '~~': pygame.image.load('gfx/water_02.png'),
         '~~~': pygame.image.load('gfx/water_03.png'),
         '~~~~': pygame.image.load('gfx/water_04.png'),
         'O': pygame.image.load('gfx/rock.png'),
         'D': pygame.image.load('gfx/door.png'),

         'Pi': pygame.image.load('gfx/player_idle.png'),
         'P1': pygame.image.load('gfx/player_walk_01.png'),
         'P2': pygame.image.load('gfx/player_walk_02.png'),
         'P3': pygame.image.load('gfx/player_walk_03.png'),
         'P4': pygame.image.load('gfx/player_walk_04.png'),
         'P5': pygame.image.load('gfx/player_walk_05.png'),

         'cursor': pygame.image.load('gfx/cursor.png'),
         'cursor_pressed': pygame.image.load('gfx/cursor_03.png'),
         'P6': pygame.image.load('gfx/player_jump_01.png'),
         'P7': pygame.image.load('gfx/player_jump_02.png'),
         }

FLOOR_TILES = ['#', '1', '2', '3', 'F', 'G', 'O']       # floor = player can stand on
OBSTACLES = ['#', 'F', 'G']                             # obstacle = player cannot walk into

PLACEABLE_TILES = ['1', 'O']                  # placeable = mouse player will place those


level = level_gen.run(1, 60, 11);


def getTile(x, y):
    if x >= len(level[0]):
        return '#'          # outside (to the right) of level area is always 'solid'
    if x < 0:
        return '#'          # outside (to the left) of level area is always 'solid'

    if y >= len(level):
        return ' '          # outside (below) of level area is always 'empty'
    if y < 0:
        return ' '          # outside (above) of level area is always 'empty'

    return level[y][x]

def setTile(x, y, tile):
    if x >= len(level[0]) or y >= len(level):
        return

    level[y] = level[y][:x] + tile + level[y][x+1:]

dissolveTiles = set()
def dissolveTile(x, y, tick):
    dissolveTiles.add((x, y, tick))

def updateDissolveTiles(tick):
    remove = []

    for x, y, t in dissolveTiles:
        count = tick - t

        if count == DISSOLVE_SPEED * 1:
            setTile(x, y, '2')
        elif count == DISSOLVE_SPEED * 2:
            setTile(x, y, '3')
        elif count == DISSOLVE_SPEED * 3:
            setTile(x, y, ' ')
            remove.append((x, y, t))

    for elem in remove:
        dissolveTiles.remove(elem)


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
        self.coyoteCount = 0

        self.dead = False

    def getSprite(self):
        if self.ydir == 0:
            if self.xdir == 0:
                return TILES['Pi']
            else:
                if int(time.time() * 1000) % 500 < 100:
                    sprite = TILES['P1']
                elif 100 <= int(time.time() * 1000) % 500 < 200:
                    sprite = TILES['P2']
                elif 200 <= int(time.time() * 1000) % 500 < 300:
                    sprite = TILES['P3']
                elif 300 <= int(time.time() * 1000) % 500 < 400:
                    sprite = TILES['P4']
                else:
                    sprite = TILES['P5']
                
                if self.xdir < 0:
                    sprite = pygame.transform.flip(sprite, True, False)  # Flip horizontally, not vertically

                return sprite 
           
        else:
            return TILES['P6']


    def jump(self, state):
        self.shouldJump = state

    def update(self, tick):
        if self.shouldJump:
            if self.onGround or self.coyoteCount < COYOTE_JUMP_TOLERANCE:
                self.ydir = -3
                self.shouldJump = False

        # gravity part 1
        tilex = int(self.xpos / TW + 0.5)
        tiley = int((self.ypos + TH * 0.9999) / TH)
        oldy = tiley

        self.ydir += 0.125
        self.onGround = False

        if self.ydir > MAX_GRAVITY:
            self.ydir = MAX_GRAVITY

        # update y position
        self.ypos += self.ydir

        # gravity part 2
        tilex1 = int(self.xpos / TW + 0.3)
        tilex2 = int(self.xpos / TW + 0.7)
        tiley = int((self.ypos + TH * 0.9999) / TH)

        tile1 = getTile(tilex1, tiley)
        tile2 = getTile(tilex2, tiley)
        if tile1 in FLOOR_TILES or tile2 in FLOOR_TILES:
            if tiley > oldy:
                self.ydir = 0
                self.ypos = int(self.ypos / TH) * TH
                self.onGround = True
                self.coyoteCount = 0

        # broesel away
        if self.onGround:
            if tile1 == '1':
                dissolveTile(tilex1, tiley, tick)
            if tile2 == '1':
                dissolveTile(tilex2, tiley, tick)

        #debugPrint('onground: %s' % self.onGround)

        # upper collision (head)
        if self.ydir < 0:
            tilex1 = int(self.xpos / TW + 0.3)
            tilex2 = int(self.xpos / TW + 0.7)
            tiley = int(self.ypos / TH)
            if getTile(tilex1, tiley) in OBSTACLES or getTile(tilex2, tiley) in OBSTACLES:
                self.ypos = int(self.ypos / TH + 1) * TH
                self.ydir = 0

        # update x position
        self.xpos += self.xdir

        # horizontal collision (to the right)
        if self.xdir > 0:
            tilex = int(self.xpos / TW + 0.7)
            tiley = int(self.ypos / TH + 0.5)
            if getTile(tilex, tiley) in OBSTACLES:
                self.xpos = int(self.xpos / TW) * TW + TW * 0.29
                self.xdir = 0

        # horizontal collision (to the left)
        if self.xdir < 0:
            tilex = int(self.xpos / TW + 0.3)
            tiley = int(self.ypos / TH + 0.5)
            if getTile(tilex, tiley) in OBSTACLES:
                self.xpos = int(self.xpos / TW) * TW + TW * 0.71
                self.xdir = 0

        # fall into water
        if self.ypos > len(level) * TH + 50:
            self.dead = True

        # coyote jump counter
        if not self.onGround:
            self.coyoteCount += 1

class Game():
    def __init__(self):
        self.reset()
        self.levelno = 1

    def reset(self):
        self.scrollx = 0
        self.mousepressed = False

        # find player start position
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 'P':
                    self.player = Player(x * TW, y * TH)

                    # remove the 'P' from level data
                    setTile(x, y, ' ')

        self.leftPressed = False
        self.rightPressed = False
        self.currentTile = PLACEABLE_TILES[0]

        self.levelFinished = False
        self.levelFinishCount = 0

    def drawTile(self, screen, tile, x, y):
        screen.blit(tile, (x * TW - self.scrollx, y * TH + 4))

    def drawHalfTile(self,screen,tile,x,y):
        if CURRENTCOOLDOWN < TILECOOLDOWN:
            tile.set_alpha(70)
        screen.blit(tile, (x * TW - self.scrollx + 4,y*TH + TH/2))

    def drawSprite(self, screen, tile, x, y):
        screen.blit(tile, (x - self.scrollx, y + 4))

    def playerLeft(self, state):
        self.leftPressed = state

    def playerRight(self, state):
        self.rightPressed = state

    def playerJump(self, state):
        self.player.jump(state)

    def render(self, screen, font):
        global CURRENTCOOLDOWN
        # draw sky
        screen.fill((64,128,192))

        #font.centerText(screen, 'F12 = TOGGLE SCROLL', y=10)

        # draw level
        for y in range(len(level)):
            for x in range(len(level[0])):
                tile = level[y][x]
                if tile in TILES:
                    if tile == '~':
                        if int(time.time() * 1000) % 400 < 100:
                            tile = '~'
                        if 100 <= int(time.time() * 1000) % 400 < 200:
                            tile = '~~'
                        if 200 <= int(time.time() * 1000) % 400 < 300:
                            tile = '~~~'
                        if 300 <= int(time.time() * 1000) % 400 < 400:
                            tile = '~~~~'
                        #else:
                        #    tile = '~~'
                    self.drawTile(screen, TILES[tile], x, y)

        # draw player
        self.drawSprite(screen, self.player.getSprite(), self.player.xpos, self.player.ypos)

        # draw mouse cursor
        pos = pygame.mouse.get_pos()
        if self.mousepressed:
            self.drawTile(screen, TILES['cursor_pressed'], int(pos[0]/TW + self.scrollx/TW), int(pos[1]/TH))
        else:
            self.drawTile(screen, TILES['cursor'], int(pos[0]/TW + self.scrollx/TW), int(pos[1]/TH))
        if CURRENTCOOLDOWN < TILECOOLDOWN:
            cooldownbar = (TILECOOLDOWN - CURRENTCOOLDOWN) / TILECOOLDOWN * TW
            pygame.draw.rect(screen, (255 - (CURRENTCOOLDOWN / TILECOOLDOWN * 255),
                                      (CURRENTCOOLDOWN / TILECOOLDOWN * 255) , 0),
                                      (int(pos[0]/TW + self.scrollx/TW) * TW - self.scrollx,  int(pos[1]/TH + 1) * TH + 4, cooldownbar, 2) )

        # draw incoming block
        incomingBlock = pygame.transform.scale(TILES[self.currentTile],(TW/2,TH/2))
        self.drawHalfTile(screen, incomingBlock, int(pos[0]/TW + self.scrollx/TW), int(pos[1]/TH))

        # draw congratz message
        if self.levelFinished:
            font.centerText(screen, 'LEVEL COMPLETE', y=10)

    def update(self, tick):
        if self.levelFinished:
            self.levelFinishCount += 1
            if self.levelFinishCount == 100:
                self.nextLevel()
            return

        # update level scroll
        if self.scrollx < len(level[0]) * TW - SCR_W:
            self.scrollx += SCROLL_SPEED

        # update player
        if self.leftPressed:
            self.player.xdir = -1
        else:
            if self.player.xdir < 0:
                self.player.xdir = 0

        if self.rightPressed:
            self.player.xdir = 1
        else:
            if self.player.xdir > 0:
                self.player.xdir = 0

        self.player.update(tick)

        if self.player.dead:
            # respawn (for debug)
            DEATHSOUND.play()
            self.player.ypos = -TH
            self.player.xpos = self.scrollx + 5 * TW
            self.player.ydir = 0
            self.player.dead = False

        # update level
        updateDissolveTiles(tick)

        # check for exit
        if getTile(int(self.player.xpos / TW), int(self.player.ypos / TH - 1)) == 'D':
            self.levelFinished = True

    def nextLevel(self):
        self.levelno += 1

        global level
        level = level_gen.run(self.levelno, 60 + self.levelno * 5, 11);

        self.reset()


class Application():
    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)

        self.font = BitmapFont('gfx/heimatfont.png', 8, 8, [(255, 255, 255)])

        self.clock = pygame.time.Clock()
        self.cooldown = 0

        self.tick = 0

    def controls(self):
        while True:
            e = pygame.event.poll()
            global CURRENTCOOLDOWN
            CURRENTCOOLDOWN += 1

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

                elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.game.playerLeft(True)

                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.game.playerRight(True)

                elif e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.game.playerJump(True)

            if e.type == pygame.MOUSEBUTTONDOWN:
                self.game.mousepressed = True
                pos = pygame.mouse.get_pos()
                if CURRENTCOOLDOWN > TILECOOLDOWN:
                    CURRENTCOOLDOWN = 0

                    x = int(pos[0]/TW + self.game.scrollx/TW)

                    y = int(pos[1]/TH)
                    PLACESOUND.play()
                    setTile(x, y,self.game.currentTile)
                    self.game.currentTile = random.choice(PLACEABLE_TILES)
                    # no check if we have some floors or greens there, and make the new block fitting to the others
                    if getTile(x, y + 1) == 'G':
                        setTile(x, y + 1,'F')
                    if getTile(x, y - 1) == 'G':
                        setTile(x, y, 'F')
                    if getTile(x, y - 1) == 'F':
                        setTile(x, y, 'F')
                else:
                    DENYSOUND.play()

            if e.type == pygame.MOUSEBUTTONUP:
                self.game.mousepressed = False


            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.game.playerLeft(False)

                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.game.playerRight(False)

                elif e.key == pygame.K_UP or e.key == pygame.K_w:
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

            self.game.update(self.tick)

            self.clock.tick(60)
            self.tick += 1

        pygame.quit()

app = Application()
app.run()

