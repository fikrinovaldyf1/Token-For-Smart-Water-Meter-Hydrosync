from functools import reduce
import random
import numpy as np
from datetime import datetime, timedelta

start_date = datetime(2014, 1, 1, 0, 0, 0)
db_date = datetime.now()
date_difference = db_date - start_date
base_date = start_date + date_difference
expiration_date = base_date + timedelta(days=365)

def bin_str(value):
    return bin(value).lstrip('0b')

def concat_str(bin1, bin2, sep=''):
    return sep.join([bin1, bin2])

def bin_pad(binary, length: int):
    binary = str(binary)
    binary_length = len(binary)
    while binary_length < length:
        binary = '0' + binary 
        binary_length += 1
    return binary

token_class = bin_pad(bin_str(0), 2) #[0-3]

def crc16(data: str):
    '''
    CRC-16-ModBus Algorithm
    '''
    inted_data = int(data, base=2)
    hexed_data = hex(inted_data).lstrip('0x')
    bin_padded_hexed_data = bin_pad(hexed_data, 14)
    data = bytearray.fromhex(bin_padded_hexed_data)
    poly = 0xA001
    crc = 0xFFFF
    for b in data:
        crc ^= (0xFF & b)
        for _ in range(0, 8):
            if (crc & 0x0001):
                crc = ((crc >> 1) & 0xFFFF) ^ poly
            else:
                crc = ((crc >> 1) & 0xFFFF)
    
    crc = int(np.uint16(crc))
    return bin_pad(bin_str(crc), 16)

def get_random():
    rnd = random.randint(0, 15)
    return bin_pad(bin_str(rnd), 4)

def get_token_id():
    now = datetime.now()
    delta = now - base_date
    minutes_from_base_date = int(delta.total_seconds() / 60)
    return bin_pad(bin_str(minutes_from_base_date), 24)

def generate_token_block(token_class: int):
    token_class = bin_pad(bin_str(token_class), 2) #[0-3]
    token_order = [token_class, get_random(), get_token_id()]
    crc = crc16(reduce(concat_str, token_order))
    token_order.append(crc)
    token64_order = token_order[1:]
    reduced_token64_order = reduce(concat_str, token64_order)
    print("Data Block:", reduced_token64_order)
    return reduced_token64_order