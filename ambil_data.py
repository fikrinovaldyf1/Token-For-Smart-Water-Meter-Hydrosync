import mysql.connector
import time
import threading
from decoder_key import generate_decoder_key
from tokengen import generate_token_block
from tokencipher import encrypt

def create_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="back_app"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_pembelian_data(cursor):
    query = "SELECT id_transaksi, status, meter_id, harga_beli FROM pembelians WHERE status = 'capture'"
    cursor.execute(query)
    return cursor.fetchall()

def process_pembelian_data(pembelian_data, cursor, conn):
    for pembelian in pembelian_data:
        id_transaksi, status, meter_id, harga_beli = pembelian
        if not harga_beli.isdigit() or int(harga_beli) <= 0:
            print("Nominal uang tidak valid.")
            continue
        rate = 5000
        amount = int(harga_beli)
        debit_beli = amount // rate

        token_block = generate_token_block(token_class=1)
        decoder_key = generate_decoder_key(meter_id)
        token_str, tkid, token_infoencrypt = encrypt(token_block, decoder_key, debit_beli)
        token_deb = token_str[:17]
        token_debit = token_deb + str(debit_beli).zfill(3)
        if len(token_debit) > 20:
            token_debit = token_debit[:20]
        else:
            token_debit = token_debit.ljust(20, '0')
        print("Token Info : ", token_infoencrypt)
        print("Kadaluarsa Token:", tkid)
        save_to_database(id_transaksi, meter_id, harga_beli, debit_beli, token_debit, tkid, cursor, conn)

def save_to_database(id_transaksi, meter_id, harga_beli, debit_beli, token, tkid, cursor, conn):
    try:
        query = """
            UPDATE pembelians 
            SET harga_beli = %s, debit_beli = %s, token = %s, status = %s, expire_token = %s
            WHERE id_transaksi = %s
        """
        values = (harga_beli, debit_beli, token, 'success', tkid, id_transaksi)
        cursor.execute(query, values)
        conn.commit()
        print("Data berhasil diperbarui di database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()

def main_loop():
    conn = create_db_connection()
    if conn:
        cursor = conn.cursor()
        while True:
            pembelian_data = get_pembelian_data(cursor)
            if pembelian_data:
                process_pembelian_data(pembelian_data, cursor, conn)
            time.sleep(5)  # Interval waktu untuk pengecekan pembelian baru
        cursor.close()
        conn.close()
    else:
        print("Koneksi database gagal. Mengakhiri program.")

def check_for_updates():
    while True:
        time.sleep(7)  # Interval waktu untuk pengecekan pembaruan
        conn = create_db_connection()
        if conn:
            cursor = conn.cursor()
            pembelian_data = get_pembelian_data(cursor)
            if pembelian_data:
                process_pembelian_data(pembelian_data, cursor, conn)
            cursor.close()
            conn.close()
        else:
            print("Koneksi database gagal dalam thread pembaruan.")

update_thread = threading.Thread(target=check_for_updates)
update_thread.daemon = True
update_thread.start()

if __name__ == "__main__":
    main_loop()
