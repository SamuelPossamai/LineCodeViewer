
#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_ami_B8ZS_base(binary_list, init_cond, is_B8ZS):
    
    last = 1 if init_cond else -1
    zeroes = 0
    
    result = []
    for bit in binary_list:
        
        if bit: 
            zeroes = 0
            last = -last;
            code_value = last
        else:
            zeroes += 1
            code_value = 0
        
        result.append(code_value)
        
        if is_B8ZS and zeroes == 8:
            result[-5] = result[-1] = last
            result[-4] = result[-2] = -last
            zeroes = 0;
    
    return result

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_ami(binary_list, init_cond):
    
    return generate_ami_B8ZS_base(binary_list, init_cond, False)

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_machester_differential(binary_list, init_cond):

    result = [int(init_cond)]
    for bit in binary_list:
        result.append(result[-1] if bit else (result[-1] + 1)%2)
        result.append(0 if result[-1] else 1)
    
    return result[1:];

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_manchester(binary_list, _):
    
    result = []
    for bit in binary_list:
        result.append(0 if bit else 1)
        result.append(bit)
    
    return result;

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_nrz_polar(binary_list, _):
    
    return [ -1 if bit else 1 for bit in binary_list ]


#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_rz(binary_list, _):
    
    result = [0]*len(binary_list)*2
    
    for i in range(len(binary_list)):
        result[2*i] = 1 if binary_list[i] else -1
    
    return result

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_B8ZS(binary_list, init_cond):
    
    return generate_ami_B8ZS_base(binary_list, init_cond, True)

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_2B1Q(binary_list, _):
    
    result = []
    for i in range(0, len(binary_list)-1, 2):
        result.append(1 if binary_list[i] else -1)
        if binary_list[i+1] == 0:
            result[-1] *= 3
    
    return result

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#

def generate_MLT3(binary_list, init_cond):
    
    growing = ( init_cond == 1 )
    
    if init_cond == 0:
        last = 1
    elif init_cond == 3:
        last = -1
    else:
        last = 0
    
    result = []
    for bit in binary_list:
        if bit:
            if growing:
                last += 1
            else:
                last -= 1
            
            if last > 1 or last < -1:
                last = 0
                growing = not growing
        
        result.append(last)
    
    return result

#-------------------------#-------------------------#-------------------------#-------------------------#-------------------------#
