import random

def giveMacAddress(companyIdentifier):
    """
    Generates a unique 48-bit MAC address.
    Format: companyIdentifier (OUI) + 3 random octets
    Example: 00:1A:2B:3C:4D:5E
    """
    macAddress = companyIdentifier
    digits = '0123456789ABCDEF'
    for _ in range(3):
        idx1 = random.randint(0, 15)   # BUG FIX: was randint(0,16) → index 16 doesn't exist in digits[0..15]
        idx2 = random.randint(0, 15)
        macAddress += f':{digits[idx1]}{digits[idx2]}'
    return macAddress