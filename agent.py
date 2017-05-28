import socket
import sys
from argparse import ArgumentParser
import re
from copy import copy

class Agent:
    def __init__(self, address='localhost', port='31415'):
        self.conn = socket.create_connection((address, port))
        self.steps = 0
        self.directions = {0: '^', 1: '<', 2: 'v', 3: '>'}
        self.desired = ['A', 'K', 'D', '$']
        self.unaccessible = ['*', '-', 'T', '~', '.']
        self.unaccessible_solution = {'*': 'D', '-': 'K', 'T': 'A', '~': 'T'}
        self.target_pos = {'$': None}
        self.items = []
        self.mission_stack = ['$']
        self.direction = 0
        self.x = 5
        self.y = 5
        self.start_point = (self.x, self.y)
        self.visited_places = {(self.x, self.y): self.steps}
        self.x_size = 11
        self.y_size = 11
        self.known_world = [['?' for _ in range(self.x_size)] for _ in range(self.y_size)]
        self.sailing = False
        data = self.recv_from_server()
        self._update_world(data)
        #self._world_we_already_know()
        #self._display(data)


    def recv_from_server(self):
        data = self.conn.recv(1024).decode()
        if not data:
            sys.exit()
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
                self.visited_places[(self.x, self.y)] = self.steps
                next_block = self._find_next_block()
                if next_block in [' ', 'A', 'K', 'D', '$', '~']:
                    if next_block == 'A':
                        self.items.append('A')
                    elif next_block == 'K':
                        self.items.append('K')
                    elif next_block == 'D':
                        self.items.append('D')
                    elif next_block != '~' and self.sailing:
                        self.items.remove('T')
                        self.sailing = False
                    if next_block == '$':
                        self.items.append('$')
                    if self.direction % 2 == 0:
                        self.y += self.direction - 1
                    elif self.direction %2 != 0:
                        self.x += (self.direction - 2)
            self._update_world(data)
            self._world_we_already_know()
            #self._display(data)
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
        x_size = 11
        y_size = 11
        
        l = sight // 2
        if self.x - l < 0:
            self.known_world = [['?' for _ in range(x_size)] + \
                self.known_world[y] for y in range(self.y_size)]
            self.x += x_size
            self.start_point = (self.start_point[0] + x_size, self.start_point[1])
            for i in list(self.visited_places.keys()):
                d = self.visited_places.pop(i)
                p = i[0] + x_size, i[1]
                self.visited_places[p] = d
            if self.path is not None:
                for i in range(len(self.path)):
                    p = self.path[i]
                    self.path[i] = (p[0]+x_size, p[1])
            self.x_size += x_size
        elif self.x + l + 1 >= self.x_size:
            self.known_world = [(self.known_world[y] + ['?' for _ in range(x_size)])\
                                 for y in range(self.y_size)]
            self.x_size += x_size
        if self.y - l < 0:
            self.known_world = [['?' for _ in range(self.x_size)] for _ in range(y_size)] + self.known_world
            self.y += y_size
            self.start_point = (self.start_point[0], self.start_point[1]+y_size)
            for i in list(self.visited_places.keys()):
                d = self.visited_places.pop(i)
                p = i[0], i[1] + y_size
                self.visited_places[p] = d
            if self.path is not None:
                for i in range(len(self.path)):
                    p = self.path[i]
                    self.path[i] = (p[0], p[1] + y_size)
            self.y_size += y_size
        elif self.y + l + 1 >= self.y_size:
            self.known_world += [['?' for _ in range(self.x_size)] for _ in range(y_size)]
            self.y_size += y_size
        for i in range(0, sight):
            for j in range(0, sight):
                self.known_world[self.y - l + i][self.x - l + j] = view[i][j]
        return

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
        print('+', '-'*self.x_size, '+', sep='')
        for i in range(self.y_size):
            print('|', end='')
            for j in range(self.x_size):
                print(self.known_world[i][j], end='')
            print('|')
        print('+', '-'*self.x_size, '+', sep='')

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
                if self.known_world[y][x].upper() == stuff.upper():
                    this_dis = x0 + y0 - x - y
                    if dis is None or this_dis < dis:
                        dis = this_dis
                        des = (x, y)
        if des is not None:
            return des
        return None

    def _heuristic(self, point, des):
        return abs(des[0] - point[0]) + abs(des[1] - point[1])

    def _astar(self, start, des):
        from queue import PriorityQueue
        def _get_around(point):
            x, y = point
            around = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            around_points = []
            for a in around:
                p = (x+a[0], y+a[1])
                if not (0 <= p[0] < self.x_size and 0 <= p[1] < self.y_size):
                    continue
                if self.known_world[p[1]][p[0]] in \
                    [b for b in self.unaccessible + ['?']\
                         if self.unaccessible_solution.get(b) not in self.items]:
                    continue
                around_points.append(p)
            return around_points
        frontier = PriorityQueue()
        frontier.put((0, start, []))

        cost_so_far = {start:0}
        came_from = {start:None}
        while not frontier.empty():
            current = frontier.get()
            current_pos = current[1]
            if current_pos == des:
                break
            around = _get_around(current_pos)
            for p in around:
                from copy import copy
                used_item = copy(current[2])
                cost = 1
                if not (0 <= p[0] < self.x_size and 0 <= p[1] < self.y_size):
                    continue
                if self.known_world[p[1]][p[0]] == '*':
                    if used_item.count('D') + 1 > self.items.count('D'):
                        continue
                    else:
                        used_item.append('D')
                        cost = 999
                        if self.known_world[current_pos[1]][current_pos[0]] == '~':
                            cost *= 2
                    tar = self._find_nearest_stuff('$')
                    if tar:
                        cost += self._heuristic((p[0], p[1]), tar) * 100
                new_cost = cost_so_far[current_pos] + cost
                if p not in cost_so_far or new_cost < cost_so_far[p]:
                    cost_so_far[p] = new_cost
                    priority = new_cost + self._heuristic(p, des)
                    frontier.put((priority, p, used_item))
                    came_from[p] = current_pos
        if des in came_from:
            path = [des]
            f = came_from[des]
            while start != f:
                path.append(f)
                f = came_from[f]
            return path[::-1]
        else:
            return None


    def _go_follow_path(self, point=None):
        if point is None:
            point = ((self.x, self.y))
        for p in self.path:
            self._go_to_neightbour_point(p)
        self.path = None
        return

    def _turn_to_direction(self, des_direction):
        left_turns =  (4 + des_direction - self.direction) % 4
        right_turns = (8 - des_direction + self.direction) % 4
        if left_turns <= right_turns:
            for _ in range(left_turns):
                self.act('L')
        elif left_turns > right_turns:
            for _ in range(right_turns):
                self.act('R')
        return

    def _landing_valuable(self, point):
        self.sailing = False
        self.items.remove('T')
        path = None
        for y in range(len(self.known_world)):
            for x in range(len(self.known_world[y])):
                if self.known_world[y][x].upper() in self.desired:
                    path = self._astar((self.x, self.y), (x,y))
        if path is None:
            self.sailing = True
            self.items.append('T')
            return False
        return True


    def _go_to_neightbour_point(self, point):
        x, y = point
        d_x = x - self.x
        d_y = y - self.y
        if d_x != 0:
            des_direction = d_x + 2
        if d_y != 0:
            des_direction = d_y + 1
        self._turn_to_direction(des_direction)
        next_block = self._find_next_block()
        if next_block in self.unaccessible:
            if next_block == '-':
                self.act('u')
                self.items.remove('K')
            elif next_block == 'T':
                self.act('c')
                if 'T' not in self.items:
                    self.items.append('T')
            elif next_block == '*':
                self.act('b')
                self.items.remove('D')
            elif next_block == '~':
                self.sailing = True
        self.act('F')
        return

    def find_meaning_of_life(self):
        if '$' in self.items:
            return self._astar((self.x, self.y), self.start_point)
        for y in range(len(self.known_world)):
            for x in range(len(self.known_world[y])):
                if self.known_world[y][x].upper() in self.desired or \
                    (self.known_world[y][x].upper() == 'T' and 'A' in self.items and 'T' not in self.items):
                    path = self._astar((self.x, self.y), (x,y))
                    if path is not None:
                        return path
                    else:
                        continue
        return None

    def walk_around(self, sight=5):
        max_mark = 0
        d=None
        def get_around(point):
            x, y = point
            around = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            around_points = []
            around = around[self.direction:] + around[:self.direction]
            for a in around:
                p = (x+a[0], y+a[1])
                if self.known_world[p[1]][p[0]] in \
                    [b for b in self.unaccessible + ['?']\
                         if self.unaccessible_solution.get(b) not in self.items or b=='*' or (b == 'T' and 'T' in self.items)]:
                    continue
                around_points.append(p)
            return around_points
        for i in range(4):
            x, y = self.x, self.y
            see = []
            if i % 2 == 0:
                if self.known_world[y+i-1][x] in self.unaccessible and not (self.sailing and self.known_world[y+i-1][x] == '~'):
                    continue
                y1 = y + 3 * (i-1)
                y2 = y + (i-1)
                if 0 < y1 < self.y_size:
                    if self.sailing:
                        if self.known_world[y2][x] != '~':
                            if not self._landing_valuable((y2, x)):
                                continue
                        nearest_tree = self._find_nearest_stuff('T')
                        if not ((nearest_tree and self._astar((self.x, self.y), nearest_tree))):
                            continue
                    see = self.known_world[y1][x-sight//2: x+sight//2+1]
                elif (x, y2) not in self.visited_places:
                    see = ['?'] * 5
            elif i % 2 == 1:
                if self.known_world[y][x+i-2] in self.unaccessible and not (self.sailing and self.known_world[y][x+i-2] == '~'):
                    continue
                x1 = x + 3 * (i-2)
                x2 = x + (i-2)
                if 0 <= x1 < self.x_size:
                    if self.sailing:
                        if self.known_world[y][x2] != '~':
                            if not self._landing_valuable((y, x2)):
                                continue
                        nearest_tree = self._find_nearest_stuff('T')
                        if not ((nearest_tree and self._astar((self.x, self.y), nearest_tree))):
                            continue
                    see = [self.known_world[_][x1] for _ in range(y-sight//2, y+sight//2+1)]
                elif (x2, y) not in self.visited_places:
                    see =  ['?']* 5
            mark = see.count('?')
            if mark > max_mark:
                d = i
                max_mark = max(mark, max_mark)
        if d is not None:
            self._turn_to_direction(d)
            self.act('f')
        else:
            around = get_around((self.x, self.y))
            earliest_visted = -1
            for p in around:
                visited_time = self.visited_places.get(p)
                if self.sailing:
                    if self.known_world[p[1]][p[0]] != '~' and not (self._landing_valuable(p) and self._find_nearest_stuff('T')):
                        continue
                if visited_time is None:
                    next_visit = p
                    break
                elif visited_time < earliest_visted or earliest_visted == -1:
                    next_visit = p
                    earliest_visted = visited_time
            self._go_to_neightbour_point(next_visit)


parser = ArgumentParser()
parser.add_argument('--port', dest='port')
args = parser.parse_args()
port = args.port

agent = Agent()
#agent._go_follow_path(path)

while True:
    # action = input("Enter Action(s): ")
    # try:
    #     agent.act(action)
    # except:
    #     print('Game over')
    #     sys.exit()
    agent.path = agent.find_meaning_of_life()
    if agent.path:
        agent._go_follow_path()
    else:
        agent.walk_around()

