from src.classes.station.device import Device
from src.classes.medium.hub import Hub
def createStarTopology():
    devicesList=[]
    for i in range(0,5):
        device=Device('A'+str(i))
        devicesList.append(device)
    hub=Hub(5)
    
    for device in devicesList:
        port=hub.connect(device)
        device.port=port
    return hub,devicesList