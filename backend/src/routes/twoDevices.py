# This is a backend route that handles two device data transfer.
from src.classes.medium.cable import Cable
from src.classes.station.device import Device
def createTwoDeviceTopology():
    deviceA=Device('A')
    deviceB=Device('B')
    cable=Cable()
    
    deviceA.port=cable.connect(deviceA)
    deviceB.port=cable.connect(deviceB)

    return deviceA,deviceB,cable
    