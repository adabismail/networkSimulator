from collections import deque


class Switch:
    """
    Layer 2 intelligent switch with MAC address learning.

    Behaviour:
      - Learns source MAC → port mappings (CAM table) as frames arrive.
      - Unicast to known destination  : forward to THAT port only.
      - Unicast to unknown destination: flood all ports except sender.
      - Broadcast (FF:FF:FF:FF:FF:FF) : flood all ports except sender.
      - Each port is a SEPARATE collision domain (no collisions across ports).

    Per the assignment test cases:
      Switch + 5 devices:
        Collision domains : 5  (one per port — each device-to-switch link is independent)
        Broadcast domains : 1  (entire switch is one broadcast domain)

      2 Hubs + Switch (10 devices):
        Collision domains : 2  (Hub1 = 1 domain, Hub2 = 1 domain; switch ports to hubs are full-duplex)
        Broadcast domains : 1  (switch bridges both hubs into one broadcast domain)

    Implementation note:
      Since the physical layer sends BIT-BY-BIT, the switch must accumulate bits per
      sender port into a buffer. Only when the sender signals completion (completion=True)
      does the switch reconstruct the frame and make a forwarding decision.
    """

    def __init__(self, ports):
        self.dict         = {p: None for p in range(ports)}   # port → device/hub
        self.macTable     = {}                                 # MAC string → port number  (CAM table)
        self.buffer       = {p: [] for p in range(ports)}     # port → accumulated bits
        self.free_ports   = deque(range(ports))
        self.transmitters = set()

    # ------------------------------------------------------------------ connections
    def connect(self, device):
        """Plug a device into a free port. Returns port number, or None if full."""
        # BUG FIX: deque has no .empty() → fixed to len() check
        if len(self.free_ports) == 0:
            return None
        free_port = self.free_ports.popleft()
        self.dict[free_port] = device
        return free_port

    def disconnect(self, port):
        if port is not None:
            self.free_ports.append(port)
            self.dict[port] = None
            self.buffer[port] = []

    # ------------------------------------------------------------------ CSMA helpers
    def is_busy(self):
        return len(self.transmitters) > 0

    def collision(self):
        # Each port is its own collision domain — the switch itself never causes collisions
        return False

    # ------------------------------------------------------------------ frame forwarding
    def transmit(self, senderPort, bit=None, flag=None, completion=None):
        """
        Switch port transmit handler.

        flag=True       → buffer one incoming bit from senderPort
        flag=False      → collision on senderPort → clear its buffer
        completion=True → reconstruct frame, learn MAC, forward intelligently
        """
        if completion:
            self._process_frame(senderPort)

        elif flag:
            # Accumulate bit into per-port buffer
            if senderPort not in self.buffer:
                self.buffer[senderPort] = []
            self.buffer[senderPort].append(bit)

        else:
            # Collision — discard buffered bits for this port
            self.buffer[senderPort] = []

    # ------------------------------------------------------------------ internal
    def _process_frame(self, senderPort):
        """Reconstruct frame from buffer, learn source MAC, forward to correct port(s)."""
        bit_string = ''.join(self.buffer.get(senderPort, []))
        self.buffer[senderPort] = []

        # Minimum Ethernet frame: 6+6+2+0+4 = 18 bytes = 144 bits
        if len(bit_string) < 144:
            return

        # ── Parse destination MAC (bits 0–47) ───────────────────────────────────
        dest_bits  = bit_string[0:48]
        dest_bytes = bytes(int(dest_bits[i:i+8], 2) for i in range(0, 48, 8))
        dest_mac   = ':'.join(f'{b:02X}' for b in dest_bytes)

        # ── Parse source MAC (bits 48–95) and LEARN it ──────────────────────────
        src_bits  = bit_string[48:96]
        src_bytes = bytes(int(src_bits[i:i+8], 2) for i in range(0, 48, 8))
        src_mac   = ':'.join(f'{b:02X}' for b in src_bytes)

        # MAC address learning — add/update CAM table entry
        if src_mac not in self.macTable or self.macTable[src_mac] != senderPort:
            self.macTable[src_mac] = senderPort
            print(f'[Switch] 📖 Learned  {src_mac} → port {senderPort}')

        # ── Forwarding decision ──────────────────────────────────────────────────
        if dest_mac == 'FF:FF:FF:FF:FF:FF':
            # BROADCAST — flood all ports except sender
            targets = [p for p, d in self.dict.items() if p != senderPort and d is not None]
            print(f'[Switch] 📢 Broadcast from port {senderPort} → flooding ports {targets}')

        elif dest_mac in self.macTable:
            # KNOWN UNICAST — forward only to the learned port
            dest_port = self.macTable[dest_mac]
            if dest_port == senderPort or self.dict.get(dest_port) is None:
                return   # destination is on same port or disconnected — filter
            targets = [dest_port]
            print(f'[Switch] 🔀 Unicast  {src_mac} → {dest_mac} via port {dest_port}')

        else:
            # UNKNOWN UNICAST — flood (destination MAC not yet in CAM table)
            targets = [p for p, d in self.dict.items() if p != senderPort and d is not None]
            print(f'[Switch] ❓ Unknown  {dest_mac} — flooding ports {targets}')

        # ── Deliver frame to each target device ─────────────────────────────────
        for port in targets:
            device = self.dict[port]
            if device is not None:
                self._deliver_to_device(device, bit_string)

    def _deliver_to_device(self, device, bit_string):
        """Inject a complete frame's bits directly into a device's physical receiver."""
        device.recieverSidePhysical.tray = list(bit_string)
        device.recieverSidePhysical.transfer()

    def show_cam_table(self):
        """Print current MAC address table — useful for demonstrating MAC learning."""
        print('\n[Switch] ── CAM Table ─────────────────────')
        if not self.macTable:
            print('  (empty)')
        else:
            for mac, port in self.macTable.items():
                print(f'  {mac}  →  port {port}')
        print('────────────────────────────────────────────')