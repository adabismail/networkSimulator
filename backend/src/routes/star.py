from src.classes.station.device import Device   # BUG FIX: was 'from src.classes.device' (wrong path)
from src.classes.medium.hub import Hub          # BUG FIX: was 'from src.classes.hub' (wrong path)


def createStarTopology():
    """
    Creates a star topology: 5 devices all connected to a central hub.

    Topology:
        [A0] ─┐
        [A1] ─┤
        [A2] ─┼── [Hub]
        [A3] ─┤
        [A4] ─┘

    Domains:
        Collision : 1  (hub is a shared medium — all devices in same collision domain)
        Broadcast : 1
    """
    devicesList = []
    for i in range(5):
        # BUG FIX: original had Device('A' + i) → TypeError: can only concatenate str to str, not int
        # FIX: str(i)
        device = Device('A' + str(i))
        devicesList.append(device)

    hub = Hub(5)
    for device in devicesList:
        port = hub.connect(device)
        device.port = port

    return hub, devicesList