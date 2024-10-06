import pygame
import pygame._sdl2.controller
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

TILECOOLDOWN=100
CURRENTCOOLDOWN=150

SCROLL_SPEED = 0.5
PLAYER_SPEED = 1.25

DISSOLVE_SPEED = 6

level_gen = Generator()

pygame.init()
pygame.mouse.set_visible(False)

pygame.mixer.init()
pygame.mixer.music.load('sfx/NichtEinFlohWalzerWeitEntfernt.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

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
         'v': pygame.image.load('gfx/trapp_g.png'),
         'L': pygame.image.load('gfx/laser_cannon.png'),
         'l': pygame.image.load('gfx/laser_beam.png'),

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


level = None


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
    def __init__(self, x, y,lifes):
        self.xpos = x
        self.ypos = y

        self.xdir = 0
        self.ydir = 0

        self.onGround = False
        self.shouldJump = False
        self.coyoteCount = 0

        self.dead = False
        self.lifes = lifes

    def getSprite(self):
        if self.onGround == True:  # self.ydir == 0:
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
            if self.xdir < 0:
                return pygame.transform.flip(TILES['P6'],True, False)
            else:
                return TILES['P6']


    def jump(self, state):
        self.shouldJump = state

    def update(self, tick, scrollx):
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
        self.xpos += self.xdir * PLAYER_SPEED

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
            self.kill()

        # scrolled out of the screen
        if self.xpos - scrollx  + TW< 0:
            self.kill()

        # coyote jump counter
        if not self.onGround:
            self.coyoteCount += 1

        # collide with trap
        tilex = int(self.xpos / TW + 0.5)
        tiley = int(self.ypos / TH + 0.5)
        if getTile(tilex, tiley) == 'v':
            self.kill()

        # collide with laser
        tilex = int(self.xpos / TW + 0.3)
        tiley = int(self.ypos / TH + 0.5)
        if getTile(tilex, tiley) == 'l':
            self.kill()

    def kill(self):
        self.dead = True
        DEATHSOUND.play()
        self.ypos = -TH * 2

class Game():
    def __init__(self):
        global level
        level = level_gen.run(1, 60, 11)

        self.lifes = 3
        self.reset()
        self.levelno = 1

    def reset(self):
        self.scrollx = 0
        self.mousepressed = False

        self.currentMousePos = (-1,-1)

        # find player start position
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 'P':
                    self.player = Player(x * TW, y * TH, self.lifes)
                    # remove the 'P' from level data
                    setTile(x, y, ' ')

        # find door position
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 'D':
                    self.door = (x * TW, y * TH) # TODO if no door is found


        self.leftPressed = False
        self.rightPressed = False
        self.currentTile = PLACEABLE_TILES[0]

        self.levelFinished = False
        self.levelFinishCount = 0

        self.respawnMode = False
        self.gameover = False


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

    def click(self, state):
        global CURRENTCOOLDOWN
        self.mousepressed = state

        x = self.currentMouseTileX
        y = self.currentMouseTileY

        tile = getTile(x, y)

        if tile == ' ' or tile == 'l':
            # make sure end gate is not overdrawn
            if getTile(x, y-1) == 'D' or getTile(x-1, y) == 'D' or getTile(x-1, y-1) == 'D' or tile == 'L':
                DENYSOUND.play()
                return

            if CURRENTCOOLDOWN > TILECOOLDOWN or self.respawnMode:
                CURRENTCOOLDOWN = 0

                if self.respawnMode:
                    if y == 0 or tile == 'l':
                        DENYSOUND.play()
                        return

                setTile(x, y, self.currentTile)

                if tile == 'l' and y < 11: # last tile was a laser beam
                    for ly in range(y + 1, 11):
                        ltile = getTile(x, ly)
                        if ltile == 'l':
                            setTile(x, ly, ' ')
                        else:
                            break

                self.currentTile = random.choice(PLACEABLE_TILES)

                # respawn player if dead
                if self.respawnMode:
                    self.player = Player(x * TW, (y - 1) * TH,self.lifes)
                    self.respawnMode = False

                PLACESOUND.play()
            else:
                DENYSOUND.play()
        else:
            DENYSOUND.play()

        if self.respawnMode:
            self.player = Player(x * TW, (y - 1) * TH, self.lifes)
            self.respawnMode = False

        # TODO this is probably deprecated
        # no check if we have some floors or greens there, and make the new block fitting to the others
        #if getTile(x, y + 1) == 'G':
        #    setTile(x, y + 1,'F')
        #if getTile(x, y - 1) == 'G':
        #    setTile(x, y, 'F')
        #if getTile(x, y - 1) == 'F':
        #    setTile(x, y, 'F')

    def render(self, screen, font):
        global CURRENTCOOLDOWN
        # draw sky
        screen.fill((64,128,192))

        #font.centerText(screen, 'F12 = TOGGLE SCROLL', y=10)
        debugPrint(self.lifes)
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

        for x in range (len(level[0])):
            tile = level[len(level) - 1][x]
            tileabove = level[len(level) - 2][x]
            if tile == '~' and tileabove == 'l' :
                self.drawTile(screen, TILES['l'], x, len(level) - 1)

        # draw player
        self.drawSprite(screen, self.player.getSprite(), self.player.xpos, self.player.ypos)

        # draw mouse cursor
        pos = pygame.mouse.get_pos()

        if pos != self.currentMousePos:
            self.currentMousePos = pos
            self.currentMouseTileX = int(pos[0] / TW + self.scrollx / TW)
            self.currentMouseTileY = int(pos[1] / TH)

            if self.respawnMode:
                if self.currentMouseTileX * TW - self.scrollx > SCR_W / 3:
                    self.currentMouseTileX = int((self.scrollx + SCR_W / 3) / TW)

        if not self.gameover:
            if self.mousepressed:
                self.drawTile(screen, TILES['cursor_pressed'], self.currentMouseTileX, self.currentMouseTileY)
            else:
                self.drawTile(screen, TILES['cursor'], self.currentMouseTileX, self.currentMouseTileY)

        # draw cooldown bar
        if not self.respawnMode and not self.gameover:
            if CURRENTCOOLDOWN < TILECOOLDOWN:
                cooldownbar = (TILECOOLDOWN - CURRENTCOOLDOWN) / TILECOOLDOWN * TW
                pygame.draw.rect(screen, (255 - (CURRENTCOOLDOWN / TILECOOLDOWN * 255),
                                        (CURRENTCOOLDOWN / TILECOOLDOWN * 255) , 0),
                                        (self.currentMouseTileX * TW - self.scrollx,
                                        (self.currentMouseTileY + 1) * TH + 4, cooldownbar, 2) )

        # draw incoming block
        if not self.gameover:
            incomingBlock = pygame.transform.scale(TILES[self.currentTile],(TW/2,TH/2))
            self.drawHalfTile(screen, incomingBlock, self.currentMouseTileX, self.currentMouseTileY)

        # draw congratz message
        if self.levelFinished:
            font.centerText(screen, 'LEVEL COMPLETE', y=10)

        # draw respawn message
        if self.respawnMode:
            font.centerText(screen, 'YOU DIED', y=10)
            font.centerText(screen, 'CLICK TO RESPAWN', y=12)

        # draw game over message
        if self.gameover:
            font.centerText(screen,'GAME OVER', y=10)
            font.centerText(screen,'PRESS SPACE OR BUTTON', y=12)

    def update(self, tick):
        global CURRENTCOOLDOWN
        CURRENTCOOLDOWN += 1

        if self.respawnMode:
            return

        if self.lifes == 0:
            self.gameover = True
            return

        if self.levelFinished:
            self.levelFinishCount += 1
            if self.levelFinishCount == 100:
                self.nextLevel()
            return

        if self.player.dead and not self.gameover:
            self.lifes = self.lifes - 1
            if self.lifes > 0:
                self.respawnMode = True
                self.currentTile = 'O'

        # update level scroll
        if self.scrollx < min(len(level[0]) * TW - SCR_W, self.door[0]- SCR_W/2):
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

        self.player.update(tick, self.scrollx)

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

        self.shouldRestartGame = False

        # init joysticks
        pygame.joystick.init()
        pygame._sdl2.controller.init()

        self.controllers = []

        print('found %s joysticks' % pygame.joystick.get_count())
        for i in range(pygame.joystick.get_count()):
            iscontroller = pygame._sdl2.controller.is_controller(i)
            print('joystick %i is game controller: %s' % (i, iscontroller))
            joy = pygame.joystick.Joystick(i)
            self.controllers.append(pygame._sdl2.controller.Controller.from_joystick(joy))

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

                elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.game.playerLeft(True)

                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.game.playerRight(True)

                elif e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.game.playerJump(True)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.game.click(True)

            elif e.type == pygame.MOUSEBUTTONUP:
                self.game.click(False)

                if self.game.gameover:
                    self.shouldRestartGame = True
                    return

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.game.playerLeft(False)

                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.game.playerRight(False)

                elif e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.game.playerJump(False)

                elif e.key == pygame.K_SPACE:
                    if self.game.gameover:
                        self.shouldRestartGame = True
                        return

            elif e.type == pygame.CONTROLLERBUTTONDOWN:
                if e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    self.game.playerLeft(True)
                if e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.game.playerRight(True)
                if e.button == pygame.CONTROLLER_BUTTON_A or e.button == pygame.CONTROLLER_BUTTON_B:
                    self.game.playerJump(True)

            elif e.type == pygame.CONTROLLERBUTTONUP:
                if e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    self.game.playerLeft(False)
                if e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.game.playerRight(False)
                if e.button == pygame.CONTROLLER_BUTTON_A or e.button == pygame.CONTROLLER_BUTTON_B:
                    self.game.playerJump(False)

                if self.game.gameover:
                    self.shouldRestartGame = True
                    return

            elif e.type == pygame.CONTROLLERAXISMOTION:
                if e.axis == pygame.CONTROLLER_AXIS_LEFTX:
                    value = max(-1, e.value / 32767)
                    if value > 0.75:
                        self.game.playerRight(True)
                    elif value < -0.75:
                        self.game.playerLeft(True)
                    else:
                        self.game.playerLeft(False)
                        self.game.playerRight(False)

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

            if self.shouldRestartGame:
                self.game = Game()
                self.shouldRestartGame = False
                print(self.game.player)

        pygame.quit()

app = Application()
app.run()

