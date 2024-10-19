from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from datetime import datetime

def generate_vending_key():
    vending_key = get_random_bytes(8)
    return vending_key

def generate_decoder_key(meter_number, key_expired_number=None):
    key_type = 2
    supply_group_code = 123456 
    trf = 2
    tariff_index = "{:02d}".format(trf)
    key_revision_no = 2  
    pad_value = 'ffffff' 
    stringed_control_params = list(map(lambda x: str(x), [key_type, supply_group_code, tariff_index, key_revision_no, pad_value]))

    issuer_id_no = 600727  
    decoder_reg_no = meter_number  
    stringed_pan_params = list(map(lambda x: str(x), [issuer_id_no, decoder_reg_no]))

    control_block = ''.join(stringed_control_params)
    pan_block = ''.join(stringed_pan_params)[-16:-1]
    print("PAN Block:", pan_block) 
    vending_key = generate_vending_key()

    x_1 = int(control_block, base=16) ^ int(pan_block, base=16)

    hexed_x_1 = hex(x_1).lstrip('0x')
    byte_arrayed_x_1 = bytearray.fromhex(hexed_x_1)
    cipher = DES.new(vending_key, DES.MODE_OFB)
    secret = cipher.encrypt(byte_arrayed_x_1)

    inted_secret = int(secret.hex(), base=16)
    x_2 = x_1 ^ inted_secret

    inted_vending_key = int(vending_key.hex(), base=16)
    x_3 = x_2 ^ inted_vending_key

    if key_expired_number:
        current_time = datetime.utcnow()
        expired_time = datetime.strptime(key_expired_number, "%Y-%m-%d")
        
        if current_time > expired_time:
            raise ValueError("Key has expired.")
    
    decoder_key = bin(x_3).lstrip('0b')

    return decoder_key

if __name__ == "__main__":
    meter_number = 6123 
    key_expired_number = "2024-12-31"  
    decoder_key = generate_decoder_key(meter_number, key_expired_number)
    print("Decoder Key:", decoder_key)
