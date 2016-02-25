import struct 

def split_stereo(s):
    i = 0
    l = len(s)
    result_left = []
    result_right = []
    sample_width = 2
    while i < l:
        sample = s[i:i + sample_width]
        result_left.append(sample)
        i += sample_width
        sample = s[i:i + sample_width]
        result_right.append(sample)
        i += sample_width
        
    return b"".join(result_left), b"".join(result_right)

def join_stereo(sl, sr):
    result = []
    sample_width = 2
    i = 0
    l = len(sl)
    while i < l:
        result.append(sl[i:i + sample_width])
        result.append(sr[i:i + sample_width])
        i += sample_width
    return b"".join(result)
    

def str_to_list(s):
    i = 0
    l = len(s)
    result = []
    sample_width = 2
    while i < l:
        sample = struct.unpack('h', s[i:i + sample_width])[0]
        result.append(sample)
        i += sample_width
    return result
    
    
def str_to_list_stereo(s):
    i = 0
    l = len(s)
    result_left = []
    result_right = []
    sample_width = 2
    while i < l:
        sample = struct.unpack('h', s[i:i + sample_width])[0]
        result_left.append(sample)
        i += sample_width
        sample = struct.unpack('h', s[i:i + sample_width])[0]
        result_right.append(sample)
        i += sample_width
        
    return result_left, result_right
    
    
def list_to_str(l):
    result = []
    for sample in l:
        result.append(struct.pack('h', sample))
    return b"".join(result)

    
def list_to_str_stereo(l_left, l_right):
    result = []
    for sample_left, sample_right in zip(l_left, l_right):
        result.append(struct.pack('h', sample_left))
        result.append(struct.pack('h', sample_right))
    return b"".join(result)
    


def complete_silence(pattern, offset, length):
    d = b"\0\0"
    return (d * offset) + pattern + d * (length - offset - len(pattern) // 2)

