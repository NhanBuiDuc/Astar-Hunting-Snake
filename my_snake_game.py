import pygame
import math
from queue import PriorityQueue, Queue
import random
from pygame import draw
from itertools import cycle
WIDTH = 800
BLOCK_SIZE = 100
pygame.init()
pygame.display.set_caption("A* Path Finding Algorithm")
font = pygame.font.SysFont('arial', 25)
clock = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = TURQUOISE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.state = 'normal'
        self.search_state = 'normal'

    def get_pos(self):
        return self.row, self.col

    def is_body(self):
        return self.state == 'body'

    def is_normal(self):
        return self.state == 'normal'

    def is_head(self):
        return self.state == 'head'

    def is_food(self):
        return self.state == 'food'

    def is_open(self):
        return self.search_state == 'open'

    def is_closed(self):
        return self.search_state == 'closed'

    def is_barrier(self):
        return self.state == 'barrier'

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def make_body(self):
        self.color = BLUE
        self.state = 'body'

    def make_normal(self):
        self.color = TURQUOISE
        self.state = 'normal'

    def make_head(self):
        self.color = RED
        self.state = 'head'

    def make_food(self):
        self.color = RED
        self.state = 'food'

    def make_open(self):
        self.search_state = 'open'

    def make_closed(self):
        self.search_state = 'closed'

    def make_barrier(self):
        self.state = 'barrier'
        self.color = BLACK

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_body() and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_body() and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_body() and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_body() and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

    def __getitem__(self, items):
        return self


def draw(win, grid, rows, WIDTH):
    win.fill(TURQUOISE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, WIDTH)
    pygame.display.update()


def draw_grid(win, rows, WIDTH):
    gap = WIDTH // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (WIDTH, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, WIDTH))


def make_grid(rows):
    grid = []
    gap = WIDTH // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)
    return grid


def add_snake_grid(grid, body, head):
    for row in grid:
        for spot in row:
            for part in body:
                if spot.row == part[0] and spot.col == part[1]:
                    spot.make_body()
                if spot.row == head[0] and spot.col == head[1]:
                    spot.make_head()


def add_food_grid(grid, food):
    for row in grid:
        for spot in row:
            if spot.row == food[0] and spot.col == food[1]:
                spot.make_food()


def delete_food_grid(grid, food):
    for row in grid:
        for spot in row:
            if spot.row == food[0] and spot.col == food[1]:
                spot.make_normal()


def add_barrier(grid, barriers):
    for row in grid:
        for spot in row:
            for barrier in barriers:
                if spot.row == barrier[0] and spot.col == barrier[1]:
                    spot.make_barrier()


def h2(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(abs(x1 - x2) * abs(x1 - x2) + abs(y1 - y2) * abs(y1 - y2))


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def GetDirection(current, start):
    if(current.col == start.col and current.row > start.row):
        return 'right'
    if(current.col == start.col and current.row < start.row):
        return 'left'
    if(current.row == start.row and current.col < start.col):
        return 'up'
    if(current.row == start.row and current.col > start.col):
        return 'down'


def reconstruct_path(came_from, current, start):
    while current in came_from:

        if(came_from[current] == start and current.state != 'body' and current.state != 'barrier'):
            direction = GetDirection(current, start)
            return direction
        current = came_from[current]


def get_head(grid, head):
    row = head[0]
    col = head[1]
    start = grid[row][col]
    return start


def get_end(grid, food):
    row = food[0]
    col = food[1]
    end = grid[row][col]
    return end


def a_start(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            return reconstruct_path(came_from, end, start)
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


def a_start2(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h2(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            return reconstruct_path(came_from, end, start)
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h2(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


def a_start3(draw, grid, start, end):
    count = float("inf")
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            return reconstruct_path(came_from, end, start)
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count -= 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


class SnakeGame:
    def __init__(self, rows):
        self.display = pygame.display.set_mode((WIDTH, WIDTH))
        self.grid = []
        self.rows = rows
        self.head = [5, 5]
        self.lenght = 3
        self.body = [[3, 5], [4, 5], [5, 5]]
        self.tail = self.body[0]
        self.direction = 'right'
        self.food = [8, 5]
        self.score = 0
        self.barrier = []
        self.tolerance = 0
        self.movement = ['left', 'right', 'up', 'down']

    def main(self, run):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.update_score()
        self.update_all()
        start = get_head(self.grid, self.head)
        end = get_end(self.grid, self.food)

        direction = a_start(lambda: draw(self.display, self.grid,
                                         self.rows, WIDTH), self.grid, start, end)
        if direction != None:
            self.move(direction)
            self.update_all()
        else:
            direction = a_start3(lambda: draw(self.display, self.grid,
                                              self.rows, WIDTH), self.grid, start, end)
            if direction != None:
                self.move(direction)
                self.update_all()
            else:
                direction = a_start2(lambda: draw(self.display, self.grid,
                                                  self.rows, WIDTH), self.grid, start, end)
                if direction != None:
                    self.move(direction)
                    self.update_all()
                else:
                    if self.tolerance <= 4:
                        self.force_move()
                    else:
                        direction = a_start2(lambda: draw(self.display, self.grid,
                                                          self.rows, WIDTH), self.grid, start, end)
                        self.move(direction)
                        self.tolerance = 0
                        self.update_all()
        self.eat()
        clock.tick(20)

        draw(self.display, self.grid, self.rows, WIDTH)

    def force_move(self):
        if self._is_collision_up(self.head) != True:
            self.move('up')
            self.update_all()
            self.tolerance += 1
            return True
        elif self._is_collision_down(self.head) != True:
            self.move('down')
            self.update_all()
            self.tolerance += 1
            return True
        elif self._is_collision_left(self.head) != True:
            self.move('left')
            self.update_all()
            self.tolerance += 1
            return True
        elif self._is_collision_right(self.head) != True:
            self.move('right')
            self.update_all()
            self.tolerance += 1
            return True
        else:
            return False

    def update_all(self):
        self.grid = make_grid(self.rows)
        add_food_grid(self.grid, self.food)
        add_snake_grid(self.grid, self.body, self.head)
        add_barrier(self.grid, self.barrier)

    def move(self, direction):
        if self.up(direction, self.head) == True:
            del self.body[0]
            self.tail = self.body[0]
            return True
        if self.down(direction, self.head) == True:
            del self.body[0]
            self.tail = self.body[0]
            return True
        if self.right(direction, self.head) == True:
            del self.body[0]
            self.tail = self.body[0]
            return True
        if self.left(direction, self.head) == True:
            del self.body[0]
            self.tail = self.body[0]
            return True

    def eat(self):
        if(self.head == self.food):
            delete_food_grid(self.grid, self.food)
            self.random_food()
            if(self.direction == 'right'):
                new_tail = [self.tail[0] - 1, self.tail[1]]
                self.body.insert(0, new_tail)
                self.score += 1
                self.lenght += 1
                # self.grid = make_grid(self.rows)
                # self.display.fill(TURQUOISE)
                add_food_grid(self.grid, self.food)
                add_snake_grid(self.grid, self.body, self.head)
            elif(self.direction == 'left'):
                new_tail = [self.tail[0] + 1, self.tail[1]]
                self.body.insert(0, new_tail)
                self.score += 1
                self.lenght += 1
                # self.grid = make_grid(self.rows)
                # self.display.fill(TURQUOISE)
                add_food_grid(self.grid, self.food)
                add_snake_grid(self.grid, self.body, self.head)
            elif(self.direction == 'up'):
                new_tail = [self.tail[0], self.tail[1] + 1]
                self.body.insert(0, new_tail)
                self.score += 1
                self.lenght += 1
                # self.grid = make_grid(self.rows)
                # self.display.fill(TURQUOISE)
                add_food_grid(self.grid, self.food)
                add_snake_grid(self.grid, self.body, self.head)
            elif(self.direction == 'right'):
                new_tail = [self.tail[0], self.tail[1] - 1]
                self.body.insert(0, new_tail)
                self.score += 1
                self.lenght += 1
                # self.grid = make_grid(self.rows)
                # self.display.fill(TURQUOISE)
                add_food_grid(self.grid, self.food)
                add_snake_grid(self.grid, self.body, self.head)

    def game_over():
        pass

    def update_score(self):
        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [0, 0])
        pygame.display.update()

    def right(self, direction, head):
        if direction != 'right':
            return False
        else:
            if self._is_collision_right(head) == False:
                head = [head[0] + 1, head[1]]
                self.body.append(head)
                self.head = head
                return True
        return False

    def left(self, direction, head):
        if direction != 'left':
            return False
        else:
            if self._is_collision_left(head) == False:
                head = [head[0] - 1, head[1]]
                self.body.append(head)
                self.head = head
                return True
        return False

    def up(self, direction, head):
        if direction != 'up':
            return False
        else:
            if self._is_collision_up(head) == False:
                head = [head[0], head[1] - 1]
                self.body.append(head)
                self.head = head
                return True
        return False

    def down(self, direction, head):
        if direction != 'down':
            return False
        else:
            if self._is_collision_down(head) == False:
                head = [head[0], head[1] + 1]
                self.body.append(head)
                self.head = head
                return True
        return False

    def _is_collision_up(self, head):
        temp_head = [head[0], head[1] - 1]
        # hits boundary
        if temp_head[1] < 0:
            return True
        # hits itself
        for part in self.body:
            if temp_head == part:
                return True
        for block in self.barrier:
            if temp_head == block:
                return True
        return False

    def _is_collision_down(self, head):
        temp_head = [head[0], head[1] + 1]
        # hits boundary
        if temp_head[1] >= self.rows:
            return True
        # hits itself
        for part in self.body:
            if temp_head == part:
                return True
        for block in self.barrier:
            if temp_head == block:
                return True
        return False

    def _is_collision_left(self, head):
        temp_head = [head[0] - 1, head[1]]
        # hits boundary
        if temp_head[0] < 0:
            return True
        # hits itself
        for part in self.body:
            if temp_head == part:
                return True
        for block in self.barrier:
            if temp_head == block:
                return True
        return False

    def _is_collision_right(self, head):
        temp_head = [head[0] + 1, head[1]]
        # hits boundary
        if temp_head[0] > self.rows:
            return True
        # hits itself
        for part in self.body:
            if temp_head == part:
                return True
        for block in self.barrier:
            if temp_head == block:
                return True
        return False

    def random_food(self):
        foodx = round(random.randrange(0, self.rows - 1))
        foody = round(random.randrange(0, self.rows - 1))
        self.food = [foodx, foody]
        add_food_grid(self.grid,  self.food)
        for part in self.body:
            if(self.food == part):
                self.random_food()
                return
        for block in self.barrier:
            if self.food == block:
                self.random_food()
                return

    #
    #
    # snakegame.grid = make_grid(snakegame.rows)
    # snakegame.display.fill(WHITE)
    # snakegame.random_food()
    # add_snake_grid(snakegame.grid, snakegame.body, snakegame.head)
    # draw(snakegame.display, snakegame.grid, snakegame.rows, WIDTH)


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


if __name__ == '__main__':
    snakegame = SnakeGame(30)
    pygame.init()
    snakegame.update_all()
    draw(snakegame.display, snakegame.grid, snakegame.rows, WIDTH)
    done = False
    starte = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, snakegame.rows, WIDTH)
                spot = snakegame.grid[row][col]

                if spot.state == 'normal':
                    snakegame.barrier.append([spot.row, spot.col])
                    spot.make_barrier()
                    add_barrier(snakegame.grid, snakegame.barrier)
                    draw(snakegame.display, snakegame.grid, snakegame.rows, WIDTH)
            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, snakegame.rows, WIDTH)
                spot = snakegame.grid[row][col]

                if spot.state == 'barrier':
                    snakegame.barrier.remove([spot.row, spot.col])
                    spot.make_normal()
                    add_barrier(snakegame.grid, snakegame.barrier)
                    draw(snakegame.display, snakegame.grid, snakegame.rows, WIDTH)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = True
                    while run:
                        snakegame.main(run)
    pygame.quit()
