#!/usr/bin/env python


import sys
from feeders import BitFeeder
from isobar.note import Note
from isobar.scale import Scale
from isobar.key import Key
from isobar.pattern.core import Pattern


class BitComposer(Pattern):
    '''Composes music based on the bitwise representation of a string
    '''

    def __init__(self, string=None, key=None):
        self._feeder = BitFeeder(string)
        self.rhythm = []

        # generate key/scale range
        tonic = self._get_int(4) % 12
        scale = self._get_int(5) % len(Scale.all())
        self.key = Key(tonic, Scale.all()[scale])
        self.octave = len(self.key.scale.semitones)
        self.lowerbound = self.octave * 3
        self.upperbound = self.octave * 8
        self.key_index = self.octave * 5

    def __iter__(self):
        return self

    def next(self):
        '''Compute next note from the string
        '''

        if not self.rhythm:
            # compute the next measure's rhythm
            self._build_rhythm()

        # get the length of the next note
        length = 4.0 / self.rhythm[0]
        self.rhythm = self.rhythm[1:]

        # shift the key index by a 4-bit signed integer
        self.key_index += self._get_int(4, True)

        # clamp key index to predefined range by moving up/down octave
        if self.key_index < self.lowerbound:
            self.key_index += self.octave
        if self.key_index > self.upperbound:
            self.key_index -= self.octave

        note = {
            'note': self.key[self.key_index],
            'dur':  length,
            'amp': 127
        }
        return note

    def feed(self, string):
        self._feeder.feed(string)

    def _build_rhythm(self):
        self.rhythm = []
        self._build_rhythm_recurse(1)
        return self.rhythm

    def _build_rhythm_recurse(self, i):
        if self._feeder.next() == '1' and i < 16:
            self._build_rhythm_recurse(i * 2)
            self._build_rhythm_recurse(i * 2)
        else:
            self.rhythm.append(i)

    def _get_int(self, bits, signed=False):
        chunk = [self._feeder.next() for i in range(bits)]
        neg = 1
        if signed:
            if chunk[0]: neg = -1
            chunk = chunk[1:]

        val = int(''.join(chunk), 2)
        val *= neg
        return val


def main():
    if len(sys.argv) == 2:
        bc = BitComposer(sys.argv[1])
        start_timeline(bc)
    else:
        running = False
        for line in sys.stdin:
            if not running:
                bc = BitComposer(line)
                start_timeline(bc)
            else:
                bc.feed(line)


def start_timeline(bc):
    timeline = Timeline(84)
    timeline.sched(bc)
    timeline.run()


def usage():
        print("Usage: %s [string]" % sys.argv[0])


if __name__ == '__main__':
    from isobar import *
    main()