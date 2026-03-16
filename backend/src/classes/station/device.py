from src.utils.mac import giveMacAddress
from src.classes.station.physicalLayer import senderSidePhysical,recieverSidePhysical
from src.classes.station.dataLinkLayer import senderSideDataLink,recieverSideDataLink

class Device:
    companyIdentifier='00:1A:2B'
    def __init__(self,name):
        self.name=name
        self.macAddress=giveMacAddress(Device.companyIdentifier)
        self.port=None
        self.senderSidePhysical=senderSidePhysical(self)
        self.recieverSidePhysical=recieverSidePhysical(self)
        self.senderSideDataLink=senderSideDataLink(self)
        self.recieverSidePhysical=recieverSideDataLink(self)