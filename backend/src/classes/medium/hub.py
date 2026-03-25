from collections import deque


class Hub:
    """
    Layer 1 multi-port repeater.

    Behaviour:
      - Broadcasts every received bit to ALL other connected ports (no intelligence).
      - Entire hub is ONE collision domain and ONE broadcast domain.
      - Does NOT examine MAC addresses — that is a Layer 2 concern.

    Collision domain  : 1  (all ports share the same medium)
    Broadcast domain  : 1
    """

    def __init__(self, ports):
        self.dict         = {p: None for p in range(ports)}  # port → device
        self.free_ports   = deque(range(ports))
        self.transmitters = set()

    def connect(self, device):
        """Plug a device into a free port. Returns assigned port number, or None if full."""
        # BUG FIX: deque has no .empty() method → would raise AttributeError
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
        return len(self.transmitters) > 0

    def collision(self):
        return len(self.transmitters) > 1

    def transmit(self, senderPort, bit=None, flag=None, completion=None):
        """
        Broadcast bit/signal to every port except the sender.

        flag=True      → normal data bit → call receive_bit(bit) on all receivers
        flag=False     → collision       → call collision_detected() on all receivers
        completion=True→ frame done      → call transfer() on all receivers
        """
        for port, device in self.dict.items():
            if port == senderPort or device is None:
                continue
            if completion:
                device.recieverSidePhysical.transfer()
            elif flag:
                # BUG FIX: original hub.py used 'recieve_bit' (typo) — fixed to 'receive_bit'
                device.recieverSidePhysical.receive_bit(bit)
            else:
                device.recieverSidePhysical.collision_detected()