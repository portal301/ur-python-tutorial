


# print
print("Hello, World!")

# dictionaly
example_dict = {"key1":1, "key2":2}
print(example_dict)

# list
example_list = [1,2,3,4,5]
print(example_list)

# for loop
for key in example_dict.keys():
    print(key, example_dict[key])

for key, value in example_dict.items():
    print(key, value)

for i in example_list:
    print(i)

# queue
import queue
q = queue.Queue()
q.put("fisrt queue")
q.put("second queue")
q.put("third queue")

while not q.empty():
    print(q.get())


# if statement
if 1 in example_list:
    print("1 is in the list")

# function
def myfunc():
    print("myfunc")
myfunc()

# class
class MyClass:
    def __init__(self):
        print("MyClass")
    def mymethod(self):
        print("mymethod")
c = MyClass()
c.mymethod()


# async function
import asyncio
async def myasyncfunc():
    print("myasyncfunc")
    await asyncio.sleep(1)
    print("myasyncfunc done")
asyncio.run(myasyncfunc())

# async class
class MyClassAsync:
    def __init__(self):
        print
        print("MyClassAsync")
    async def mymethod(self):
        print("mymethod")
        await asyncio.sleep(1)
        print("mymethod done")
c = MyClassAsync()
asyncio.run(c.mymethod())

