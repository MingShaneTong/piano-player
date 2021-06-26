# creates a file dialog
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from mido import MidiFile
from os import path

BLACK_STATIONARY = 2.18683
WHITE_STATIONARY = 1.33825

FPS = 24

# number of seconds to process of the file
# make high number if the whole file is to be processed
EARLY_END = 40


class Piano:
    """
    Creates a piano object
    """
    A = 65
    C = 67
    F = 70

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
        # create the key objects
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


class Key:
    """
    Contains the key on the piano
    """

    def __init__(self, midi, note, is_white):
        self.midi = midi
        self.note = note
        self.is_white = is_white
        self.pressed = False
        self.frames = set()

    def __str__(self):
        return str(self.midi)

    def press(self):
        self.pressed = True

    def unpress(self):
        self.pressed = False

    def draw(self, frm):
        """
        Changes the key on the blender model
        :param frm: the number of the frame to change the key on
        :return:
        """
        adjust = self.adjust()
        obj = bpy.data.objects["key" + str(self.midi)]
        if self.pressed:
            obj.location.z -= adjust
        else:
            obj.location.z += adjust

        # insert frame for object
        # makes sure animation is not happening at the same time as another action
        insert_frm = frm
        while insert_frm in self.frames:
            insert_frm += 2
        obj.keyframe_insert(data_path="location", frame=insert_frm)
        self.frames.add(insert_frm)


class WhiteKey(Key):
    """
    Represents the white key on the piano
    """
    adj = 0.9

    def __init__(self, midi, note):
        super(WhiteKey, self).__init__(midi, note, True)

    def __str__(self):
        return super(WhiteKey, self).__str__() + "W"

    def adjust(self):
        return self.adj


class BlackKey(Key):
    """
    Represents the black key on the piano
    """
    adj = 0.75

    def __init__(self, midi, note):
        super().__init__(midi, note, False)

    def __str__(self):
        return super(BlackKey, self).__str__() + "B"

    def adjust(self):
        return self.adj


def play_piano(mid, piano):
    """
    Animates the frames of the blender piano playing the song
    :param mid: The Midi file of the song
    :param piano:   The piano object with the data about the state of the song
    :return:
    """
    time = 0

    # process the midi file
    for msg in mid:
        if not msg.is_meta and (msg.type == 'note_on' or msg.type == 'note_off'):
            key = piano.keys[msg.note]
            frm = int(time * FPS)

            # press or unpress key
            if msg.type == 'note_off' or msg.velocity <= 0:
                key.unpress()
            else:
                key.press()
            key.draw(frm)

            # check if the piano should stop
            time += msg.time
            if time >= EARLY_END:
                break

    # switch to constant interpolation
    for obj in bpy.data.collections['Keys'].all_objects:
        fcurves = obj.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'CONSTANT'


def reset_piano():
    """
    Puts all the piano keys to the correct height
    :return:
    """
    for obj in bpy.data.collections['Black'].all_objects:
        obj.location.z = BLACK_STATIONARY
        obj.keyframe_insert(data_path="location", frame=0)
    for obj in bpy.data.collections['White'].all_objects:
        obj.location.z = WHITE_STATIONARY
        obj.keyframe_insert(data_path="location", frame=0)


def main(file):
    """
    Creates the piano and plays the file
    :param file: the file path of the audio file
    :return:
    """
    if not path.exists(file):
        print("File does not exist")
        return

    mid = MidiFile(file, clip=True)
    p = Piano()
    play_piano(mid, p)


class OpenFileBrowser(Operator, ImportHelper):
    """
    Opens a file browser in blender and selects an MIDI file
    the file path is then used for animation
    """
    bl_idname = "test.open_filebrowser"
    bl_label = "Select an audio file"

    filter_glob: StringProperty(default='*.mid')

    def execute(self, context):
        main(self.filepath)
        return {'FINISHED'}


if __name__ == "__main__":
    reset_piano()
    bpy.utils.register_class(OpenFileBrowser)
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')
