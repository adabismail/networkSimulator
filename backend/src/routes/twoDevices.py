from src.classes.station.device import Device   # BUG FIX: was 'from src.classes.device' (wrong path)
from src.classes.medium.cable import Cable      # BUG FIX: was 'from src.classes.cable' (wrong path)


def createTwoDeviceTopology():
    """
    Creates two devices connected by a dedicated cable.

    Topology:
        [Device A] ──cable── [Device B]

    Domains:
        Collision : 1  (both ends share one cable)
        Broadcast : 1
    """
    deviceA = Device('A')
    deviceB = Device('B')
    cable   = Cable()

    deviceA.port = cable.connect(deviceA)
    deviceB.port = cable.connect(deviceB)

    # BUG FIX: original code had 'deviceA,deviceB,cable' with NO return keyword
    # → function returned None, unpacking in main.py raised TypeError
    return deviceA, deviceB, cable