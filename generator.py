import perlin_noise

class Generator(object):
    def __init__(self):
        pass

    def run(self, level, width, height):
        return  ['                                                                        ',
                 '                                                                        ',
                 '                                                          ##            ',
                 'GG                                                                      ',
                 'FF           OOOOOO       GG                                            ',
                 'FF       OOO              FF                  ###                     GG',
                 'FF                       GFFG                                         FF',
                 'FFG                      FFFF         ####                            FF',
                 'FFF           GG         FFFFG                                        FF',
                 'FFF        GGGFFG        FFFFF                                      GGFF',
                 'FFF~~~~~~~~FFFFFF~~~~~~~~FFFFF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FFFF',
                 ]