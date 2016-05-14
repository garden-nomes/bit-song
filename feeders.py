import sys


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
        self._ba += bytearray(string, 'utf-8')
        if self._current_byte == b'':
            self._load_next_byte()

    def _load_next_byte(self):
        try:
            self._current_byte = format(self._ba[0], '08b')
            self._ba = self._ba[1:]
        except IndexError:
            raise StopIteration


class UnicodeFeeder(object):

    def __init__(self, string=None):
        self._s = u''
        if string:
            self.feed(string)

    def feed(self, string):
        self._s += string

    def next(self):
        '''Returns tuple of (width, codepoint)
        '''
        try:
            width = len(bytearray(self._s[0], 'utf-8'))
            codepoint = ord(self._s[0])
            self._s = self._s[1:]
            return (width, codepoint)
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return self
