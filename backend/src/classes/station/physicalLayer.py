import time
import random

class senderSidePhysical:
    def __init__(self,device):
        self.device=device
        self.k=0
    
    def transmitToMedium(self,bits_string,medium):
        if self.device.port!=None:
            while(self.k<=15):
                while medium.is_busy():
                  pass
                medium.transmitters.add(self.device)

                flag=True
                for bit in bits_string:
                    if medium.collision():
                        flag=False
                        break
                    else:
                        medium.transmit(self.device.port,bit)
                        time.sleep(1)
                if(flag):
                    medium.transmit(self.device.port,True)
                    return
                else:
                    # Collision detected
                    medium.transmit(self.device.port,not(flag))
                    medium.transmitters.remove(self.device)
                    # Send jamming signal to the medium.
                    self.k=self.k+1
                    # Wait for backoff time.
                    Tfr=len(bits_string)
                    time.sleep(random.randint(0,2**self.k -1)*Tfr)

class recieverSidePhysical:
    def __init__(self,device):
       self.device=device
       self.tray=[]

    def receive_bit(self,bit):
        self.tray.append(bit)

    def collision_detected(self):
        self.tray.clear()

    def transfer(self):
        bit_string="".join(self.tray)
        self.tray.clear()
        # Pass bits to reciever datalink layer.
        self.device.recieverSideDatalink.receive(bit_string)