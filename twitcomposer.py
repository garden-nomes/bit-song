from bitcomposer import BitComposer
from tweetfeeder import TweetFeeder, NoTweetsYet
import time


class TwitComposer(BitComposer):

    def __init__(self):
        self.feeder = TweetFeeder()
        while not self.feeder.ready():
            pass
        BitComposer.__init__(self, self._grab_tweet())

    def next(self):
        ret = BitComposer.next(self)
        if self.bit_index > self.bits.length() / 2 and self.feeder.ready():
            tweet = self._grab_tweet()
            print("tweet gotten: " + tweet)
            self.append('\n\n' + tweet)
            print
        return ret

    def disconnect(self):
        self.feeder.disconnect()

    def _grab_tweet(self):
        return self.feeder.get_tweet().text.encode('utf-8')


if __name__ == '__main__':
    from isobar import *

    def runtwitcomposer():
        try:
            bc = TwitComposer()
            timeline = Timeline(140)
            timeline.sched(bc)
            timeline.run()
        except KeyboardInterrupt:
            bc.disconnect()
            print
            exit()

    runtwitcomposer()
