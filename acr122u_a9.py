
import time
import smartcard
LOADKEY_A = [0xFF, 0x82, 0x00, 0x00, 0x06]
GET_UID = [0xFF,0xCA,0x00,0x00,0x04]
from smartcard.util import toHexString

def get_uid(conn):
    response = execute_command(conn, GET_UID)
    if check_validate(response):
        print(response[0])
    else:
        print("Error")

def make_conn():
    reader = smartcard.System.readers()
    if not reader:
        print("Sem leitores")
        return False
    else:
        conn =  reader[0].createConnection()
        conn.connect()
        print("Conexão estabelecida com "+str(reader))
        return conn

def execute_command(conn, command):
    response = conn.transmit(command)
    return response

def check_validate(response):
    if response[1] == 144:
        return True
    return False

def load_akey(conn):
    key = input("Digite a chave A:\n Contém 6 bytes, digite em numero decimal."\
        +"\nExemplo: 255,255,255,255,255,255\n")
    key = key.split(',')
    if len(key) == 6:
        key = [int(i) for i in key]
        for byte in key:
            if 0 <= byte <= 255:
                LOADKEY_A.append(byte)
            else:
                print("Número inválido: "+str(byte))
                return False
        response = execute_command(conn, LOADKEY_A)
        if check_validate(response):
            print("Chave carrega com sucesso.")
        else:
            print("Problema ao carregar a chave")
    else:
        print("A chave precisa conter 6 bytes, separados por virgula.")

def read_sector(conn):
    sector = input("Selecione o setor para leitura.\nDigite um número de 0 a 15.\n")
    sector = int(sector)
    if 0 <= sector <= 15:
        print("Lendo blocos do setor "+str(sector))
        for block in range(sector*4, sector*4+4):
            COMMAND = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            execute_command(conn, COMMAND)
            response = execute_command(conn, [0xFF, 0xB0, 0x00, block, 0x10])
            if check_validate(response):
                print(toHexString(response[0]))
            else:
                print("ERRO no bloco")
    else:
        print("Setor incorreto.\nSelecione um setor de 0 a 15.")
            
conn = make_conn()
get_uid(conn)
load_akey(conn)
read_sector(conn)
