import queue
q = queue.Queue()
q.put("fisrt queue")
q.put("second queue")
q.put("third queue")

# q = ["fisrt queue","second queue","third queue"]
while not q.empty():
    print(q.get())


task = queue.Queue()
task.put({"action":"ready"})

# vision camera -> object detection result: p=[0,0,0,0,0,0] type="bottle"
object_pos = [0,0,0,0,0,0]
object_type = "bottle"

task.put({"action":"grip","data":object_pos})
task.put({"action":"ungrip","data":object_type})


def requestToRobot(task):
    # movej, movej, movej, movej ...
    # movel, movel, movel ...
    # wait sensor signal
    # socket open/connect
    # send data using socket
    # ~~~~~~~~~~~~~~~~
    print(task)

while not task.empty():
    requestToRobot(task.get())


# myrobotMission

# import myrobotMission

