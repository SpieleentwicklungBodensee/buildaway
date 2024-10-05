from perlin_noise import PerlinNoise

class GeneratorData(object):
    def __init__(self, level, width, height):
        self.level = level + 473284
        self.width = width
        self.height = height
        self.grid = [[' ' for x in range(width)] for y in range(height)]

class Generator(object):
    def __init__(self):

        self.noise = PerlinNoise(octaves=10, seed=1)
        pass

    def run(self, level, width, height):
        if level == -1:
            return  ['          P                                                             ',
                 '                                                                        ',
                 '                                                          ##            ',
                 'GGGGGGGGGGGG                                                            ',
                 'FFFF                      GG                                            ',
                 'FFFF                      FF                  ###                     GG',
                 'FFFF                     GFFG                                         FF',
                 'FFFFG                    FFFF         ####                            FF',
                 'FFFFF         GG         FFFFG                                        FF',
                 'FFFFF      GGGFFG        FFFFF                                      GGFF',
                 'FFFFF~~~~~~FFFFFF~~~~~~~~FFFFF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FFFF',
                 ]

        data = GeneratorData(level, width, height)

        self.make_water(data)

        self.make_floors(data)

        self.make_it_green(data)

        self.make_player(data)

        # make each line as string
        for y in range(data.height):
            data.grid[y] = ''.join(data.grid[y])

        return data.grid

    def change_block(self, data, x, y, element):
        try:
            data.grid[y][x] = element
        except IndexError:
            pass

    def make_floors(self, data):
        ratio =   (data.width / data.height)

        # lower generation
        threshold = 4
        for y in range(data.height):
            for x in range(data.width):
                xdim = x / 80
                ydim = y
                cur = self.noise([xdim, ydim, data.level/10]) * 20
                if cur > threshold:
                    #print (cur)
                    #if data[y][x] != '~':
                    self.change_block(data, x, y+5, 'F')

        # fillup blocks from below
        for x in range(data.width):
            lowest = -1
            for y in reversed(range(data.height)):
                if data.grid[y][x] in ['F', 'G']:
                    lowest = y
                    break

            if lowest > -1:
                for y in range(lowest, data.height):
                    self.change_block(data, x, y, 'F')

        # make more platforms above
        threshold = 5
        for y in range(data.height):
            for x in range(data.width):
                xdim = x / 80  + 20
                ydim = y / 10
                cur = self.noise([xdim, ydim, data.level/10+1234]) * 20
                if cur > threshold and y < 7:
                    #print (cur)
                    #if data[y][x] != '~':
                    self.change_block(data, x, y, 'F')

    def make_water(self, data):
        for x in range(data.width):
            data.grid[-1][x] = '~'

    def make_it_green(self, data,):
        for x in range(data.width):
            last = ' '
            for y in range(data.height):
                cur = data.grid[y][x]

                if cur == 'F' and last == ' ':
                    self.change_block(data, x, y, 'G')

                last = cur

    def make_player(self, data,):
        for x in range(data.width):
            if x > 5:
                last = ''
                for y in range(data.height):
                    cur = data.grid[y][x]

                    if cur == 'G' and last == ' ':
                        self.change_block(data, x, y-1, 'P')
                        return
                    last = cur
