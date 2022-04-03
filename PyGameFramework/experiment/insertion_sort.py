import random

class A:
    def __init__(self, val, active=True):
        self.val=val
        self.active=active

def insertionSort(arr):
    # Traverse through 1 to len(arr)
    for i in range(1, len(arr)):

        key = arr[i]

        # Move elements of arr[0..i-1], that are
        # greater than key, to one position ahead
        # of their current position
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key



def insertionObjectSort1(arr):
    swaps = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key.val < arr[j].val:
            arr[j + 1] = arr[j]
            j -= 1
            swaps+=1
        arr[j + 1] = key
        swaps += 1
    return swaps

def insertionObjectSort3(arr):
    swaps = 0
    for i in range(1, len(arr)):
        if not arr[i].active:
            continue
        key = arr[i]
        j = i - 1
        skips = 0
        while j >= 0: #and key.val < arr[j].val:
            if not arr[j].active: #ignore inactive entries
                skips+=1 #this is how many entries to 'jump' on the next swap
            elif key.val < arr[j].val:
                arr[j+1+skips] = arr[j]
                skips = 0 #reset the number of entries to 'jump'
                swaps += 1
            else: #we are now sorted for this sub array
                break
            j -= 1
        arr[j + 1 + skips] = key
        swaps += 1
    return swaps

def isSorted(arr):
    for i in range(0, len(arr)-2):
        if arr[i].val > arr[i+1].val:
            return False
    return True

def isActiveSorted(arr):
    active_list = list()
    for a in arr:
        if a.active:
            active_list.append(a.val)
    test_list = active_list[:]
    test_list.sort()
    if test_list == active_list:
        return True
    return False


### START ###
array1 = list()
array2 = list()

max_objects = 2000
i = 0

#build 2 identical lists
while i < max_objects:
    active = True
    if random.randint(1,10) > 4:
        active = False
    val = random.randint(1,10000)
    array1.append(A(val, active))
    array2.append(A(val, active))
    i+=1

swaps1 = insertionObjectSort1(array1)
swaps2 = insertionObjectSort3(array2)

#print("array1:")
#for i in range(len(array1)):
#    print("%d" % array1[i].val)
#print("array2")
#for i in range(len(array2)):
#    if array2[i].active:
#        print("%d" % array2[i].val)
print("Swaps for array1: " + str(swaps1))
print("Swaps for array2: " + str(swaps2))

if isSorted(array1):
    print("Array1 is sorted")
else:
    print("Array1 is not sorted")

if isActiveSorted(array2):
    print("Array2 is sorted")
else:
    print("Array2 is not sorted")