# This is a backend route that handles two device data transfer.
from src.classes.cable import Cable
from src.classes.device import Device
def createTwoDeviceTopology():
    deviceA=Device('A')
    deviceB=Device('B')
    cable=Cable()
    
    deviceA.port=cable.connect(deviceA)
    deviceB.port=cable.connect(deviceB)

    deviceA,deviceB,cable
    