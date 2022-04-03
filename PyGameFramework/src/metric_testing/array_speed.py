'''
Speed of multi dimensional array vs objects
Speed if numpy vs array


'''

from time import time
import random
import sys

readtest = 0

class BV: #BoundingVolume
    square = [random.randint(0,200),random.randint(0,200),random.randint(0,200),random.randint(0,200)]

    def int(self):
        pass

    def test(self):
        global readtest
        if self.square[0] >= 0:
            readtest +=1


class BVC: #BoundingVolumeContainer

    #one for each frame of animation
    course_bvs = [BV(), BV(), BV(), BV(), BV(), BV(), BV(), BV()]
    fine_bvs = [[BV(),BV(), BV()],
                [BV(), BV(), BV()],
                [BV(), BV(), BV()],
                [BV(),BV(), BV()],
                [BV(), BV(), BV()],
                [BV(), BV(), BV()],
                [BV(), BV(), BV()],
                [BV(),BV(), BV()]]

    def __init__(self):
        pass

    def test(self):
        for a in self.course_bvs:
            a.test()
        for b in self.fine_bvs:
            for c in b:
                c.test()


class BP: #BoundingPortion
    #one for each direction
    bvcs = [BVC(),BVC(),BVC(),BVC(),BVC(),BVC(),BVC(),BVC()]
    def __init__(self):
        pass

    def test(self):
        for a in self.bvcs:
            a.test()

class EBC: #EntityBoundingComponent
    #one for each sub-entity and state
    bps = [[BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()], #Head
           [BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()], #Torso
           [BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()], #Right Arm
           [BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()], #Left Arm
           [BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()], #L Leg
           [BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP(), BP()]] #R Leg

    def __init__(self):
        pass

    def test(self):
        for a in self.bps:
            for b in a:
                b.test()

def createFlatArray():
    flatarray = []
    i = 0
    while i < 15360:
        flatarray+=[BV()]
        i+=1

    return flatarray

def createFlatTuple():
    return tuple(createFlatArray())


def create5Darray():
    multiarray = [] #subcomponents, states, directions, frames, BV's

    i=0
    j=0
    k=0
    l=0
    while i <6: #subcomponents
        i+=1
        while j < 10: #states
            j+=1
            while k < 8: #directions
                k+=1
                while l < 8: #frames
                    #multiarray+= [[[[[BV(), BV(), BV(), BV()]]]]]
                    l+=1
    i = 0
    while i <3840:
        multiarray += [[[[[BV(), BV(), BV(), BV()]]]]]
        i+=1
    return multiarray

def createintDict():
    dictarray = {}
    i = 0
    while i < 15360:
        dictarray[i] = BV()
        i+=1
    return dictarray

def createintintDict():
    dictarray = {}
    i = 0
    while i < 15360:
        dictarray[(i,i)] = BV()
        i+=1
    return dictarray

def createstringDict():
    dictarray = {}
    i = 0
    while i < 15360:
        dictarray['astring' + str(i)] = BV()
        i+=1
    return dictarray

def time_allClass(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the class')
    ebc = EBC()
    i = 0
    start = time()
    while i < numtests:
        ebc.test()
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end-start

def time_allFlat_foreach(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the flat array with foreach')
    ebc = createFlatArray()
    i = 0
    start = time()
    while i < numtests:
        for a in ebc:
            a.test()
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end-start

def time_allFlattuple_foreach(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the flat tuple with foreach')
    ebc = createFlatTuple()
    i = 0
    start = time()
    while i < numtests:
        for a in ebc:
            a.test()
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end-start

def time_allFlat_indexed(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the flat array with indexing')
    ebc = createFlatArray()
    i = 0
    start = time()
    while i < numtests:
        j = 0
        while j < 15360:
            ebc[j].test()
            j+=1
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_allFlattuple_indexed(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the flat tuple with indexing')
    ebc = createFlatTuple()
    i = 0
    start = time()
    while i < numtests:
        j = 0
        while j < 15360:
            ebc[j].test()
            j+=1
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start


def time_allMulti_indexing(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the multi array with indexing')
    ebc = create5Darray()

    max_i = len(ebc)
    max_j = len(ebc[0])
    max_k = len(ebc[0][0])
    max_l = len(ebc[0][0][0])
    max_m = len(ebc[0][0][0][0])

    start = time()
    total = 0
    while total < numtests:
        total+=1
        i=0
        while i<max_i:
            j=0
            while j < max_j:
                k=0
                while k < max_k:
                    l=0
                    while l < max_l:
                        m=0
                        while m < max_m:
                            ebc[i][j][k][l][m].test()
                            m+=1
                        l+=1
                    k+=1
                j+=1
            i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))

    return end - start

def time_allMulti_foreach(numtests = 1):
    global readtest
    readtest = 0
    print('Read every BV in the multi array with foreach')
    ebc = create5Darray()
    i = 0
    start = time()
    while i < numtests:
        for a in ebc:
            for b in a:
                for c in b:
                    for d in c:
                        for e in d:
                            e.test()
        i+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))

    return end - start

def time_oneread_class(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the class')
    ebc = EBC()


    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc.bps[0][0].bvcs[0].fine_bvs[3][0].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_flat(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the class')
    ebc = createFlatArray()


    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc[10000].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_tuple(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the tuple')
    ebc = createFlatTuple()
    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc[10000].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_multi(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the class')
    ebc = create5Darray()


    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc[0][0][0][0][0].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_intdict(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the int dict')
    ebc = createintDict()
    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc[55].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_intintdict(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the intint dict')
    ebc = createintintDict()
    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc[(20,20)].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

def time_oneread_stringdict(numtests = 1, numreads = 15360):
    global readtest
    readtest = 0
    print('Read a single BV in the string dict')
    ebc = createstringDict()
    start = time()
    i=0
    while i<numtests:
        i+=1
        localreads = 0
        while localreads < numreads:
            ebc['astring22'].test()
            localreads+=1
    end = time()
    print('Total reads: ' + str(readtest))
    print('Time: ' + str(end-start))
    return end - start

if __name__ == '__main__':
    TESTS = 500
    results = []
    print('Speed Test')
    results+=  [['Read All in Class:         '] + [time_allClass(TESTS)]]
    results += [['Read All in flat foreach:  '] + [time_allFlat_foreach(TESTS)]]
    results += [['Read All in flat indexed:  '] + [time_allFlat_indexed(TESTS)]]
    results += [['Read All in multi foreach: '] + [time_allMulti_foreach(TESTS)]]
    results += [['Read All in multi indexed: '] + [time_allMulti_indexing(TESTS)]]
    results += [['Read All in tuple foreach: '] + [time_allFlattuple_foreach(TESTS)]]
    results += [['Read All in tuple indexed: '] + [time_allFlattuple_indexed(TESTS)]]
    results += [['Read one in class:         '] + [time_oneread_class(TESTS)]]
    results += [['Read one in flat:          '] + [time_oneread_flat(TESTS)]]
    results += [['Read one in multi:         '] + [time_oneread_multi(TESTS)]]
    results += [['Read one in int dict:      '] + [time_oneread_intdict(TESTS)]]
    results += [['Read one in string dict:   '] + [time_oneread_stringdict(TESTS)]]
    results += [['Read one in intint dict:   '] + [time_oneread_intintdict(TESTS)]]
    results += [['Read one in tuple      :   '] + [time_oneread_tuple(TESTS)]]
    print("RESULTS")
    for r in results:
        print(r)

    '''
    Results for 500 TESTS
    Read All:
    1. Flat Tuple: Foreach - 2.46
    2. Flat List: Foreach - 2.54
    3. Class - 2.90
    4. multi dimensional foreach 3.12
    5. Tuple indexed - 3.85
    6. Flat indexed - 3.85
    
    Read One:
    1. Flat Tuple - 3.79
    2. int dict - 3.84
    3. flat array - 3.85
    4. string dict - 3.93
    5. intint dict - 4.11
    6. multi - 4.68
    7. Class - 5.5
    
    
    
    '''