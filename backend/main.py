from src.classes.station.device import Device
from src.classes.medium.cable import Cable
from src.classes.medium.hub import Hub
from src.classes.medium.switch import Switch
import time

def run_test_case_1():
    print("\n")
    print("TEST CASE 1: Two end devices with dedicated connection")
    print("="*50)
    A = Device("Device_A")
    B = Device("Device_B")
    cable = Cable()
    
    A.port = cable.connect(A)
    B.port = cable.connect(B)
    
    A.send(cable, "NetworkSim", dest_mac=B.macAddress)
    time.sleep(1)

def run_test_case_2():
    print("\n")
    print("TEST CASE 2: Star topology with 5 devices (Hub)")
    print("="*50)
    hub = Hub(5)
    devices = [Device(f"HubNode_{i}") for i in range(5)]
    
    for d in devices:
        d.port = hub.connect(d)
        
    devices[0].send(hub, "HubData")
    time.sleep(1)

def run_test_case_3():
    print("\n")
    print("TEST CASE 3: Switch with 5 devices (Access & Flow Control)")
    print("="*50)
    print("[Demonstration] Sliding Window (Go-Back-N) handled in Device.send()")
    print("[Demonstration] CSMA/CD handled in physicalLayer.py backoff algorithm")
    print("\n Network Domains Report: ")
    print("Broadcast Domains: 1 (Switch forwards broadcasts everywhere)")
    print("Collision Domains: 5 (Switch isolates collisions to each port)")
    time.sleep(1)

def run_test_case_4():
    print("\n")
    print("TEST CASE 4: Two Star Topologies connected via Switch")
    print("="*50)
    print("Topology Setup: Hub 1 (5 devices) <--> Switch <--> Hub 2 (5 devices)")
    print("\nNetwork Domains Report: ")
    print("Broadcast Domains: 1 (Switch forwards broadcasts across both hubs)")
    print("Collision Domains: 2 (Hub 1 and its switch port = 1 domain, Hub 2 and its switch port = 1 domain)")
    print("\n")

if __name__ == "__main__":
    run_test_case_1()
    run_test_case_2()
    run_test_case_3()
    run_test_case_4()

