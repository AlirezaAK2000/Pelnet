


WELCOME = """
ENTER HELP TO LIST COMMANDS
"""


CMD_BEG = ">>> "


HELP = """
telnet upload "path" (uploads file with specified path to the connected server)
telent exec "command" (run command in the server side)
telnet send "message" (send message with pure TCP connection)
telnet send -e "message" (send encrypted message via TLS handshake)
telnet history
telnet openports
"""

ERRORS = [
    "command not found"
]



COMMAND_VALID = 'command is valid'


FILE_FINISHED = '\n\n/n/'


MODES = """
1.p (connection protocol for local server)
2.t (simple TCP connection to another host)
"""
