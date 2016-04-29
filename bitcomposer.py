import sys
import bitarray
from isobar.note import Note
from isobar.key import Key
from isobar.pattern.core import Pattern


class BitMelody(Pattern):
    """Composes music based on the bitwise representation of a string
    """

    def __init__(self, string, key=None):
        self.bits = bitarray.bitarray()
        self.bits.frombytes(string)

        self.key = key if key else Key.random()
        self.octave = len(self.key.scale.semitones)
        self.lowerbound = self.octave * 4
        self.upperbound = self.octave * 8

        # print('%s: %s to %s'
                # % (str(self.key),
                   # str(Note(self.key[self.lowerbound])),
                   # str(Note(self.key[self.upperbound]))))

        self.reset()

    def __iter__(self):
        return self

    def reset(self):
        self.key_index = self.octave * 4
        self.index = 0

    def append(self, string):
        self.bits.frombytes(string)

    def bitregion(self, value):
        """Return number of consecutive 0's or 1's from the current index
        """
        count = 0
        try:
            while self.bits[self.index] == value:
                count += 1
                self.index += 1
        except IndexError:
            sys.stdout.write('\r' + self.bits[:self.index].tostring())
            sys.stdout.flush()
            raise StopIteration
        return count

    def next(self):
        """Compute next note from the string
        """
        # move up/down scale based on consecutive 0's
        if self.bits[self.index / 8]:
            self.key_index += self.bitregion(True)
        else:
            self.key_index -= self.bitregion(True)
        # clamp key index to predefined range by moving up/down octave
        if self.key_index < self.lowerbound:
            self.key_index += self.octave
        if self.key_index > self.upperbound:
            self.key_index -= self.octave

        # length of note based on consecutive 0's
        length = 1.0 / min(self.bitregion(False), 4)

        # print('note: %s' % str(Note(self.key[self.key_index])))
        sys.stdout.write('\r' + self.bits[:self.index].tostring())
        sys.stdout.flush()
        return {'note': self.key[self.key_index], 'dur': length, 'amp': 127}


def testbitcomposer(string, key):
    bc = BitMelody(string, key)
    timeline = Timeline(84)
    timeline.sched(bc)
    timeline.run()
    print


if __name__ == '__main__':
    from isobar import *
    if (len(sys.argv) == 4):
        try:
            testbitcomposer(sys.argv[3], Key(sys.argv[1], sys.argv[2]))
        except KeyError:
            print("Error: unknown key")
    elif (len(sys.argv) == 2):
        testbitcomposer(sys.argv[1], Key.random())
    else:
        print("Usage: %s [tonic scale] string" % sys.argv[0])