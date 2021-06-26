from keys import *
from mido import MidiFile
from os import path
import sys
import pygame
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

display_width = 1200
display_height = 200


def main(file):
    """
    Creates the piano and plays the file
    :param file:
    :return:
    """
    if not path.exists(file):
        print("File does not exist")
        return

    mid = MidiFile(file, clip=True)

    # initialise GUI and create piano
    pygame.init()
    game_display = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)
    pygame.display.set_caption("Piano Player")
    p = Piano()

    # play the piano
    update_display(game_display, p)
    pygame.mixer.music.load(file)
    status = play_piano(game_display, mid, p)
    if not status:
        pygame.quit()
        quit()

    # wait until user exits the screen
    update_display(game_display, p)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


def play_piano(display, mid, piano):
    pygame.mixer.music.play()

    for msg in mid:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        if not msg.is_meta:
            if msg.type == 'note_on' or msg.type == 'note_off':
                print(msg)
                key = piano.keys[msg.note]
                # press or unpress key
                key.press()
                if msg.type == 'note_off' or msg.velocity <= 0:
                    key.unpress()

                # display update
                time.sleep(msg.time)
                update_display(display, piano)

    return True


def update_display(display, piano):
    """
    Update the pygame display with the piano
    :param display:
    :param piano:
    :return:
    """
    display.fill(WHITE)
    piano.draw(display)
    pygame.display.update()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please enter 1 argument for the midi to be played")
