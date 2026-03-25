# def encodeData(dataword,generator='10011'):
#     temp=[0]*len(dataword)
#     for i in range(0,len(dataword)):
#         temp[i]=dataword[i]
#     temp.extend(['0']*(len(generator)-1))

#     index=None

#     for i in range(0,len(temp)):
#         if((len(temp)-i) < len(generator)):
#             index=i
#             break
#         else:
#             k=i+1
#             if(temp[i]=='1'):
#                 for j in range(1,len(generator)):
#                     if(temp[k]==generator[j]):
#                         temp[k]='0'
#                     else:
#                         temp[k]='1'
#                     k=k+1
                
#             else:
#                 if(generator[0]=='0'):
#                     for j in range(1,len(generator)):
#                         if(temp[k]==generator[j]):
#                             temp[k]='0'
#                         else:
#                             temp[k]='1'
#                         k=k+1
#                 else:
#                     for j in range(1,len(generator)):
#                         if(temp[k]=='0'):
#                             temp[k]='0'
#                         else:
#                             temp[k]='1'
#                         k=k+1
    
#     crc=[]
#     for i in range(index,len(temp)):
#         crc.append(temp[i])
#     return ''.join(crc)

def encodeData(dataword, generator='10011'):
    """
    Computes CRC remainder using binary XOR long division.

    Args:
        dataword  : string of '0'/'1' characters  e.g. "0110100001100101"
        generator : polynomial string              e.g. "10011"  (default CRC-4 style)

    Returns:
        crc_bits  : string of '0'/'1' — the remainder, length = len(generator)-1
                    e.g. "1011"

    Usage in Data Link layer:
        data_bits = bytes_to_bits(data.encode())
        crc_bits  = encodeData(data_bits)          # → e.g. "1011"
        crc_int   = int(crc_bits, 2)               # → integer for frame storage
    """
    # Copy dataword into mutable list and append (len(generator)-1) zeros
    temp = list(dataword)
    temp.extend(['0'] * (len(generator) - 1))

    index = None

    for i in range(len(temp)):
        if (len(temp) - i) < len(generator):
            index = i
            break

        k = i + 1

        if temp[i] == '1':
            # XOR current window with generator bits 1..end
            for j in range(1, len(generator)):
                temp[k] = '0' if (temp[k] == generator[j]) else '1'
                k += 1
        else:
            if generator[0] == '0':
                # Generator also starts with 0 — still XOR
                for j in range(1, len(generator)):
                    temp[k] = '0' if (temp[k] == generator[j]) else '1'
                    k += 1
            else:
                # Current bit is 0, generator starts with 1 → no subtraction (identity)
                for j in range(1, len(generator)):
                    temp[k] = '0' if temp[k] == '0' else '1'   # no-op: preserves value
                    k += 1

    return ''.join(temp[index:])