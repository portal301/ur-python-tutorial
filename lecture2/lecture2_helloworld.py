import socket

robot_url = "192.168.0.21"
script = """
def helloworld():
    popup("Happy learning!")
end
"""

socketPrimaryClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# change the robot IP address here
socketPrimaryClient.connect((robot_url, 30001)) # 30001 --> Primary interface
socketPrimaryClient.send((script + "\n").encode())
socketPrimaryClient.close()



# PORT_PRIMARY_CLIENT = 30001
# PORT_SECONDARY_CLIENT = 30002

# ## Phase1: Make 'helloworld example' more neat
# def sendScriptViaPrimaryClient(robot_url, script):
#     socketPrimaryClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     socketPrimaryClient.connect((robot_url, PORT_PRIMARY_CLIENT))
#     socketPrimaryClient.send((script + "\n").encode())
#     socketPrimaryClient.close()

# def sendScriptViaSecondaryClient(robot_url, script):
#     socketSecondaryClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     socketSecondaryClient.connect((robot_url, PORT_SECONDARY_CLIENT))
#     socketSecondaryClient.send((script + "\n").encode())
#     socketSecondaryClient.close()