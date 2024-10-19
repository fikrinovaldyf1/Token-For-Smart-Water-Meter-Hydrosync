from datetime import datetime, timedelta
from decoder_key import generate_decoder_key
from proses_enkripsi import class_insert, substitute, permutate, rotate
from tokengen import bin_pad, bin_str,generate_token_block, base_date, token_class

#iv = get_random_bytes(8)

def encrypt(token_block, decoder_key, debit_beli):
    token_block_int = int(token_block, base=2)
    decoder_key_int = int(decoder_key, base=2)
    print("Decoder Key:", decoder_key)
    start_point_int = token_block_int ^ decoder_key_int
    start_point_bin_str = bin_pad(bin_str(start_point_int), 64)
    print("Hasil XOR Biner:", start_point_bin_str)
    substituted = substitute(start_point_bin_str)
    print("Hasil proses substitusi:", substituted)
    permuted = permutate(substituted)
    print("Hasil proses permutasi:", permuted)
    rotated = rotate(permuted)
    print("Hasil proses rotasi:", rotated)
    class_inserted = class_insert(rotated)
    print("Hasil inserted:", class_inserted)
    result_bin_str = class_inserted.zfill(64) 
    print("Hasil Biner:", result_bin_str)
    binary = int(result_bin_str, 2)
    binary_str = "{:064b}".format(binary)
    decimal_output = "{:017d}".format(binary)
    token_str = ''.join([decimal_output[i:i + 4].zfill(4) for i in range(0, len(decimal_output), 4)])
    debit_beli_str = str(debit_beli).zfill(3)
    token_deb = token_str[:17] 
    token_debit = token_deb + debit_beli_str
    if len(token_debit) > 20:
        token_debit = token_debit[:20]
    else:
        token_debit = token_debit.ljust(20, '0')
    print("Hasil Token:", decimal_output)
    print("Hasil Token dan Debit:", token_debit)
    token_debit_int = int(token_debit)
    binarytoken=bin(token_debit_int)[2:]
    print("Hasil biner token:",binarytoken)
    
    # Extract token info
    subclass = binary_str[0: 4]
    rnd_bits = binary_str[4: 8]
    tk_id = binary_str[8:32]
    tk_id_formatted = base_date + timedelta(minutes=int(tk_id, base=2))
    # Hitung waktu sekarang dan delta dari base_date
    now = datetime.now()
    delta = now - base_date
    # Hitung menit dari base_date untuk tk_id
    tk_id_minutes = int(delta.total_seconds() / 60)
    # Hitung waktu kedaluwarsa (1 hari setelah waktu sekarang)
    expiration_time = now + timedelta(days=1)
    tkid = expiration_time.strftime('%Y-%m-%d %H:%M')
    #amount = binary_str[32: 48]
    amount_formatted = debit_beli
    hasil_debit= binarytoken[65:66]

    token_infoencrypt = {
        'class': '01',
        'subclass': subclass,
        'rnd': rnd_bits,
        'Masa Berlaku Token': tk_id_formatted,
        'amount': amount_formatted,
    }
    return token_str,tkid, token_infoencrypt   
if __name__ == "__main__":
    rate = input("Masukkan harga perkubik: ")
    amount = input("Masukkan harga: ")
    meter_number = input("Masukkan meter number: ")
    token_class = input("Masukkan golongan: ") # [0-3]

    token_block = generate_token_block(int(rate), int(amount), int(token_class))
    decoder_key = generate_decoder_key(int(meter_number))
    print("Decoder Key:", decoder_key)

    encrypted_token_20digits, iv, token_infoencrypt = encrypt(token_block, decoder_key)
    print("Encrypted Token Biner:", encrypted_token_20digits)
    print("Token Info:", token_infoencrypt)