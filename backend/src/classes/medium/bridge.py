from collections import deque
class BridgeInterface:
    """
    One physical port on a Bridge.

    Mimics the receiver interface of a Device so it can plug into a Hub
    exactly like a regular device. When the hub delivers bits to it, it
    accumulates them and notifies the Bridge when the frame is complete.
    """

    def __init__(self, bridge, side_id):
        self.bridge   = bridge
        self.side_id  = side_id   # 0 = left segment, 1 = right segment
        self.tray     = []
        self.port     = None      # port number assigned by the hub

        # Hub calls device.recieverSidePhysical.receive_bit() / transfer()
        # Point it at self so this object IS its own receiver.
        self.recieverSidePhysical = self

    def receive_bit(self, bit):
        self.tray.append(bit)

    def collision_detected(self):
        self.tray.clear()

    def transfer(self):
        """Hub signals frame complete → pass buffered bits to Bridge for processing."""
        bit_string = ''.join(self.tray)
        self.tray.clear()
        if bit_string:
            self.bridge.process(self.side_id, bit_string)


class Bridge:
    """
    Layer 2 two-port bridge.

    Connects two separate network segments (hubs or direct devices) and
    selectively forwards frames between them based on learned MAC addresses.

    Key behaviours:
      - Address learning : maps source MACs to which side they came from.
      - Filtering        : does NOT forward frames whose destination is on the
                           same segment as the source (avoids unnecessary traffic).
      - Flooding         : forwards to the other side when destination is unknown.
      - Broadcast        : always forwards broadcast frames to the other side.

    Domain analysis:
      - Collision domains : 2  (each segment is independent — bridge separates them)
      - Broadcast domains : 1  (bridge connects both segments into one broadcast domain)

    Usage:
        hub1 = Hub(5)
        hub2 = Hub(5)
        bridge = Bridge()
        bridge.connect(hub1, side=0)
        bridge.connect(hub2, side=1)
    """

    def __init__(self):
        self.macTable   = {}                          # MAC → side_id (0 or 1)
        self.interfaces = [BridgeInterface(self, 0),  # left  port
                           BridgeInterface(self, 1)]  # right port
        self.hubs       = [None, None]                # hub/device on each side

    # ------------------------------------------------------------------ setup
    def connect(self, hub, side):
        """
        Plug bridge port into a hub (or cable).
        The bridge interface registers itself as a device on the hub.

        Args:
            hub  : Hub (or Cable) instance
            side : 0 for left segment, 1 for right segment
        Returns:
            port number assigned by the hub, or None if hub is full
        """
        iface = self.interfaces[side]
        port  = hub.connect(iface)        # hub stores iface in its port table
        iface.port   = port
        self.hubs[side] = hub
        return port

    # ------------------------------------------------------------------ frame processing
    def process(self, incoming_side, bit_string):
        """
        Called by a BridgeInterface when a complete frame has been received.
        Makes the forwarding/filtering decision.
        """
        if len(bit_string) < 144:   # minimum 18-byte frame
            return

        # ── Read destination MAC (bits 0–47) ────────────────────────────────────
        dest_bits  = bit_string[0:48]
        dest_bytes = bytes(int(dest_bits[i:i+8], 2) for i in range(0, 48, 8))
        dest_mac   = ':'.join(f'{b:02X}' for b in dest_bytes)

        # ── Read source MAC (bits 48–95) and LEARN which side it is on ──────────
        src_bits  = bit_string[48:96]
        src_bytes = bytes(int(src_bits[i:i+8], 2) for i in range(0, 48, 8))
        src_mac   = ':'.join(f'{b:02X}' for b in src_bytes)

        if src_mac not in self.macTable or self.macTable[src_mac] != incoming_side:
            self.macTable[src_mac] = incoming_side
            print(f'[Bridge] 📖 Learned {src_mac} → side {incoming_side}')

        other_side = 1 - incoming_side

        # ── Forwarding decision ──────────────────────────────────────────────────
        if dest_mac == 'FF:FF:FF:FF:FF:FF':
            forward = True
            print(f'[Bridge] 📢 Broadcast — forwarding to side {other_side}')

        elif dest_mac in self.macTable:
            if self.macTable[dest_mac] == incoming_side:
                # Destination is on the SAME side → filter (do not forward)
                forward = False
                print(f'[Bridge] 🚫 Filtering {dest_mac} — already on side {incoming_side}')
            else:
                forward = True
                print(f'[Bridge] 🔀 Forwarding {dest_mac} to side {other_side}')
        else:
            # Unknown destination → flood to the other side
            forward = True
            print(f'[Bridge] ❓ Unknown {dest_mac} — forwarding to side {other_side}')

        if not forward:
            return

        # ── Deliver frame to the other segment ──────────────────────────────────
        other_hub = self.hubs[other_side]
        if other_hub is None:
            return

        bridge_sender_port = self.interfaces[other_side].port

        for port, device in other_hub.dict.items():
            if port == bridge_sender_port or device is None:
                continue
            if hasattr(device, 'recieverSidePhysical'):
                # Regular Device
                device.recieverSidePhysical.tray = list(bit_string)
                device.recieverSidePhysical.transfer()
            # (BridgeInterface objects would have recieverSidePhysical = self,
            #  but we don't chain bridges in this simulation)

    def show_mac_table(self):
        """Print the bridge's MAC address table."""
        print('\n[Bridge] ── MAC Table ──────────────────────')
        if not self.macTable:
            print('  (empty)')
        else:
            for mac, side in self.macTable.items():
                print(f'  {mac}  →  side {side}')
        print('────────────────────────────────────────────')