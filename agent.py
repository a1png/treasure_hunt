import socket
import sys
from argparse import ArgumentParser
import re

class Agent:
    def __init__(self, address='localhost', port='31415'):
        self.conn = socket.create_connection((address, port))
        self.steps = 0
        self.directions = {0: '^', 1: '<', 2: 'v', 3: '>'}
        self.desired = ['A', 'K', 'D', '$']
        self.unaccessible = ['*', '-', 'T', '~']
        self.unaccessible_solution = {'*': 'D', '-': 'K', 'T': 'A', '~': 'T'}
        self.target_pos = {'$': None}
        self.mission_stack = ['$']
        self.direction = 0
        self.x = 5
        self.y = 5
        self.known_world = [['?' for _ in range(11)] for _ in range(11)]
        data = self.recv_from_server()
        self.axe = False
        self.key = False
        self.dynamite = False
        self._update_world(data)
        self._world_we_already_know()
        self._display(data)


    def recv_from_server(self):
        data = self.conn.recv(1024).decode()
        return data

    def act(self, action):
        p = re.compile("^[LRFCBU]+$")
        if not re.match(p, action.upper()):
            print('Illegal action!')
            return
        for a in action:
            if a.upper() in ('L', 'R'):
                self._turn(a)
            self.conn.send(a.encode())
            data = self.recv_from_server()
            if a.upper() == 'F':
                next_block = self._find_next_block()
                if next_block in [' ', 'A', 'K', 'D', '$']:
                    if next_block == 'A':
                        self.axe = True
                    elif next_block == 'K':
                        self.key = True
                    elif next_block == 'D':
                        self.dynamite = True
                    if self.direction % 2 == 0:
                        self.y += self.direction - 1
                    elif self.direction %2 != 0:
                        self.x += (self.direction - 2)
            self._update_world(data)
            self._world_we_already_know()
            self._display(data)
            self.steps += 1
        return

    def _turn(self, turn):
        if turn.upper() == 'L':
            self.direction += 1
        elif turn.upper() == 'R':
            self.direction -= 1
        if self.direction == 4:
            self.direction = 0
        if self.direction == -1:
            self.direction = 3
        return

    def _update_world(self, data, sight=5):
        view = self._rotate_view(data)
        x_size = len(self.known_world[0])
        y_size = len(self.known_world)
        l = sight // 2
        if self.x - l < 0:
            self.known_world = [['?' for _ in range(x_size)] + \
                self.known_world[y] for y in range(y_size)]
            self.x += x_size 
        if self.x + l >= x_size:
            self.known_world = [(self.known_world[y] + ['?' for _ in range(x_size)])\
                                 for y in range(y_size)]
        if self.y - l < 0:
            self.known_world = [(['?' for _ in range(y_size)] + \
                self.known_world[x]) for x in range(x_size)]
            self.y += y_size
        if self.y + l >= y_size:
            self.known_world = [(self.known_world[x] + ['?' for _ in range(y_size)])\
                                 for x in range(x_size)]
        for i in range(0, sight):
            for j in range(0, sight):
                self.known_world[self.y - l + i][self.x - l + j] = view[i][j]

    def _rotate_view(self, data, sight=5):
        data = data[:sight**2//2] + self.directions[self.direction] + data[sight**2//2:]
        view = [['?' for _ in range(sight)] for _ in range(sight)]
        for i in range(sight):
            for j in range(sight):
                view[i][j] = data[sight * i + j]
        for _ in range(self.direction):
            rotated_view = [['?' for _ in range(sight)] for _ in range(sight)]
            for i in range(sight):
                for j in range(sight):
                    rotated_view[i][j] = view[j][sight-i-1]
            view = rotated_view
        return view

    def _find_next_block(self, steps=1):
        x = self.x
        y = self.y
        if self.direction % 2 == 0:
            y += (self.direction - 1) * steps
        elif self.direction %2 != 0:
            x += (self.direction - 2) * steps
        next_block = self.known_world[y][x].upper()
        return next_block 

    def _world_we_already_know(self):
        y_size = len(self.known_world)
        x_size = len(self.known_world[0])
        print('+', '-'*x_size, '+', sep='')
        for i in range(y_size):
            print('|', end='')
            for j in range(x_size):
                print(self.known_world[i][j], end='')
            print('|')
        print('+', '-'*x_size, '+', sep='')

    def _display(self, data):
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

    def _find_nearest_stuff(self, stuff, point=None):
        if point is None:
            point = (self.x, self.y)
        x0, y0 = point
        dis = None
        des = None
        for y in range(len(self.known_world)):
            for x in range(len(self.known_world[0])):
                if self.known_world[y][x].upper() == stuff:
                    this_dis = x0 + y0 - x - y
                    if dis is None or this_dis < dis:
                        dis = this_dis
                        des = (x, y)
        if des is not None:
            return des
        return None

    def _heuristic(self, start, des):
        pass

    def a_star(self, start, des):
        from queue import PriorityQueue as p_queue

    def go_to_point(self, point, path):
        pass

    def _go_to_neightbour_point(self, point):
        x, y = point
        d_x = x - self.x
        d_y = y - self.y
        if d_x != 0:
            des_direction = d_x + 2
        if d_y != 0:
            des_direction = d_y + 1
        left_turns = abs(self.direction - des_direction)
        right_turns = (4 - des_direction + self.direction) % 4
        print(des_direction, self.direction, left_turns, right_turns)
        if left_turns <= right_turns:
            for _ in range(left_turns):
                self.act('L')
        elif left_turns > right_turns:
            for _ in range(right_turns):
                self.act('R')
        self.act('F')
        return


parser = ArgumentParser()
parser.add_argument('--port', dest='port')
args = parser.parse_args()
port = args.port

agent = Agent()
while True:
    action = input("Enter Action(s): ")
    # try:
    #     agent.act(action)
    # except:
    #     print('Game over')
    #     sys.exit()
    agent.act(action)
agent.act(action)


