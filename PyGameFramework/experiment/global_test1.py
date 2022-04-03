import myglobals
import global_test2




def bar():
    print("bar() - MYGLOBE1: " + str(myglobals.MYGLOBE1) )





if __name__ == "__main__":
    print("Globals test start")
    bar()
    print("MYGLOBE1: " + str(myglobals.MYGLOBE1) )
    global_test2.foo()

    myglobals.MYGLOBE1 = "anewstring"
    print("MYGLOBE1: " + str(myglobals.MYGLOBE1) )
    global_test2.foo()
    bar()
    print("Globals test end")