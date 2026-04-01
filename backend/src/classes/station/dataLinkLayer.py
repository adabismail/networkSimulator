from src.utils.encode import encodeData
from src.utils.decode import decodeData

# CRC configuration — must match in both sender and receiver
GENERATOR   = '10011'
CRC_BITS    = len(GENERATOR) - 1   # = 4 bits for generator '10011'
CRC_BYTES   = 4                     # bytes reserved in frame for CRC field


class senderSideDataLink:
    def __init__(self, device):
        self.device = device
        # --- NEW: GBN Sender State ---
        self.window_size = 4
        self.base = 0
        self.next_seq_num = 0
        self.window_buffer = {}  # seq_num -> bits_string (for retransmission)

    @staticmethod
    def _mac_to_bytes(mac):
        return bytes.fromhex(mac.replace(':', ''))

    @staticmethod
    def _length_to_bytes(length):
        return length.to_bytes(2, 'big')

    @staticmethod
    def _data_to_bytes(data):
        return data.encode('utf-8')

    @staticmethod
    def _bytes_to_bits(byte_data):
        return ''.join(format(byte, '08b') for byte in byte_data)

    @staticmethod
    def _crc_int_to_bytes(crc_int):
        return crc_int.to_bytes(CRC_BYTES, 'big')

    # --- NEW: Helper for single byte headers ---
    @staticmethod
    def _int_to_byte(val):
        return val.to_bytes(1, 'big')

    # --- CHANGED: Added frame_type and seq_num parameters with defaults ---
    def conversion(self, dest_mac, src_mac, length, data, medium, frame_type=0, seq_num=None):
        """
        Builds an Ethernet-like frame and passes it to the Physical layer.

        Frame layout (bytes):
          [dest_mac: 6][src_mac: 6][type: 1][seq: 1][length: 2][data: N][crc: 4]
        """
        # --- NEW: Auto-assign sequence number for new DATA frames ---
        if frame_type == 0 and seq_num is None:
            seq_num = self.next_seq_num
            self.next_seq_num += 1

        data_bytes = self._data_to_bytes(data)
        
        # --- CHANGED: Assemble bytes WITHOUT CRC first to calculate CRC over header ---
        header_payload = (
            self._mac_to_bytes(dest_mac)    +   # 6 bytes
            self._mac_to_bytes(src_mac)     +   # 6 bytes
            self._int_to_byte(frame_type)   +   # 1 byte  <-- NEW
            self._int_to_byte(seq_num)      +   # 1 byte  <-- NEW
            self._length_to_bytes(length)   +   # 2 bytes
            data_bytes                          # N bytes
        )
        
        # --- CHANGED: Compute CRC over the header+payload bit-string ---
        data_bits = self._bytes_to_bits(header_payload)
        crc_bits = encodeData(data_bits, GENERATOR)          # returns e.g. "1011"
        crc_int  = int(crc_bits, 2) if crc_bits else 0      # convert to int for storage

        # --- CHANGED: Assemble final frame bytes ---
        frame_bytes = header_payload + self._crc_int_to_bytes(crc_int)
        bits_string = self._bytes_to_bits(frame_bytes)

        # --- NEW: GBN buffering ---
        if frame_type == 0:
            self.window_buffer[seq_num] = bits_string

        # --- CHANGED: Print statements to reflect Type and Seq ---
        type_str = "ACK" if frame_type == 1 else "DATA"
        print(f'\n[{self.device.name}] ── SENDING {type_str} (Seq: {seq_num}) ─────────')
        print(f'  src  : {src_mac}')
        print(f'  dst  : {dest_mac}')
        print(f'  data : "{data}"')
        print(f'  CRC  : {crc_bits} (= {crc_int})')
        print(f'  frame: {len(frame_bytes)} bytes / {len(bits_string)} bits')

        self.device.senderSidePhysical.transmitToMedium(bits_string, medium)

    # --- NEW: Handle incoming ACKs ---
    def receive_ack(self, ack_num):
        print(f'[{self.device.name}] 🔄 Sliding Window: Received ACK {ack_num}')
        self.base = ack_num + 1
        keys_to_remove = [seq for seq in self.window_buffer if seq <= ack_num]
        for k in keys_to_remove:
            del self.window_buffer[k]


class recieverSideDataLink:
    def __init__(self, device):
        self.device = device
        # --- NEW: GBN Receiver State ---
        self.expected_seq = 0

    @staticmethod
    def _bits_to_bytes(bit_string):
        return bytes(
            int(bit_string[i:i+8], 2)
            for i in range(0, len(bit_string), 8)
        )

    @staticmethod
    def _bytes_to_bits(byte_data):
        return ''.join(format(byte, '08b') for byte in byte_data)

    @staticmethod
    def _bytes_to_mac(b):
        return ':'.join(f'{x:02X}' for x in b)

    def receive(self, bits_string):
        """
        Parses incoming frame, checks MAC address, verifies CRC.
        Returns True if frame is accepted, False otherwise.
        """
        # --- CHANGED: Minimum frame size check: 6+6+1+1+2+0+4 = 20 bytes = 160 bits ---
        if len(bits_string) < 160:
            print(f'[{self.device.name}] Frame too short ({len(bits_string)} bits) — discarded.')
            return False

        byte_string = self._bits_to_bytes(bits_string)

        # --- CHANGED: Parse frame fields (shifted by 2 bytes for Type and Seq) ---
        dest_mac   = self._bytes_to_mac(byte_string[0:6])
        src_mac    = self._bytes_to_mac(byte_string[6:12])
        frame_type = byte_string[12]                               # <-- NEW
        seq_num    = byte_string[13]                               # <-- NEW
        length     = int.from_bytes(byte_string[14:16], 'big')
        data       = byte_string[16:16 + length]
        crc        = byte_string[16 + length: 16 + length + CRC_BYTES]

        crc_int  = int.from_bytes(crc, 'big')
        data_str = data.decode('utf-8', errors='replace')

        # --- Step 1: MAC Address Check ---
        is_broadcast = (dest_mac == 'FF:FF:FF:FF:FF:FF')
        is_mine      = (dest_mac == self.device.macAddress.upper())

        if not is_broadcast and not is_mine:
            # Frame addressed to someone else — silently discard (normal switch behaviour)
            return False
    
        # --- CHANGED: Verify CRC against the new header+payload length ---
        header_payload_bytes = byte_string[:16 + length]
        data_bits = self._bytes_to_bits(header_payload_bytes)
        crc_bits  = format(crc_int, f'0{CRC_BITS}b') 
        codeword  = data_bits + crc_bits
        valid, _  = decodeData(codeword, GENERATOR)

        # --- CHANGED: Move print statements up so we see the frame type ---
        type_str = "ACK" if frame_type == 1 else "DATA"
        print(f'\n[{self.device.name}] ── RECEIVED {type_str} (Seq: {seq_num}) ────────')
        print(f'  src  : {src_mac}')
        print(f'  dst  : {dest_mac} {"(broadcast)" if is_broadcast else "(unicast)"}')
        print(f'  data : "{data_str}"')
        print(f'  CRC  : {crc_bits} → {"VALID" if valid else " ERROR DETECTED"}')

        if not valid:
            return False

        # --- NEW: Flow Control Logic (Go-Back-N) ---
        if frame_type == 1:
            # It's an ACK frame. Slide the sender's window.
            self.device.senderSideDataLink.receive_ack(seq_num)
            return True

        if frame_type == 0:
            # It's a DATA frame. Check sequence number.
            if seq_num == self.expected_seq:
                print(f'[{self.device.name}] ✅ In-order frame accepted.')
                self.expected_seq += 1
            else:
                print(f'[{self.device.name}] ⚠️ Out-of-order frame (Expected {self.expected_seq}, Got {seq_num}). Discarding.')

            # Always ACK the highest in-order frame successfully received
            ack_to_send = self.expected_seq - 1
            if ack_to_send >= 0:
                print(f'[{self.device.name}] ✉️ Generating ACK {ack_to_send} for {src_mac}')
                if self.device.medium is not None:
                    self.device.senderSideDataLink.conversion(
                        dest_mac=src_mac,
                        src_mac=self.device.macAddress,
                        length=0,
                        data="",
                        medium=self.device.medium, 
                        frame_type=1, 
                        seq_num=ack_to_send
                    )
                else:
                    print(f'[{self.device.name}] ❌ Cannot send ACK. Device has no medium assigned.')

        return valid