import argparse

parser = argparse.ArgumentParser(description='hello')
parser.add_argument('file')
args = parser.parse_args()

def toInt(b):
    return int.from_bytes(b, byteorder='big', signed=False)
def getBytesAsInt(ba, startIndex, k):
    return toInt(ba[startIndex:(startIndex + k)])

class Record:
    def __init__(self, ba, recordStart):
        self.ba = ba
        self.recordStart = recordStart
        self.recordSize = getBytesAsInt(ba, recordStart, 4)
        self.recordNumber = getBytesAsInt(ba, recordStart + 4, 4)

class Table:
    def __init__(self, ba, tableStart):
        self.ba = ba
        self.tableStart = tableStart
        self.tableSize = getBytesAsInt(ba, tableStart, 4)
        self.tableID = getBytesAsInt(ba, tableStart + 4, 4)
        self.rc = getBytesAsInt(ba, tableStart + 8, 4)
        self.firstRecordOffset = getBytesAsInt(ba, tableStart + 12, 4)
        self.indexesOffset = getBytesAsInt(ba, tableStart + 16, 4)
        self.freeListHead = getBytesAsInt(ba, tableStart + 20, 4)
        self.rnc = getBytesAsInt(ba, tableStart + 24, 4)
    def getRecord(self, offset):
        if offset < self.firstRecordOffset:
            return None
        else:
            return Record(self.ba, self.tableStart + offset)
    def getRecordOffsetList(self):
        offsets = []
        for i in range(0, self.rnc):
            offsets.append(getBytesAsInt(self.ba, self.tableStart + 28 + 4*i, 4))
        return offsets

    def getRecordSizes(self):
        offsets = self.getRecordOffsetList()
        sizes = []
        for x in offsets:
            record = self.getRecord(x)
            if record:
                sizes.append(record.recordSize)        
        return sizes
def verifyFLH(table):
    if table.rc == table.rnc:
        assert(table.freeListHead == 0)
    else:
        assert(table.rc < table.rnc)
        assert(table.freeListHead == 4*table.rc + 29)
def verifyRecordOffsetList(table):
    offsets = table.getRecordOffsetList()
    numUnused = 0
    for i in range(0, len(offsets)):
        offset = offsets[i]
        #print('offset: ' + str(offset))
        record = table.getRecord(offset)
        if record:
            #print('record: ' + ' '.join([str(record.recordStart), str(record.recordSize), str(record.recordNumber)]))
            assert(record.recordNumber == i)
        else:
            numUnused += 1
    assert(numUnused == table.rnc - table.rc)

def verifyRecordIteration(table):
    offsetsFromList = table.getUsedOffsetsFromList()
    offsetsBySizeIter = table.getOffsetsBySizeIter()
    assert(len(offsetsFromList) == len(offsetsBySizeIter))
    for i in range(0, len(offsetsFromList)):
        if offsetsFromList[i] != offsetsBySizeIter[i]:
            print('First record offset: ' + str(table.firstRecordOffset))
            print(offsetsFromList)
            print(offsetsBySizeIter)
        assert(offsetsFromList[i] == offsetsBySizeIter[i])
def verifyTableSize(table):
    recordSizes = table.getRecordSizes()
    print('total record sizes: ' + str(sum(recordSizes)))
    assert(sum(recordSizes) + 28 + 4*table.rnc <= table.tableSize)




with open(args.file, 'rb') as f:
    ba = bytearray(f.read())
    magic = ba[0:4]
    print('magic: ' + str(magic))
    version = ba[4:8]
    print('version: ' + str(version))
    headerSize = ba[8:12]
    print('header size: ' + str(headerSize))
    schemaOffset = ba[12:16]
    print('schema offset: ' + str(schemaOffset))
    authOffset = ba[16:20]
    print('auth offset: ' + str(authOffset))
    schemaStart = toInt(schemaOffset)
    schemaSize = ba[schemaStart:(schemaStart + 4)]
    print('schema size: ' + str(toInt(schemaSize)))
    tableCount = toInt(ba[(schemaStart + 4):(schemaStart + 8)])
    print('table count: ' + str(tableCount))
    print('X + 1 offset: ' + str(toInt(ba[(schemaStart + 8 + 4*tableCount):(schemaStart + 12 + 4*tableCount)])))
    for i in range(0, tableCount):
        s = ['table ', str(i + 1), ' offset: ']
        tableOffset = toInt(ba[(schemaStart + 8 + 4*i):(schemaStart + 12 + 4*i)])
        s.append(str(tableOffset))
        tablePlace = tableOffset + schemaStart
        table = Table(ba, tablePlace)        
        size = table.tableSize
        count = table.rc        
        tableID = table.tableID
        recordNumberCount = table.rnc
        s.append('tableID')
        s.append(str(hex(tableID)))
        s.append('size')
        s.append(str(size))
        s.append('record count:')
        s.append(str(count))
        s.append('record number count:')
        s.append(str(recordNumberCount))
        firstRecordOffset = table.firstRecordOffset
        s.append('first record offset:')
        s.append(str(firstRecordOffset))
        print(' '.join(s))
        #verifyFLH(table)
        verifyRecordOffsetList(table)
        verifyTableSize(table)
        s = []
        
        print('first record offset: ' + str(firstRecordOffset))
        assert(firstRecordOffset - 28 == recordNumberCount*4)
        print('First offset in list: ' + str(toInt(ba[(tablePlace + 28):(tablePlace + 32)])))
        if recordNumberCount == 1 and count == 0:
            print('size of first record: ' + str(toInt(ba[(tablePlace + firstRecordOffset):(tablePlace + firstRecordOffset + 4)])))
            
        
        
