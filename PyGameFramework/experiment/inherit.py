class ParentClass:
    def __init__(self, data):
        self.data = data

    def foo(self):
        print('Parent Foo data: ' + str(self.data))

class ChildClass(ParentClass):
    def __init__(self, data):
        super(ChildClass, self).__init__(data)

    def foo(self):
        super(ChildClass, self).foo()
        print('Child Foo')

class ClassA:
    def __init__(self, numb):
        self.data = 'A' + str(numb)

class ClassB:
    def __init__(self):
        self.data = 'B'

if __name__ == '__main__':
    child1 = ChildClass(1)
    child2 = ChildClass(2)
    child1.foo()
    child2.foo()

    MAKEA = ClassA
    MAKEB = ClassB

    classA1 = MAKEA(1)
    classA2 = MAKEA(2)
    classB = MAKEB()

    print(classA1.data)
    print(classA2.data)
    print(classB.data)
