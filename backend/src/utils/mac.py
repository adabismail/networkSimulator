import random
def giveMacAddress(companyIdentifier):
    # unique 48 bit mac address each time it is called.
    macAddress=companyIdentifier
    digits='0123456789ABCDEF'
    for i in range(0,3):
        idx1=random.randint(0,15)
        idx2=random.randint(0,15)
        macAddress+=f':{digits[idx1]}{digits[idx2]}'
    return macAddress