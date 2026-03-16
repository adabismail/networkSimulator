from src.utils.encode import encodeData
from src.utils.decode import decodeData

class senderSideDataLink:
    def __init__(self,device):
        self.device=device
    
    def conversion(self,dest,src,length,data,medium):
        def mac_to_bytes(mac):
            return bytes.fromhex(mac.replace(":",""))

        def length_to_bytes(length):
            return length.to_bytes(2,'big')

        def data_to_bytes(data):
            return data.encode()

        def crc_to_bytes(crc):
            return crc.to_bytes(4,'big')

        def bytes_to_bits(byte_data):
            return ''.join(format(byte,'08b')for byte in byte_data)
        
        crc=encodeData(data)
        frame={
            'dest_mac':mac_to_bytes(dest),
            'src_mac':mac_to_bytes(src),
            'length':length_to_bytes(length),
            'data':data_to_bytes(data),
            'crc':crc_to_bytes(crc)
        }
        
        byte_string=frame["dest_mac"]+frame["src_mac"]+frame['length']+frame["data"]+frame['crc']
        bits_string=bytes_to_bits(byte_string)
        self.callSenderPhysical(bits_string,medium)
    
    def callSenderPhysical(self,bit_string,medium):
        self.device.senderSidePhysical.transmitToMedium(bit_string,medium)

class recieverSideDataLink:
    def __init__(self,device):
        self.device=device
        
    def recieve(self,bits_string):
        def bits_to_bytes(bit_string):
            return bytes(
                int(bit_string[i:i+8],2)
                for i in range(0,len(bit_string),8)
            )
        byte_string=bits_to_bytes(bits_string)

        dest=byte_string[0:6]
        src=byte_string[6:12]

        length=byte_string[12:14]
        length=int.from_bytes(length,'big')
        
        data=byte_string[14:14+length]
        crc=byte_string[14+length:]

        crc=int.from_bytes(crc,'big')
        dest=':'.join(f'{b:02X}' for b in dest)
        src=':'.join(f'{b:02X}' for b in src)
        data=data.decode()

        frame={
            "dest_mac":dest,
            "src_mac":src,
            "length":length,
            "data":data,
            "crc":crc
        }

        # Now checking here(Error detection and control,mac address matching).
        # Returns true if mac address matches and no error, else false.
    
    