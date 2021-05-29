from operator import le
import re
import socket

import os

import subprocess

from cryptools import *

import logging

from model import History

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filename='server.log',
                    filemode='a',
                    level=logging.INFO)

from constants import *

from handlers import *


def client_message_handler(conn: socket.socket, encoding, server_info,
                           client_info, buffer_size,**kwargs):
    
    message_len = conn.recv(buffer_size)
    if len(message_len) == 0:
        return '/c'

    message_len = int(message_len.decode(encoding))

    logging.info(
        f"<<SIMPLE TCP>> {client_info} ====> {server_info} : {message_len}")

    message = conn.recv(message_len).decode(encoding)
    logging.info(
        f"<<SIMPLE TCP>> {client_info} ====> {server_info} : {message}")

    print(f'message : {message}')

    return message


def client_file_upload_handler(conn: socket.socket, encoding, server_info,
                               client_info, buffer_size,**kwargs):
    try:
        init_message = conn.recv(buffer_size)

        print('going to get file')
        file_name, file_size, buff_size = (
            init_message.decode(encoding)).split("\n\n\n")

        # sys.path.basename(f'server_file/{file_name}')

        print("{} {} {}".format(file_name, file_size, buff_size))

        file_size, buff_size = int(file_size), int(buff_size)

        with open(os.path.join('server_files', file_name), 'wb') as file:
            while True:

                bytes_read = conn.recv(buff_size)

                if not bytes_read:
                    break

                file.write(bytes_read)
                
                if len(bytes_read) < buff_size:
                    break 
               
        print('file transfer finished') 
        return file_name

    except Exception as e:
        print(str(e))


def client_exec_handler(conn: socket.socket, encoding, server_info,
                        client_info, buffer_size,**kwargs):

    command = conn.recv(buffer_size).decode(encoding).strip('\r\n')

    res = subprocess.run([command], shell=True, capture_output=True)

    output = res.stdout.decode(encoding)

    conn.send(str(output).encode(encoding))
    
    return command


def client_tls_message_handler(conn: socket.socket, encoding, server_info,
                               client_info, buffer_size,**kwargs):

    logging.info("<<TLS>>  connection started")
    hello_req = conn.recv(buffer_size).decode(encoding)
    if len(hello_req) == 0:
        return '/c'

    logging.info(f"<<TLS>> {client_info} ====> {server_info} : {hello_req}")

    if hello_req == 'hello':

        conn.send(hello_req.encode(encoding))
        logging.info(
            f"<<TLS>> {server_info} ====> {client_info} : {hello_req}")

        master_secret_encrypted = conn.recv(buffer_size)
        logging.info(
            f"<<TLS>> {client_info} ====> {server_info} : {master_secret_encrypted}"
        )

        finish_message = encrypt_message('finish', master_secret_encrypted,
                                         '{')

        conn.send(finish_message)
        logging.info(
            f"<<TLS>> {server_info} ====> {client_info} : {finish_message}")

        message_size = conn.recv(buffer_size)
        logging.info(
            f"<<TLS>> {client_info} ====> {server_info} : {message_size}")
        message_size = int(
            decrypt_message(message_size, master_secret_encrypted, b'{'))

        message = conn.recv(message_size)
        logging.info(f"<<TLS>> {client_info} ====> {server_info} : {message}")
        message = decrypt_message(message, master_secret_encrypted,
                                  b'{').decode(encoding)

        print(f"message : {message}")

    logging.info("<<TLS>>  connection closed")
    
    return message 


def client_history_handler(conn: socket.socket, encoding, server_info,client_info, buffer_size ,**kwargs):
    
    session = kwargs['session']
    
    records = History.select(History).where(History.session == session).order_by(History.date)
    
    response = '\n'.join([record.command for record in records]) if len(records) else ""
    
    response = response.encode(encoding)
    
    res_length = str(len(response)).encode(encoding)
    
    res_length += b' ' * (buffer_size - len(res_length))
    
    conn.send(res_length)
    
    conn.send(response)
    