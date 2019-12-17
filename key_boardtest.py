"""
ACR122u-A9
Mifare Classic 1K
pyscard (1.9.9)
pynput (1.6.0)
"""
import time
import smartcard
from smartcard.util import toHexString
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType

from pynput.keyboard import Key, Controller

BLOCK_NUMBER = 0x00 #default
KEY_A = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
AUTH_BLOCK = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, BLOCK_NUMBER, 0x60, 0x00]
READ_16_BYTES = [0xFF, 0xB0, 0x00, BLOCK_NUMBER, 0x10]
GET_UID = [0xFF,0xCA,0x00,0x00,0x04]

class ReaderACR():
    def make_conn(self):
        reader = smartcard.System.readers()
        if not reader:
            print("No readers")
            return
        conn =  reader[0].createConnection()
        conn.connect()
        print("Connection established successfully with "+str(reader))
        return conn

    def check_response(self, response):
        if response[1] == 144:
            return True
        return

    def execute_command(self, conn, command):
        response = conn.transmit(command)
        return response

    def get_uid(self,conn):
        response = self.execute_command(conn, GET_UID)
        if self.check_response(response):
            return toHexString(response[0])
        return


    def load_key_a(self, conn):
        response = self.execute_command(conn, KEY_A)
        if self.check_response(response):
            print("Key loaded successfully")
            return
        print("Something wrong when loading the key A")

    def read_all(self):
        blocks = ""
        try:
            cardtype = AnyCardType()
            request = CardRequest(timeout=60, cardType=cardtype)
            request.waitforcard()
            conn = self.make_conn()
            self.load_key_a(conn)#Default key = FF,FF,FF,FF,FF,FF
            blocks += self.get_uid(conn)+"\n"
            for block in range(0, 64):
                AUTH_BLOCK[7] = block
                READ_16_BYTES[3] = block
                response = self.execute_command(conn, AUTH_BLOCK)
                response = self.execute_command(conn, READ_16_BYTES)
                #print(toHexString(response[0]))
                blocks += toHexString(response[0])+"\n"
            return blocks
        except Exception as e:
            print("Error: "+str(e))
            return

class OutPutRead():

    def press_keys(self):
        response = ReaderACR().read_all()
        print("Starting typing...")
        time.sleep(2)
        keyboard = Controller()
        for char in response:
            time.sleep(0.01)
            if char == '\n':
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                continue
            keyboard.press(char)
            keyboard.release(char)


OutPutRead().press_keys()
