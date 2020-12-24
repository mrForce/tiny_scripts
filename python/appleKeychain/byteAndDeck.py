import itertools
import collections

class ByteAndDeck(collections.abc.Sequence):
    """
    Uses the deque deck and byte iterator in tandem to provide a random access list of bytes.
    """
    def __init__(self, byteIterator, minSize):
        self.byteIterator = byteIterator
        self.deck = collections.deque()
        self.minSize = minSize
        self.deck.extend(itertools.islice(self.byteIterator, self.minSize))
    def __getitem__(self, key):
        stop = key
        if isinstance(key, slice):
            stop = key.stop
        deckLen = len(self.deck)
        if stop >= deckLen:
            self.deck.extend(itertools.islice(self.byteIterator, stop - deckLen + 1))
        if isinstance(key, slice):
            l = list(self.deck)
            return l.__getitem__(key)
        else:
            return self.deck[stop]
    def __len__(self):
        return len(self.deck)
    def popleft(self):
        item = self.deck.popleft()
        if len(self.deck) < self.minSize:
            self.deck.extend(itertools.islice(self.byteIterator, self.minSize - len(self.deck)))            

    def toByteArray(self, length):
        #copy first length bytes into a byte array and return.
        return bytes(self[0:length])
    
def toInt(b):
    return int.from_bytes(bytes(b), byteorder='big', signed=False)
def getBytesAsInt(ba, startIndex, k):
    a = ba[startIndex:(startIndex + k)]
    assert(len(a) == k)
    return toInt(a)
