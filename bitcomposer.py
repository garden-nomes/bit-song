from isobar.pattern import Pattern
from isobar.key import Key
from isobar.scale import Scale
from isobar.util import miditoname
import re
import sys


def note_to_lilypond(note):
    '''Convert a note to lilpond notation (e.g. c'4)
    '''
    # split a note name like 'C4' into ['C', '4']
    match = re.match(
            r'([a-z]+)([0-9]+)',
            miditoname(note['note']).replace('#', 'is').replace('b', 'es'),
            re.I
    )

    if match:
        ret = match.groups()[0]
        octave_num = int(match.groups()[1]) - 4;
        if octave_num > 0:
            ret += '\'' * octave_num
        else:
            ret += ',' * (octave_num * -1)

        ret += str(int(4.0 / note['dur']))
        return ret
    else:
        return ''


class BitFeeder(object):
    '''Feed it strings, and it will pop out a string of bits from the utf-8
    encoding of that string.

    Supports iterator interface
    '''

    def __init__(self, string=None):
        self._ba = bytearray()
        self._current_byte = b''
        if string: self.feed(string)

    def __iter__(self):
        return self

    def next(self):
        if not self._current_byte:
            self._load_next_byte()

        bit = self._current_byte[0]
        self._current_byte = self._current_byte[1:]

        return bit

    def feed(self, string):
        self._ba += bytearray(string)
        if self._current_byte == b'':
            self._load_next_byte()

    def _load_next_byte(self):
        try:
            self._current_byte = format(self._ba[0], '08b')
            self._ba = self._ba[1:]
        except IndexError:
            raise StopIteration


class BitComposer(Pattern):
    '''Composes music based on the bitwise representation of a string
    '''

    def __init__(self, string=None, key=None):
        self._feeder = BitFeeder(string)
        self._rhythm = []

        # generate key/scale range
        tonic = self._get_int(3)
        scale = self._get_int(4)
        self._key = Key(tonic, Scale.all()[scale])
        self._octave = len(self._key.scale.semitones)
        self._lowerbound = self._octave * 4
        self._upperbound = self._octave * 8
        self._key_index = self._octave * 6

        print str(self._key)

    def next(self):
        '''Compute next note from the string
        '''

        try:
            if not self._rhythm:
                # compute the next measure's rhythm
                sys.stdout.write('\n')
                self._build_rhythm()

            # shift the key index by a 4-bit signed integer
            self._key_index += self._get_int(4, True)

            # clamp key index to predefined range by moving up/down octave
            if self._key_index < self._lowerbound:
                self._key_index += self._octave
            if self._key_index > self._upperbound:
                self._key_index -= self._octave

            note = {
                'note': self._key[self._key_index],
                'dur':  self._rhythm[0],
                'amp': 127
            }

            sys.stdout.write(note_to_lilypond(note) + ' ')
            self._rhythm = self._rhythm[1:]

        except StopIteration:
            # uncomment in order to sustain program after it runs out of data
            # note = {
                # 'note': 0,
                # 'dur': 1,
                # 'amp': 0
            # }
            raise StopIteration
        return note

    def __iter__(self):
        return self

    def feed(self, string):
        self._feeder.feed(string)

    def _build_rhythm(self):
        '''Wrapper for _build_rhythm_recurse.
        '''
        self._rhythm = []
        self._build_rhythm_recurse(1)
        return self._rhythm

    def _build_rhythm_recurse(self, i):
        '''Build the rhythmic pattern for the next measure by recursively
        subdividing based on bit feeder input, up to 1/16th notes.
        '''
        if self._feeder.next() == '1' and i < 16:
            self._build_rhythm_recurse(i * 2)
            self._build_rhythm_recurse(i * 2)
        else:
            self._rhythm.append(4.0 / i)

    def _get_int(self, bits, signed=False):
        '''Return a signed or unsigned integer of <bits> length from the bit
        feeder.
        '''
        chunk = [self._feeder.next() for i in range(bits)]
        neg = 1
        if signed:
            if chunk[0]: neg = -1
            chunk = chunk[1:]

        val = int(''.join(chunk), 2)
        val *= neg
        return val