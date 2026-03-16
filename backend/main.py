from src.routes.twoDevices import createTwoDeviceTopology
from src.routes.star import createStarTopology

# twoDeviceNetwork
def createTwoDeviceNetwork():
    A,B,cable=createTwoDeviceTopology()
    return A,B,cable

def transferDataInTwoDeviceNetwork(sender,cable,data):
    sender.send(cable,data)

# starNetwork
def createStarNetwork():
    hub,devicesList=createStarTopology()
    return hub,devicesList
    
def transferDataInStarNetwork(sender,hub,data):
    sender.send(hub,data)


