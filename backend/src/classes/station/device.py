from src.utils.mac import giveMacAddress
from src.classes.station.physicalLayer import senderSidePhysical, recieverSidePhysical
from src.classes.station.dataLinkLayer import senderSideDataLink, recieverSideDataLink

class Device:
    companyIdentifier='00:1A:2B'
    def __init__(self,name):
        self.name=name
        self.macAddress=giveMacAddress(Device.companyIdentifier)
        self.port=None
        self.senderSidePhysical=senderSidePhysical(self)
        self.recieverSidePhysical=recieverSidePhysical(self)
        self.senderSideDataLink=senderSideDataLink(self)
        self.recieverSideDataLink = recieverSideDataLink(self)

    def send(self, medium, data, dest_mac="FF:FF:FF:FF:FF:FF"):
        """Implements Sliding Window (Go-Back-N) Flow Control"""
        window_size = 4
        chunk_size = 2 
        
        frames = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        total_frames = len(frames)
        
        print(f"\n[{self.name}] --- Starting Go-Back-N Transmission ---")
        print(f"[{self.name}] Total frames: {total_frames}, Window Size: {window_size}")
        
        base = 0
        while base < total_frames:
            upper_bound = min(base + window_size, total_frames)
            for seq_num in range(base, upper_bound):
                chunk = frames[seq_num]
                print(f"[{self.name}] Sliding Window -> Sending Frame {seq_num}: '{chunk}'")
                
                payload = f"{seq_num}|{chunk}"
                self.senderSideDataLink.conversion(
                    dest=dest_mac, 
                    src=self.macAddress, 
                    length=len(payload), 
                    data=payload, 
                    medium=medium
                )
            
            print(f"[{self.name}] Window sent. Waiting for ACKs... ACKs received. Sliding window forward.")
            base += window_size
            
        print(f"[{self.name}] All data transmitted successfully.\n")