import socket

import json

import sys

from senders import *

from constants import *

from commands import *

import re



with open("config.json" , 'r') as file:
    conf = json.load(file)

IP = conf['ip']
PORT = conf['port']
ENCODING = conf['encoding']
MSG_LEN = conf['msg_len']
SERVER_INFO = (IP , PORT)

    

def main():
    with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as sock:
        try:    
            sock.connect(SERVER_INFO)
            
            print("connection established !!!")

            message = ''

            print("enter mode : ")
            
            print(MODES)

            message = input(CMD_BEG)
                    
            mode = message.strip('\n') == 'p'

            if not mode:
                welcome_message = sock.recv(MSG_LEN).decode(ENCODING).strip('\r\n')
                
                print(welcome_message)
            
            while True:
                try:
                    
                    message = input(CMD_BEG)
                    
                    if message == 'openports':
                        beg = int(input('start from : '))
                        end = int(input('end :'))
                        ports = scan_ports(IP ,beg , end)
                        print('\n'.join([str(port) for port in ports]))
                        continue
                    
                    if mode:

                        if message == "quit":
                            simple_message_sender(sock , message ,ENCODING , MSG_LEN )
                            break
                        
                        if message == 'telnet help':
                            print(HELP)
                            continue
                        
                        parts = decompose_command(message)
                        
                        
                        msg = f' '.join(re.sub('\".*?\"',"" , message).split())
                        
                        simple_message_sender(sock , msg , ENCODING , MSG_LEN)
                        
                        res = sock.recv(MSG_LEN).decode(ENCODING)                    
                        if res == COMMAND_VALID:
                            
                            args =  re.findall('\".*?\"' , message)
                            
                            arg = re.sub( '"','', re.findall('\".*?\"' , message)[0]) if len(args) else ""

                            sender = COMMANDS[parts['cmd']]['options'][parts['option']]['sender']
                            
                            sender(sock , arg , ENCODING , MSG_LEN)


                    else:
                        request_sender(sock, message, ENCODING, MSG_LEN)

                except NotACommandError as e:
                    print(str(e))
                    print('invalid command \n type "telnet help" to see all commnds')
                
                

        except BrokenPipeError:
            print("connection finished")
            exit()

    

if __name__ == '__main__':
    
    if len(sys.argv) == 3:
        args = sys.argv
        IP = args[1] if args[1] else IP
        PORT = int(args[2]) if args[2] else PORT
        SERVER_INFO = (IP , PORT)
        
    try:
        main()
    except ConnectionRefusedError as e:
        print('connection refused !!!')
        exit()