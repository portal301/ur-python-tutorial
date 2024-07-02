# Primary interface
import socket

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

## Phase1: Make 'helloworld example' more neat
def sendScriptViaPrimaryClient(robot_url, script):
    socketPrimaryClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketPrimaryClient.connect((robot_url, PORT_PRIMARY_CLIENT))
    socketPrimaryClient.send((script + "\n").encode())
    socketPrimaryClient.close()

def sendScriptViaSecondaryClient(robot_url, script):
    socketSecondaryClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketSecondaryClient.connect((robot_url, PORT_SECONDARY_CLIENT))
    socketSecondaryClient.send((script + "\n").encode())
    socketSecondaryClient.close()

## Phase2: elaborate the functions
def getScriptFromPath(script_path):
    # Open the file in read mode
    with open(script_path, 'r') as file:
        # Read the contents of the file
        script = file.read()
        # print(script)
    return script

def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.send((script + "\n").encode())
    socketClient.close()

def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, port)

if __name__ == "__main__":
    robot_url = "192.168.0.21"
    # script_path = "scripts/helloworld.script"
    script_path = "scripts/slowmove.script"
    # sendScriptFile(robot_url, script_path, PORT_PRIMARY_CLIENT)
    sendScriptFile(robot_url, script_path, PORT_SECONDARY_CLIENT)


# load & send script


# dashboard



