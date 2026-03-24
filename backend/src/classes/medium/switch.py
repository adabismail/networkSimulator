from collections import deque
class Switch:
    def __init__(self,ports):
        self.dict={}
        self.macTable={}
        self.free_ports=deque(range(ports))
        self.transmitters=set()

        for port in range(0,ports):
            self.dict[port]=None

    def connect(self,device):
        if len(self.free_ports) == 0:
            return None
        else:
            free_port=self.free_ports.popleft()
            self.dict[free_port]=device
            device.port = free_port
            return free_port

    def disconnect(self,port):
        if port is not None and self.dict.get(port) is not None:
            self.free_ports.append(port)
            self.dict[port]=None
    
    # def is_busy(self):
    #     return len(self.transmitters)>0

    # def collision(self):
    #     return len(self.transmitters)>1
    
    # def transmit(self,senderPort,frame):
    #     reciever=frame["dest_mac"]
    #     if(self.macTable[reciever]!=None):
    #         flag=False
    #         while(not(flag)):
    #             flag=self.macTable[reciever].recieve(frame)
    #     else:
    #         flag=False
    #         while(not(flag)):
    #             for port in self.dict:
    #                 if(port!=senderPort):
    #                     flag=self.dict[port].recieve(frame)
    #                     if(flag):
    #                         self.macTable[reciever]=self.dict[port]
    #                         break

    def transmit(self, senderPort, frame_dict):
        src_mac = frame_dict["src_mac"]
        dest_mac = frame_dict["dest_mac"]

        if src_mac not in self.macTable:
            self.macTable[src_mac] = senderPort
            print(f"[Switch] Learned MAC {src_mac} on Port {senderPort}")

        if dest_mac in self.macTable:
            target_port = self.macTable[dest_mac]
            
            if target_port != senderPort: 
                target_device = self.dict[target_port]
                if target_device:
                    print(f"[Switch] Forwarding frame to Port {target_port}")
        else:
            print(f"[Switch] MAC {dest_mac} unknown. Flooding out all other ports.")
            for port, target_device in self.dict.items():
                if port != senderPort and target_device is not None:
                    pass
