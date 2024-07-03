print("hello world")
print('hello world')


# list
pos=[1,2,3,4,5,6]

print(pos)

print("printing pos one by one:")
print(pos[0])
print(pos[1])
print(pos[2])
print(pos[3])
print(pos[4])
print(pos[5])

# print list using for loop
print("printing pos one by one using for loop:")
for i in pos:
    print("data:",i)


# dict
dict0 = {'1':0,'2':2,'3':3}
dict1 = {
    'ready':[0,0,0,0,0,0],
    'grip':[1,1,1,1,1,1],
    'ungrip':[2,2,2,2,2,2],
    # "test": [3,3,3,3,3,3],
    }

print(dict1)

print("printing dict1 one by one:")
print(dict1["ready"])
print(dict1["grip"])
print(dict1["ungrip"])

print("printing dict1 one by one using for loop:")
for key in dict1.keys():
    print(key, dict1[key])

for key, value in dict1.items():
    print(key, value)
