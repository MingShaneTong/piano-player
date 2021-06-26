from abc import ABC, abstractmethod
import pygame

WHITE = (255, 255, 255)
SEMIWHITE = (200, 200, 200)
SEMIBLACK = (100, 100, 100)
BLACK = (0, 0, 0)


class Piano:
    """
    Creates a piano object
    """
    A = 65
    C = 67
    F = 70

    # the margin around the piano
    MARGIN = 10
    # smallest size for 1cm for a key
    MIN_SCALE = 8

    def __init__(self):
        """
        Creates the piano and its keys
        """
        self.keys = {}
        self.white_keys = []
        self.black_keys = []

        G = Piano.F + 1
        white = Piano.get_white_midi()
        note = Piano.A
        octave = 0
        for i in range(21, 109):
            if i in white:
                # white key
                key = WhiteKey(i, chr(note) + "_" + str(octave))
                self.keys[i] = key
                self.white_keys.append(key)

                # increment char and sec if needed
                note += 1
                if note == Piano.C:
                    octave += 1
                elif note == G:
                    note = Piano.A
            else:
                # black key, # key
                key = BlackKey(i, chr(note) + "s_" + str(octave))
                self.keys[i] = key
                self.black_keys.append(key)

    @staticmethod
    def get_white_midi():
        """
        Finds all the midi numbers for the white keys
        :return:
        """
        return set(range(21, 109)) - Piano.get_black_midi()

    @staticmethod
    def get_black_midi():
        """
        Finds all the midi numbers for the black keys
        :return:
        """
        black_midi = {22}
        curr = 25
        for i in range(7):
            black_midi.add(curr)
            black_midi.add(curr + 2)
            black_midi.add(curr + 5)
            black_midi.add(curr + 7)
            black_midi.add(curr + 9)
            curr += 12
        return black_midi

    def get_dimension(self, display):
        w, h = display.get_size()

        # find the scale of the piano
        board_width = w - Piano.MARGIN * 2
        board_height = h - Piano.MARGIN * 2
        boardw_cm = len(self.white_keys) * WhiteKey.WHITE_HEIGHT * Key.KEY_WIDTH_RATIO
        boardh_cm = WhiteKey.WHITE_HEIGHT
        scale = min(board_width / boardw_cm, board_height / boardh_cm)
        scale = max(scale, Piano.MIN_SCALE)

        # allocate an x and y to each tile
        dimensions = {}
        cx = Piano.MARGIN
        cy = Piano.MARGIN
        white_height = scale * WhiteKey.WHITE_HEIGHT
        white_width = white_height * Key.KEY_WIDTH_RATIO
        black_height = scale * BlackKey.BLACK_HEIGHT
        black_width = black_height * Key.KEY_WIDTH_RATIO
        black_shift = (2 * white_width - black_width) / 2

        for i in range(21, 109):
            key = self.keys[i]
            if isinstance(key, WhiteKey):
                # use current key
                dimensions[key] = pygame.Rect(cx, cy, white_width, white_height)
                cx += white_width
                pass
            else:
                # black key draw halfway between white keys
                dimensions[key] = pygame.Rect(cx + black_shift, cy, black_width, black_height)
                pass
        return dimensions

    def draw(self, display):
        """
        Draws the piano on the game display
        :param display: display to draw into
        :return:
        """
        dimensions = self.get_dimension(display)
        # draw keys onto game display
        for key in self.white_keys:
            key.draw(display, dimensions[key])
        for key in self.black_keys:
            key.draw(display, dimensions[key])

    def draw_black(self, display):
        """
        Draws the piano on the game display
        :param display: display to draw into
        :return:
        """
        dimensions = self.get_dimension(display)
        # draw keys onto game display
        for key in self.white_keys:
            key.draw(display, dimensions[key])
        for key in self.black_keys:
            key.draw(display, dimensions[key])


class Key(ABC):
    """
    Contains the key on the piano
    """
    KEY_WIDTH_RATIO = 0.154

    def __init__(self, midi, note, is_white):
        self.midi = midi
        self.note = note
        self.is_white = is_white
        self.pressed = False

    def __str__(self):
        return str(self.midi)

    def press(self):
        self.pressed = True

    def unpress(self):
        self.pressed = False

    @abstractmethod
    def draw(self, game_display, dimension):
        """
        Draws a key onto the game_display
        :param game_display:
        :param dimension: size and place to draw the key
        :return:
        """
        pass


class WhiteKey(Key):
    WHITE_HEIGHT = 15  # height of key

    def __init__(self, midi, note):
        super(WhiteKey, self).__init__(midi, note, True)

    def __str__(self):
        return super(WhiteKey, self).__str__() + "W"

    def draw(self, game_display, dimension):
        if self.pressed:
            pygame.draw.rect(game_display, SEMIWHITE, dimension)
        pygame.draw.rect(game_display, BLACK, dimension, 1)


class BlackKey(Key):
    BLACK_HEIGHT = 9  # height of key

    def __init__(self, midi, note):
        super().__init__(midi, note, False)

    def __str__(self):
        return super(BlackKey, self).__str__() + "B"

    def draw(self, game_display, dimension):
        if self.pressed:
            pygame.draw.rect(game_display, SEMIBLACK, dimension)
        else:
            pygame.draw.rect(game_display, BLACK, dimension)
