from src.utils.encode import encodeData
from src.utils.decode import decodeData

# CRC configuration — must match in both sender and receiver
GENERATOR   = '10011'
CRC_BITS    = len(GENERATOR) - 1   # = 4 bits for generator '10011'
CRC_BYTES   = 4                     # bytes reserved in frame for CRC field


class senderSideDataLink:
    def __init__(self, device):
        self.device = device


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


    def conversion(self, dest_mac, src_mac, length, data, medium):
        """
        Builds an Ethernet-like frame and passes it to the Physical layer.

        Frame layout (bytes):
          [dest_mac: 6][src_mac: 6][length: 2][data: N][crc: 4]

        CRC computation:
          BUG FIX (original): encodeData(data) passed raw text → encodeData expects bit string
          FIX: convert data → bytes → bit string → THEN compute CRC
        """
        data_bytes = self._data_to_bytes(data)
        data_bits  = self._bytes_to_bits(data_bytes)

        # Compute CRC over the data bit-string
        crc_bits = encodeData(data_bits, GENERATOR)          # returns e.g. "1011"
        crc_int  = int(crc_bits, 2) if crc_bits else 0      # convert to int for storage
        # BUG FIX (original): crc_to_bytes(crc) where crc was a STRING → int.to_bytes() on a string → TypeError
        # FIX: crc_int is now a proper integer

        # Assemble frame bytes
        frame_bytes = (
            self._mac_to_bytes(dest_mac)    +   # 6 bytes
            self._mac_to_bytes(src_mac)     +   # 6 bytes
            self._length_to_bytes(length)   +   # 2 bytes
            data_bytes                      +   # N bytes
            self._crc_int_to_bytes(crc_int)     # 4 bytes
        )

        bits_string = self._bytes_to_bits(frame_bytes)

        print(f'\n[{self.device.name}] ── SENDING ──────────────────────────────')
        print(f'  src  : {src_mac}')
        print(f'  dst  : {dest_mac}')
        print(f'  data : "{data}"')
        print(f'  CRC  : {crc_bits} (= {crc_int})')
        print(f'  frame: {len(frame_bytes)} bytes / {len(bits_string)} bits')

        self.device.senderSidePhysical.transmitToMedium(bits_string, medium)


class recieverSideDataLink:
    def __init__(self, device):
        self.device = device

    
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

        BUG FIX: method was named 'recieve' (typo) — now consistently 'receive'
        physicalLayer.py's transfer() also updated to call .receive()
        """
        # Minimum frame size check: 6+6+2+0+4 = 18 bytes = 144 bits
        if len(bits_string) < 144:
            print(f'[{self.device.name}] Frame too short ({len(bits_string)} bits) — discarded.')
            return False

        byte_string = self._bits_to_bytes(bits_string)

        # --- Parse frame fields ---
        dest_mac = self._bytes_to_mac(byte_string[0:6])
        src_mac  = self._bytes_to_mac(byte_string[6:12])
        length   = int.from_bytes(byte_string[12:14], 'big')
        data     = byte_string[14:14 + length]
        crc      = byte_string[14 + length: 14 + length + CRC_BYTES]

        crc_int  = int.from_bytes(crc, 'big')
        data_str = data.decode('utf-8', errors='replace')

        # --- Step 1: MAC Address Check ---
        is_broadcast = (dest_mac == 'FF:FF:FF:FF:FF:FF')
        is_mine      = (dest_mac == self.device.macAddress.upper())

        if not is_broadcast and not is_mine:
            # Frame addressed to someone else — silently discard (normal switch behaviour)
            return False
    
        data_bits = self._bytes_to_bits(data)
        crc_bits  = format(crc_int, f'0{CRC_BITS}b') 
        codeword  = data_bits + crc_bits
        valid, _  = decodeData(codeword, GENERATOR)

        print(f'\n[{self.device.name}] ── RECEIVED ─────────────────────────────')
        print(f'  src  : {src_mac}')
        print(f'  dst  : {dest_mac} {"(broadcast)" if is_broadcast else "(unicast)"}')
        print(f'  data : "{data_str}"')
        print(f'  CRC  : {crc_bits} → {"VALID" if valid else " ERROR DETECTED"}')

        return valid