# c/c++
# int function_name(int a, int b){
#     return a+b;
# }

def function1(a, b):
    print(a+b)

function1(1,2)
# function1() # fail

def function2(a=1, b=2):
    print("a:",a)
    print("b:",b)

function2()
function2(10,20) # a=10, b=20
function2(b=20,a=10) # a=10, b=20
function2(b=31) # a=1, b=31