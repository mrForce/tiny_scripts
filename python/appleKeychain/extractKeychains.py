import argparse
import itertools
import collections
import sys
import mmap
import os
from byteAndDeck import *
WINDOW_SIZE = 4
ATOM_SIZE = 4
METADATA_ID = 0X80008000
parser = argparse.ArgumentParser(description='verify a file')
parser.add_argument('file')
parser.add_argument('outputDir')
args = parser.parse_args()
assert(os.path.isdir(args.outputDir))
def hasMagic(byteAccess):
    return byteAccess[0] == ord('k') and byteAccess[1] == ord('y') and byteAccess[2] == ord('c') and byteAccess[3] == ord('h')


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
        try:
            headerSize = getBytesAsInt(byteAccess, 2*ATOM_SIZE, ATOM_SIZE)
            if headerSize > 20:
                return None
            schemaOffset = getBytesAsInt(byteAccess, 3*ATOM_SIZE, ATOM_SIZE)
            if schemaOffset > 50:
                return None
            schemaSize = getBytesAsInt(byteAccess, schemaOffset, ATOM_SIZE)
            if schemaSize > 10**9:
                return None
            tableCount = getBytesAsInt(byteAccess, schemaOffset + ATOM_SIZE, ATOM_SIZE)
            if tableCount > 100:
                return None
            offsets = [getBytesAsInt(byteAccess, schemaOffset + (i+2)*ATOM_SIZE, ATOM_SIZE) for i in range(0, tableCount)]
            if max(offsets) > schemaSize:
                return None
            containsMetadata = False
            tableSizeSum = 0
            for offset in offsets:
                print('offset: ' + str(offset))
                tableSize = getBytesAsInt(byteAccess, schemaOffset + offset, ATOM_SIZE)
                print('table size: ' + str(tableSize))
                if offset + tableSize > schemaSize:
                    return None
                tableSizeSum += tableSize
                if schemaSize < tableSizeSum:
                    return None
                tableID = getBytesAsInt(byteAccess, schemaOffset + offset + ATOM_SIZE, ATOM_SIZE)
                if tableID == METADATA_ID:
                    containsMetadata = True
                    if not verifyMetadata(byteAccess, schemaOffset + offset):
                        return None
                    

            if not containsMetadata:
                return None
            print('Found a valid keychain')
            print('header size: ' + str(headerSize))
            print('schema offset: ' + str(schemaOffset))
            print('schema size: ' + str(schemaSize))
            print('table count: ' + str(tableCount))
            print('offsets')
            print(offsets)
            length = schemaOffset + schemaSize + 4
            print('length: ' + str(length))
            return byteAccess.toByteArray(length)
        except e:
            print('exception')
            print(e)
            return None
    else:
        return None

def keychainGenerator(byteIterator):
    byteAccess = ByteAndDeck(byteIterator, WINDOW_SIZE)
    i = 0
    while len(byteAccess) >= WINDOW_SIZE:
        if i == 54976512:
            print(byteAccess.deck)
        if i % 10**8 == 0:
            print('i: ' + str(i/(10**8)))
        i += 1
        if hasMagic(byteAccess):
            print('found magic')        
            keychain = extractKeychain(byteAccess)
            if keychain:
                yield keychain
        byteAccess.popleft()

def byteReader(f, chunkSize=8192):
    while True:
        chunk = f.read(chunkSize)
        if chunk:
            yield from chunk
        else:
            break
        
f = open(args.file, 'rb')
#byteIter = iter(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))
byteIter = byteReader(f)
keychains = keychainGenerator(byteIter)
i = 1
for keychain in keychains:
    with open(os.path.join(args.outputDir, str(i) + '.bin'), 'wb') as g:
        g.write(keychain)
    i += 1
