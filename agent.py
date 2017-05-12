import socket
import sys
from argparse import ArgumentParser
import re

class Agent:
    def __init__(self, address='localhost', port='31415'):
        self.conn = socket.create_connection((address, port))
        self.display()

    def recv_from_server(self):
        data = self.conn.recv(1024).decode()
        return data

    def act(self, action):
        p = re.compile("^[LRFCB]+$")
        if not re.match(p, action.upper()):
            print('Illegal action!')
            return
        for a in action:
            self.conn.send(a.encode())
            self.display()
        return

    def display(self):
        data = self.recv_from_server()
        assert(data)
        data = data[:12] + '^' + data[12:]
        print('+-----+')
        for i in range(5):
            print('|', end='')
            for j in range(5):
                print(data[5*i+j], end='')
            print('|')
        print('+-----+')
        return


parser = ArgumentParser()
parser.add_argument('--port', dest='port')
args = parser.parse_args()
port = args.port

agent = Agent()
while True:
    action = input("Enter Action(s): ")
    try:
        agent.act(action)
    except:
        print('Game over')
        sys.exit()
agent.act(action)


