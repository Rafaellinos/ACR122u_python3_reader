"""
ACR122u-A9
Mifare Classic 1K
pyscard (1.9.9)

"""
import time
import smartcard
from smartcard.util import toHexString

BLOCK_NUMBER = 0x00 #default
LOADKEY_A = [0xFF, 0x82, 0x00, 0x00, 0x06]
GET_UID = [0xFF,0xCA,0x00,0x00,0x04]
WRITE_16_BYTES = [0xFF, 0xD6, 0x00, BLOCK_NUMBER, 0x10]
FORBIDDEN_BLOCKS = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63] 
#access trailer is forbidden to write by default


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
        time.sleep(2)
        for block in range(sector*4, sector*4+4):
            COMMAND = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            execute_command(conn, COMMAND)
            response = execute_command(conn, [0xFF, 0xB0, 0x00, block, 0x10])
            if check_validate(response):
                print(toHexString(response[0]))
            else:
                print("ERRO ao autenticar o bloco")
    else:
        print("Setor incorreto.\nSelecione um setor de 0 a 15.")

def read_block(conn):
    BLOCK_NUMBER = int(input("Selecione um bloco para ler. Blocos vão de 0 a 63.\n"))
    if not 0 <= BLOCK_NUMBER <= 63:
        print("Bloco inválido. Blocos de 0 a 63")
        return
    print("Lendo bloco...")
    time.sleep(2)
    COMMAND = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, BLOCK_NUMBER, 0x60, 0x00]
    response = execute_command(conn, COMMAND)
    if check_validate(response):
        response = execute_command(conn,[0xFF, 0xB0, 0x00, BLOCK_NUMBER, 0x10])
        if check_validate(response):
            print(toHexString(response[0]))
        else:
            print("Erro ao ler o bloco.")
    else:
        print("Erro ao autenticar o bloco")


    
def write_block(conn):
    warning = "\nO valor precisa estar em ASCII e possuir 16 bytes!\nExemplo: 'Hello World RFID' ou 'This is my MESG1'.\n"
    BLOCK_NUMBER = int(input("Digite o block para escrever. Blocos vão de 0 a 63.\n"))
    if not 0 <= BLOCK_NUMBER <= 63:
        print("Número inválido. Blocos de 0 a 63.")
        return
    if BLOCK_NUMBER in FORBIDDEN_BLOCKS:
        print("Bloco proibido por ser um bloco trailer(último de cada setor) ou bloco 0")
        return
    WRITE_16_BYTES[3] = BLOCK_NUMBER
    value_to_write = input("Digite o valor para escrever no bloco."+warning)
    list_value = []
    for value in value_to_write:
        list_value.append(int(hex(ord(value)),16))
    if len(list_value) == 16:
        for value in list_value:
            WRITE_16_BYTES.append(value)
        response = execute_command(conn, WRITE_16_BYTES)
        if check_validate(response):
            print("Bloco escrito com sucesso!")
        else:
            print("Problema ao escrever no bloco!")
    else:
        print("Valor acima ou abaixo do permitido."+warning)
        return
    
            
conn = make_conn()
#get_uid(conn)
load_akey(conn)
#write_block(conn)
#read_sector(conn)
read_block(conn)
