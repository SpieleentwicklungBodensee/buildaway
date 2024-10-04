import perlin_noise

class Generator(object):
    def __init__(self):
        pass

    def run(self, level, width, height):
        return  ['                                                                        ',
                 '                                                                        ',
                 '          P                                               ##            ',
                 'GGGGGGGGGGG                                                             ',
                 'FFFF                      GG                                            ',
                 'FFFF                      FF                  ###                     GG',
                 'FFFF                     GFFG                                         FF',
                 'FFFFG                    FFFF         ####                            FF',
                 'FFFFF         GG         FFFFG                                        FF',
                 'FFFFF      GGGFFG        FFFFF                                      GGFF',
                 'FFFFF~~~~~~FFFFFF~~~~~~~~FFFFF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FFFF',
                 ]