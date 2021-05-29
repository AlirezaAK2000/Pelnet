from handlers import *
from senders import *
import re

COMMANDS = {
    'upload':{
        'options' : {
            '':{
                'sender': file_sender,
                'handler': client_file_upload_handler
            }   
        }
    },
    'exec':{
        'options' : {
            '':{
                'sender':request_sender,
                'handler': client_exec_handler
            }
        }
    },
    'send':{
        'options': {
            '-e':{
                'sender':tls_simple_message_sender,
                'handler':client_tls_message_handler
            },
            '':{
                'sender':simple_message_sender,
                'handler':client_message_handler
            }       
        }
    },
    'history':{
        'options':{
            '':{
                'sender':history_retriver,
                'handler':client_history_handler
            }    
        }      
    }
}


def decompose_command(command):
    parts = re.sub('\".*?\"',"" , command).split()
    if parts[0] != 'telnet':
        raise NotACommandError('you forgot to put telnet')
    
    parts = parts[1:]
    
    if parts[0] not in COMMANDS.keys():
        raise NotACommandError(f'command {parts[0]} is not defined')
    
    parts_dict = dict()
    
    parts_dict['cmd'] = parts[0]
    
            
    parts_dict['option'] = parts[1] if len(parts) >= 2 and '-' in parts[1] else ""
        
    return parts_dict



class NotACommandError(Exception):

    """
        raised for commands that does not implemented
    """
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
        