# -*- encoding: utf-8 -*-
from b3.parsers.iourt41 import Iourt41Parser
from b3.fake import FakeConsole, fakeConsole

CLIENTS_PORT = {}

def set_clients_ports(ports):
    global CLIENTS_PORT
    CLIENTS_PORT = ports


def my_rcon_status_response():
    global CLIENTS_PORT
    lines = []
    for cid, port in CLIENTS_PORT.items():
        lines.append("%s     0    0 xxxx^7                  0 192.168.1.2:%s      33909  8000" % (cid, port))

    return """\
status
map: ut4_casa
num score ping name            lastmsg address               qport rate
--- ----- ---- --------------- ------- --------------------- ----- -----
%s
""" % '\n'.join(lines)


original_write = fakeConsole.write
def my_console_write(data):
    if data == 'status':
        return my_rcon_status_response()
    else:
        return original_write(data)


def prepare_fakeparser_for_tests():
    FakeConsole.gameName = 'iourt41'
    fakeConsole.write = my_console_write
    fakeConsole._regPlayer = Iourt41Parser._regPlayer

