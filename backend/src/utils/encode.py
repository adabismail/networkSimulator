def encodeData(dataword,generator='10011'):
    temp=[0]*len(dataword)
    for i in range(0,len(dataword)):
        temp[i]=dataword[i]
    temp.extend(['0']*(len(generator)-1))

    index=None

    for i in range(0,len(temp)):
        if((len(temp)-i) < len(generator)):
            index=i
            break
        else:
            k=i+1
            if(temp[i]=='1'):
                for j in range(1,len(generator)):
                    if(temp[k]==generator[j]):
                        temp[k]='0'
                    else:
                        temp[k]='1'
                    k=k+1
                
            else:
                if(generator[0]=='0'):
                    for j in range(1,len(generator)):
                        if(temp[k]==generator[j]):
                            temp[k]='0'
                        else:
                            temp[k]='1'
                        k=k+1
                else:
                    for j in range(1,len(generator)):
                        if(temp[k]=='0'):
                            temp[k]='0'
                        else:
                            temp[k]='1'
                        k=k+1
    
    crc=[]
    for i in range(index,len(temp)):
        crc.append(temp[i])
    return ''.join(crc)