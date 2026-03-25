from collections import deque


class Cable:
    """
    Point-to-point physical medium connecting exactly 2 devices.
    Models a dedicated wire / Ethernet patch cable.

    Properties:
      - Exactly 2 ports (port 0 and port 1)
      - Shared collision domain: if both ends transmit simultaneously → collision
      - 1 collision domain, 1 broadcast domain
    """

    def __init__(self):
        self.dict        = {0: None, 1: None}   # port → device
        self.free_ports  = deque([0, 1])
        self.transmitters = set()               # devices currently transmitting

    def connect(self, device):
        """Plug a device into a free port. Returns assigned port number, or None if full."""
        # BUG FIX: deque has no .empty() method → AttributeError
        # FIX: check len(self.free_ports) == 0
        if len(self.free_ports) == 0:
            return None
        free_port = self.free_ports.popleft()
        self.dict[free_port] = device
        return free_port

    def disconnect(self, port):
        if port is not None:
            self.free_ports.append(port)
            self.dict[port] = None

    def is_busy(self):
        """True if any device is currently transmitting."""
        return len(self.transmitters) > 0

    def collision(self):
        """True if more than one device is transmitting simultaneously."""
        return len(self.transmitters) > 1

    def transmit(self, senderPort, bit=None, flag=None, completion=None):
        """
        Forward signal to all ports except the sender.

        Modes (use keyword arguments — do NOT pass positionally):
          transmit(port, bit=b,         flag=True )  → forward one data bit
          transmit(port,                flag=False)  → collision signal → clear receiver trays
          transmit(port,                completion=True) → frame done → assemble & pass up stack

        BUG FIX: physicalLayer called medium.transmit(port, bit) positionally.
          With the original signature transmit(senderPort, bit, flag, completion):
            medium.transmit(port, bit)   → flag=None → fell to else → collision_detected() EVERY bit!
          FIX: physicalLayer now uses keyword args; this method just needs to handle them correctly.
        """
        for port, device in self.dict.items():
            if port == senderPort or device is None:
                continue
            if completion:
                device.recieverSidePhysical.transfer()
            elif flag:
                # BUG FIX: hub.py had 'recieve_bit' (typo). physicalLayer defines 'receive_bit'.
                # Standardised to 'receive_bit' (correct English) everywhere.
                device.recieverSidePhysical.receive_bit(bit)
            else:
                device.recieverSidePhysical.collision_detected()