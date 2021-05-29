import socket

import json

from concurrent.futures import ThreadPoolExecutor

from handlers import *

from commands import *

from cryptools import create_session

from model import History

from datetime import datetime

with open("config.json", 'r') as file:
    conf = json.load(file)

IP = conf['ip']
PORT = conf['port']
ENCODING = conf['encoding']
MSG_LEN = conf['msg_len']
SERVER_INFO = (IP, PORT)


def client_main_handler(conn: socket.socket, encoding, server_info,
                        client_info, buffer_size):
    session = create_session()
    
    print(f'session : {session}')

    while True:
        try:
            command = client_message_handler(conn, encoding, server_info,
                                                client_info, buffer_size)

            if command == 'quit' or command == '/c':
                break

            parts = decompose_command(command)

            # send acceptance message
            conn.send(COMMAND_VALID.encode(encoding))

            handler = COMMANDS[parts['cmd']]['options'][
                parts['option']]['handler']

            response = handler(conn, encoding, server_info, client_info,
                                buffer_size,session=session)

            if response == '/c':
                break

            History.create(session = session , date = datetime.now() , command=f'{parts["cmd"]} {parts["option"]} "{response}"')

        except NotACommandError as e:
            # send invlid command
            print("oooooppppssss")
            print(str(e))
            # conn.send(str(e).encode(encoding))

    print('connection closed')
    conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.bind(SERVER_INFO)

        sock.listen()

        print("listening to clients : ")

        with ThreadPoolExecutor(10) as executor:
            while True:
                conn, client_info = sock.accept()

                print(f"connected to {client_info}")

                executor.submit(
                    client_main_handler,
                    *(conn, ENCODING, SERVER_INFO, client_info, MSG_LEN))



if __name__ == '__main__':

    main()