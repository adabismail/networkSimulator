from src.utils.mac import giveMacAddress
from src.classes.station.physicalLayer import senderSidePhysical, recieverSidePhysical
from src.classes.station.dataLinkLayer import senderSideDataLink, recieverSideDataLink


class Device:
    """
    Represents a Layer 1/2 end device (host/PC).

    Stack:
      Application data
           ↓  ↑
      [ Data Link Layer ]   senderSideDataLink / recieverSideDataLink
           ↓  ↑
      [ Physical Layer  ]   senderSidePhysical / recieverSidePhysical
           ↓  ↑
         medium (Hub / Cable / Switch)
    """
    companyIdentifier = '00:1A:2B'   # OUI — first 3 octets of MAC

    def __init__(self, name):
        self.name = name
        self.macAddress = giveMacAddress(Device.companyIdentifier)
        self.port = None   # assigned when connected to a medium
        self.medium = None

        # Physical layer (both directions)
        self.senderSidePhysical   = senderSidePhysical(self)
        self.recieverSidePhysical = recieverSidePhysical(self)

        # Data Link layer (both directions)
        self.senderSideDataLink   = senderSideDataLink(self)
        # BUG FIX: original code had TWO lines both assigned to self.recieverSidePhysical:
        #   self.recieverSidePhysical = recieverSidePhysical(self)   ← correct
        #   self.recieverSidePhysical = recieverSideDataLink(self)   ← OVERWROTE physical receiver!
        # FIX: second line uses correct attribute name recieverSideDataLink
        self.recieverSideDataLink = recieverSideDataLink(self)

    def send(self, medium, data, dest_mac='FF:FF:FF:FF:FF:FF'):
        """
        Public API to send data through a medium.

        Args:
            medium   : Cable, Hub, or Switch the device is connected to
            data     : Plain text string to send
            dest_mac : Destination MAC address. Defaults to broadcast (FF:FF:FF:FF:FF:FF).
                       Pass a specific MAC for unicast (used with switches for targeted delivery).

        BUG FIX: main.py called sender.send(cable, data) but Device had NO send() method → AttributeError
        """
        length = len(data.encode('utf-8'))
        self.senderSideDataLink.conversion(dest_mac, self.macAddress, length, data, medium)

    def __repr__(self):
        return f'Device(name={self.name}, MAC={self.macAddress}, port={self.port})'