from perlin_noise import PerlinNoise

class GeneratorData(object):
    def __init__(self, level, width, height):
        self.level = level
        self.width = width
        self.height = height
        self.seed = 29153 + level * 3 - 3 #473284
        self.grid = [[' ' for x in range(width)] for y in range(height)]
        self.doorx = 0

class Generator(object):
    def __init__(self):

        self.noise = PerlinNoise(octaves=10, seed=1)
        pass

    def run(self, level, width, height):
        if level == -1:
            return  ['          P                                                             ',
                 '                                                                        ',
                 '                                                          ##            ',
                 'GGGGGGGGGGGG                                                         D  ',
                 'FFFF                      GvG                                           ',
                 'FFFF                      FFF                 ###                    GGG',
                 'FFFF                     GFFF                                        FFF',
                 'FFFFG                    FFFF         ####                           FFF',
                 'FFFFF         GG         FFFFG                                       FFF',
                 'FFFFF      GGGFFG        FFFFF                                      GGFF',
                 'FFFFF~~~~~~FFFFFF~~~~~~~~FFFFF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FFFF',
                 ]

        data = GeneratorData(level, width, height)

        self.make_water(data)

        self.make_floors(data)

        self.make_it_green(data)

        self.make_rocks(data)

        self.make_walls(data)

        self.make_player(data)

        self.make_door(data)

        self.make_traps(data)

        self.make_laser(data)

        # make each line as string
        for y in range(data.height):
            data.grid[y] = ''.join(data.grid[y])

        return data.grid

    def change_block(self, data, x, y, element):
        try:
            data.grid[y][x] = element
        except IndexError:
            pass

    def get_block(self, data, x, y):
        try:
            return data.grid[y][x]
        except IndexError:
            return ''


    def make_floors(self, data):
        ratio =   (data.width / data.height)

        # lower generation
        threshold = 4
        for y in range(data.height):
            for x in range(data.width):
                xdim = x / 80
                ydim = y
                cur = self.noise([xdim, ydim, (data.level + data.seed)/10]) * 20
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
                cur = self.noise([xdim, ydim, (data.level + data.seed)/10+1234]) * 20
                if cur > threshold and y < 7:
                    #print (cur)
                    #if data[y][x] != '~':
                    self.change_block(data, x, y, 'F')

    def make_water(self, data):
        for x in range(data.width):
            data.grid[-1][x] = '~'

    def make_rocks(self, data,):
        for x in range(data.width):
            for y in range(data.height):
                xdim = x / 80
                ydim = y
                val = self.noise([xdim, ydim, (data.level + data.seed)/10+38291]) * 20

                if val > 1:
                    cur = data.grid[y][x]
                    above = self.get_block(data, x, y - 1)
                    below = self.get_block(data, x, y + 1)

                    if cur == 'G' and above == ' ' and below == ' ':
                        self.change_block(data, x, y, 'O')
                        if val > 3:
                            self.change_block(data, x, y, '1')
                        #if val > 3:
                        #    self.change_block(data, x, y, '2')
                        #if val > 4:
                        #    self.change_block(data, x, y, '2')

    def make_walls(self, data,):
        for x in range(data.width):
            for y in range(data.height):
                xdim = x / 180
                ydim = y
                val = self.noise([xdim, ydim, (data.level + data.seed)/10+1204]) * 20

                if val > 1:
                    cur = data.grid[y][x]
                    #above = self.get_block(data, x, y - 1)
                    #below = self.get_block(data, x, y + 1)

                    if cur == 'F': # and above == ' ' and below == ' ':
                        self.change_block(data, x, y, '#')

    def make_traps(self, data,):
        for x in range(data.width):
            last = ' '
            for y in range(data.height):
                xdim = x / 20
                ydim = y
                val = self.noise([xdim, ydim, (data.level + data.seed)/10+15590]) * 20
                cur = data.grid[y][x]
                door1 = self.get_block(data, x-1, y-2)
                door2 = self.get_block(data, x, y-2)
                
                if val > 3:
                    if cur == 'G' and last == ' ' and door1 != 'D' and door2 != 'D':
                        self.change_block(data, x, y, 'v')

                last = cur


    def make_laser(self, data):
        for x in range(data.width):

            xdim = x / 20
            ydim = 0
            val = self.noise([xdim, ydim, (data.level + data.seed)/10+93356]) * 20
            
            cur = self.get_block(data, x, 0)

            #if not self.has_element_on_column(data, x, 'P') and cur == ' ' and val > 1 and x > data.doorx + 2 and x < data.doorx - 2:
            nodoor =  not ( (x >= data.doorx - 1) and (x <= data.doorx + 2) )
            if cur == ' ' and not self.has_element_on_column(data, x, 'P') and nodoor and val > 6:
                
                self.change_block(data, x, 0, 'L')
                for y in range(1, data.height):
                    cury = self.get_block(data, x, y)
                    if cury == ' ':
                        self.change_block(data, x, y, 'l')
                    else:
                        break


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

    def is_free_to_top(self, data, x, y):
        for cury in range (y):
            if data.grid[cury][x] != ' ':
                return False
        return True
    
    def has_element_on_column(self, data, x, element):
        for y in range(data.height):
            cur = self.get_block(data, x, y)
            if cur == element:
                return True

        return False

    def make_door(self, data,):
        for x in reversed(range(data.width)):
            if x < data.width - 4:
                last = ''
                for y in range(data.height):
                    if y > 1:
                        cur = data.grid[y][x]

                        if cur == 'G' and last == ' ':
                            f1 = data.grid[y][x-1]
                            if f1 == 'G' and self.is_free_to_top(data, x, y-1) and self.is_free_to_top(data, x-1, y-1):
                                self.change_block(data, x-1, y-2, 'D')
                                data.doorx = x-1
                                return
                        last = cur
