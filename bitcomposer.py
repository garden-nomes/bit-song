import sys
import bitarray
from isobar.note import Note
from isobar.key import Key
from isobar.pattern.core import Pattern


class BitFeeder(object):
    '''Feed it strings, and it will pop out a string of bits from the utf-8
    encoding of that string.

    Supports iterator interface
    '''

    def __init__(self, string=None):
        self._ba = bytearray()
        self._current_byte = b''
        self._byte_i = 0    # index in byte array
        self._bit_i = 0     # index in current bit

        if string:
            self.feed(string)

    def __iter__(self):
        return self

    def next(self):
        if self._bit_i == 0:
            self._load_next_byte()
            print   # DEBUG
        bit = self._current_byte[self._bit_i]

        self._bit_i += 1
        if self._bit_i >= len(self._current_byte):
            self._byte_i += 1
            self._bit_i = 0

        return bit

    def _load_next_byte(self):
        try:
            self._current_byte = format(self._ba[self._byte_i], '08b')
        except IndexError:
            raise StopIteration

    def feed(self, string):
        self._ba += bytearray(string, 'utf-8')
        if self._current_byte == b'':
            self._load_next_byte()


class BitComposer(Pattern):
    '''Composes music based on the bitwise representation of a string
    '''

    def __init__(self, string, key=None):
        # create bit array
        self.bits = bitarray.bitarray()
        self.bits.frombytes(bytes(string))
        self.bit_index = 0

        # create key scale range
        self.key = key if key else Key.random()
        self.octave = len(self.key.scale.semitones)
        self.lowerbound = self.octave * 3
        self.upperbound = self.octave * 8
        self.key_index = self.octave * 5

    def __iter__(self):
        return self

    def append(self, string):
        self.bits.frombytes(string)

    def bitregion(self, value):
        '''Return number of consecutive 0's or 1's from the current index
        '''
        count = 0
        try:
            while self.bits[self.bit_index] == value:
                count += 1
                self.bit_index += 1
        except IndexError:
            sys.stdout.write('\r' + self.bits[:self.bit_index].tostring())
            sys.stdout.flush()
            raise StopIteration
        return count

    def next(self):
        '''Compute next note from the string
        '''
        # move up/down scale based on consecutive 0's
        if self.bits[self.bit_index / 8]:
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

        x = self.bits[:self.bit_index].tobytes().decode('utf-8').find('\n')
        if x != -1:
            print('\r' + self.bits[:x].tobytes().decode('utf-8'))
            self.bits = self.bits[x:]

        sys.stdout.write('\r' +
            self.bits[:self.bit_index]
                .tobytes()
                .decode('utf-8')
        )
        sys.stdout.flush()
        return {'note': self.key[self.key_index], 'dur': length, 'amp': 127}


if __name__ == '__main__':
    from isobar import *

    def runbitcomposer(string, key=None):
        bc = BitComposer(string, key)
        timeline = Timeline(84)
        timeline.sched(bc)
        timeline.run()
        print

    if len(sys.argv) == 4:
        try:
            testbitcomposer(sys.argv[3], Key(sys.argv[1], sys.argv[2]))
        except KeyError:
            print("Error: unknown key")
    elif len(sys.argv) == 2:
        runbitcomposer(sys.argv[1])
    else:
        print("Usage: %s [tonic scale] string" % sys.argv[0])