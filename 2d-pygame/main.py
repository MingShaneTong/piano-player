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

    # convert msgs into list
    msgs = []
    for msg in mid:
        msgs.append(msg)

    # play the piano
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    status = play_piano(game_display, msgs, p)
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


def play_piano(display, msgs, piano):
    # main loop
    end = False
    index = 0
    while not end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        # press on the key
        pressed = []
        holdtime = 0
        press_end = False
        while not press_end:
            if index >= len(msgs):
                end = True
                press_end = True
            else:
                msg = msgs[index]
                if not msg.is_meta and msg.type == 'note_on':
                    pressed.append(piano.keys[msg.note])
                    if msg.time > 0:
                        holdtime = msg.time
                        press_end = True
                index += 1

        # hold the keys then release
        press(pressed)
        update_display(display, piano)
        time.sleep(holdtime)
        unpress(pressed)
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


def press(keys):
    """
    Unpress the keys
    :param keys:
    :return:
    """
    for key in keys:
        key.press()


def unpress(keys):
    """
    Unpress the keys
    :param keys:
    :return:
    """
    for key in keys:
        key.unpress()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please enter 1 argument for the midi to be played")
