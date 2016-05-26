from isobar.pattern import Pattern
from isobar.key import Key
from isobar.scale import Scale


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
        self._lowerbound = self._octave * 3
        self._upperbound = self._octave * 8
        self._key_index = self._octave * 5

    def next(self):
        '''Compute next note from the string
        '''

        try:
            if not self._rhythm:
                # compute the next measure's rhythm
                self._build_rhythm()

            # get the length of the next note
            length = 4.0 / self._rhythm[0]
            self._rhythm = self._rhythm[1:]

            # shift the key index by a 4-bit signed integer
            self._key_index += self._get_int(4, True)

            # clamp key index to predefined range by moving up/down octave
            if self._key_index < self._lowerbound:
                self._key_index += self._octave
            if self._key_index > self._upperbound:
                self._key_index -= self._octave

            note = {
                'note': self._key[self._key_index],
                'dur':  length,
                'amp': 127
            }
        except StopIteration:
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
            self._rhythm.append(i)

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