import pygame

from bitmapfont import BitmapFont


SCR_W = 320
SCR_H = 180

TW = 16
TH = 16



class Game():
    def __init__(self):
        pass

    def render(self, screen, font):
        screen.fill((40,60,80))
        font.centerText(screen, 'HELLO WORLD', y=5)

    def update(self):
        pass


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

