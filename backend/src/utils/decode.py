def decodeData(codeword, generator='10011'):
    """
    Verifies CRC by dividing codeword by generator and checking remainder is zero.

    Args:
        codeword  : string of '0'/'1' — data bits + CRC bits concatenated
                    e.g. "01101000...1011"
        generator : same polynomial used during encoding  e.g. "10011"

    Returns:
        (True,  dataword_bits)  if remainder is all zeros  → no error
        (False, "1")            if remainder has a 1-bit   → error detected

    Usage in Data Link layer:
        data_bits = bytes_to_bits(data_bytes)
        crc_bits  = format(crc_int, '04b')         # 4 bits for generator '10011'
        codeword  = data_bits + crc_bits
        valid, _  = decodeData(codeword)
    """
    dividend = list(codeword)
    temp = dividend.copy()
    index = None

    for i in range(len(temp)):
        if (len(temp) - i) < len(generator):
            index = i
            break

        k = i + 1

        if temp[i] == '1':
            for j in range(1, len(generator)):
                temp[k] = '0' if (temp[k] == generator[j]) else '1'
                k += 1
        else:
            if generator[0] == '0':
                for j in range(1, len(generator)):
                    temp[k] = '0' if (temp[k] == generator[j]) else '1'
                    k += 1
            else:
                for j in range(1, len(generator)):
                    temp[k] = '0' if temp[k] == '0' else '1'   # no-op
                    k += 1

    # Check remainder — must be all zeros for a valid frame
    for i in range(index, len(temp)):
        if temp[i] != '0':
            return False, "1"

    dataword = ''.join(dividend[:index])
    return True, dataword