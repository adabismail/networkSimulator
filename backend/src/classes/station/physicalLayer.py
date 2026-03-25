import time
import random


class senderSidePhysical:
    def __init__(self, device):
        self.device = device

    def transmitToMedium(self, bits_string, medium):
        """
        CSMA/CD with Binary Exponential Backoff.

        Algorithm:
          1. Wait until medium is free (carrier sense).
          2. Begin transmitting bit-by-bit.
          3. If collision detected mid-transmission → send jam, back off, retry.
          4. Max 16 attempts (k = 0..15). On 16th failure → drop frame.
          5. On success → signal completion so receivers know frame is done.
        """
        if self.device.port is None:
            print(f'[{self.device.name}] ERROR: Device has no port assigned.')
            return

        k = 0   # Backoff exponent — LOCAL per transmission call, resets each time

        while k <= 15:
            # --- Step 1: Carrier Sense — wait until medium is idle ---
            while medium.is_busy():
                time.sleep(0.001)

            # --- Step 2: Start transmitting, add self to active transmitters ---
            medium.transmitters.add(self.device)

            success = True
            for bit in bits_string:
                # --- Collision Detection: check if another transmitter joined ---
                if medium.collision():
                    success = False
                    break

                # Send one bit to all receivers on the medium
                # BUG FIX: was medium.transmit(port, bit) → positional arg mapped to 'bit'
                # but flag=None so hub fell to else branch → collision_detected() fired on EVERY bit
                # FIX: use keyword argument flag=True to signal this is a normal data bit
                medium.transmit(self.device.port, bit=bit, flag=True)
                time.sleep(0.01)   # Propagation delay simulation (reduced from 1s)

            if success:
                # --- Step 5: Transmission complete — notify all receivers to assemble frame ---
                medium.transmitters.discard(self.device)   # BUG FIX: original code forgot to remove on success
                medium.transmit(self.device.port, completion=True)
                return
            else:
                # --- Step 3: Collision — send jam signal, remove from transmitters, back off ---
                medium.transmit(self.device.port, flag=False)   # flag=False → collision_detected()
                medium.transmitters.discard(self.device)

                k += 1
                Tfr = len(bits_string) * 0.01
                backoff_slots = random.randint(0, 2**k - 1)
                print(f'[{self.device.name}] Collision! Attempt {k}/16. Backing off {backoff_slots} slots.')
                time.sleep(backoff_slots * Tfr)

        print(f'[{self.device.name}] TRANSMISSION FAILED after 16 attempts — frame dropped.')


class recieverSidePhysical:
    def __init__(self, device):
        self.device = device
        self.tray = []   # Accumulates incoming bits until frame is complete

    def receive_bit(self, bit):
        """Called by medium for each incoming bit."""
        self.tray.append(bit)

    def collision_detected(self):
        """Called by medium when a collision is detected — discard partial frame."""
        self.tray.clear()

    def transfer(self):
        """
        Called by medium when sender signals transmission complete.
        Assembles all buffered bits into a bit-string and passes up to Data Link layer.
        """
        bit_string = ''.join(self.tray)
        self.tray.clear()
        if bit_string:
            # BUG FIX: was self.device.recieverSideDatalink.receive(bit_string)
            # Correct attribute name: recieverSideDataLink  (capital L)
            # Correct method name:    receive  (not recieve)
            self.device.recieverSideDataLink.receive(bit_string)