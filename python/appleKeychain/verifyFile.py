import argparse
import itertools
import collections
import mmap
import os
WINDOW_SIZE = 4
ATOM_SIZE = 4
METADATA_ID = 0X80008000
parser = argparse.ArgumentParser(description='verify a file')
parser.add_argument('file')
parser.add_argument('outputDir')
args = parser.parse_args()
assert(os.path.isdir(args.outputDir))
def hasMagic(byteAccess):
    return byteAccess[0] == b'k' and byteAccess[1] == b'y' and byteAccess[2] == b'c' and byteAccess[3] == b'h'


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
        return b''.join(self[0:length])
    
def toInt(b):
    return int.from_bytes(b, byteorder='big', signed=False)
def getBytesAsInt(ba, startIndex, k):    
    return toInt(b''.join(ba[startIndex:(startIndex + k)]))

def verifyMetadataRecord(byteAccess, startIndex):
    return getBytesAsInt(byteAccess, startIndex + 6*ATOM_SIZE, ATOM_SIZE) == 0XFADE0711
def verifyMetadata(byteAccess, startIndex):
    tableSize = getBytesAsInt(byteAccess, startIndex, ATOM_SIZE)
    rc = getBytesAsInt(byteAccess, startIndex + 2*ATOM_SIZE, ATOM_SIZE)
    rnc = getBytesAsInt(byteAccess, startIndex + 6*ATOM_SIZE, ATOM_SIZE)
    if rnc == 0:
        return False
    count = 0
    for i in range(0, rnc):
        offset = getBytesAsInt(byteAccess, startIndex + (i + 7)*ATOM_SIZE, ATOM_SIZE)
        if offset >= ATOM_SIZE*(7 + rnc):
            if not verifyMetadataRecord(byteAccess, startIndex + offset):
                return False
            count += 1
    if count != rc:
        return False
    return True

#pass an instance of the ByteAndDeck class.
def extractKeychain(byteAccess):
    if hasMagic(byteAccess):
        headerSize = getBytesAsInt(byteAccess, 2*ATOM_SIZE, ATOM_SIZE)
        schemaOffset = getBytesAsInt(byteAccess, 3*ATOM_SIZE, ATOM_SIZE)
        if schemaOffset > 50:
            return None
        schemaSize = getBytesAsInt(byteAccess, schemaOffset, ATOM_SIZE)
        if schemaSize > 2*10**9:
            return None
        tableCount = getBytesAsInt(byteAccess, schemaOffset + ATOM_SIZE, ATOM_SIZE)
        if tableCount > 100:
            return None
        offsets = [getBytesAsInt(byteAccess, schemaOffset + (i+2)*ATOM_SIZE, ATOM_SIZE) for i in range(0, tableCount)]
        if max(offsets) > schemaSize:
            return None
        containsMetadata = False
        for offset in offsets:
            tableSize = getBytesAsInt(byteAccess, schemaOffset + offset, ATOM_SIZE)
            tableID = getBytesAsInt(byteAccess, schemaOffset + offset + ATOM_SIZE, ATOM_SIZE)
            if tableID == METADATA_ID:
                containsMetadata = True
                if not verifyMetadata(byteAccess, schemaOffset + offset):
                    return None
                    

        if not containsMetadata:
            return None
        length = schemaOffset + schemaSize + 4
        return byteAccess.toByteArray(length)
    else:
        return None

def keychainGenerator(byteIterator):
    byteAccess = ByteAndDeck(byteIterator, WINDOW_SIZE)
    while len(byteAccess) >= WINDOW_SIZE:
        if hasMagic(byteAccess):
            keychain = extractKeychain(byteAccess)
            if keychain:
                yield keychain
        byteAccess.popleft()

f = open(args.file, 'rb')
byteIter = iter(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))
keychains = keychainGenerator(byteIter)
i = 1
for keychain in keychains:
   with open(os.path.join(args.outputDir, str(i) + '.bin'), 'wb') as g:
       g.write(keychain)
