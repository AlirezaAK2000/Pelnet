from base64 import encode
from constants import FILE_FINISHED
import socket

import os

from typing import List

import tqdm

from cryptools import *

import logging

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filename='server.log',
    filemode='a',
)


def simple_message_sender(sock: socket.socket, message: str, encoding,
                          buffer_size):

    msg = message.encode(encoding)

    msg_length = str(len(msg)).encode(encoding)

    msg_length += b' ' * (buffer_size - len(msg_length))

    sock.send(msg_length)

    sock.send(msg)


def request_sender(sock: socket.socket, message: str, encoding, buffer_size):

    message += '\r\n'
    sock.send(message.encode(encoding))

    response = sock.recv(buffer_size).decode(encoding)

    print(response)
    return response


def file_sender(sock: socket.socket, file_name: str, encoding, buff_size: int):
    file_size = os.path.getsize(os.path.join('client_files', file_name))

    seperator = '\n\n\n'

    message = f"{file_name}{seperator}{file_size}{seperator}{buff_size}"
    sock.send(message.encode(encoding))

    # progress bar
    with tqdm.tqdm(range(file_size),
                   f"Sending {file_name}",
                   unit="B",
                   unit_scale=True,
                   unit_divisor=1024) as progress:
        
        with open(os.path.join('client_files', file_name), 'rb') as file:

            while True:

                bytes_read = file.read(buff_size)

                if not bytes_read:
                    break

                # print(bytes_read)
                sock.send(bytes_read)

                progress.update(len(bytes_read))
                
        sock.send(FILE_FINISHED.encode(encoding))


def scan_ports(ip, beg, end) -> List:
    open_ports = []
    for port in range(beg, end):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            sock.settimeout(1)

            result = sock.connect_ex((ip, port))

            if result == 0:
                open_ports.append(port)

    return open_ports


def tls_simple_message_sender(sock: socket.socket, message, encoding,
                              buffer_size):

    sock.send('hello'.encode(encoding))
    hello_res = sock.recv(buffer_size).decode(encoding)

    if hello_res == 'hello':
        master_secret_encrypted = generate_secret_key_for_AES_cipher()

        sock.send(master_secret_encrypted)

        finish_handshake = decrypt_message(sock.recv(buffer_size),
                                           master_secret_encrypted,
                                           b"{").decode(encoding)

        if finish_handshake == 'finish':

            message = encrypt_message(message, master_secret_encrypted, "{")

            message_size = encrypt_message(str(len(message)),
                                           master_secret_encrypted, "{")

            message_size += b' ' * (buffer_size - len(message_size))

            sock.send(message_size)

            sock.send(message)


def history_retriver(sock: socket.socket, message, encoding, buffer_size):
    
    res_len = int(sock.recv(buffer_size).decode(encoding))
    
    response = sock.recv(res_len).decode(encoding)
    
    print(response)