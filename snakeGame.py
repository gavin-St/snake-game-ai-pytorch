import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 20)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# colors
WHITE = (255, 255, 255)
GRAY = (0, 25, 51)
RED1 = (181, 0, 0)
RED2 = (255, 80, 80)
GREEN1 = (0, 153, 0)
GREEN2 = (102, 255, 51)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20

class SnakeGameAI:

    def __init__(self, nth_game = 0, w=640, h=480, speed=5, hiScore = 0):
        self.w = w
        self.h = h
        self.speed = speed
        self.nth_game = nth_game
        self.hi_score = hiScore
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.nth_game = self.nth_game + 1


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.speed = min(self.speed + 5, 500)
                elif event.key == pygame.K_DOWN:
                    self.speed = max(self.speed - 5, 1)
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for i in range (self.w//BLOCK_SIZE):
            for j in range (self.h//BLOCK_SIZE):
                pygame.draw.rect(self.display, GRAY, pygame.Rect(i* BLOCK_SIZE, j*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x-1, pt.y-1, BLOCK_SIZE+2, BLOCK_SIZE+2))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x+3, pt.y+3, 15, 15))

        pygame.draw.rect(self.display, RED1, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, RED2, pygame.Rect(self.food.x+3, self.food.y+3, 14, 14))

        text1 = font.render("Score: " + str(self.score), True, WHITE)
        text2 = font.render("AI Generation: " + str(self.nth_game), True, WHITE)
        text3 = font.render("Press up/down arrows to increase/decrease speed!", True, WHITE)
        self.hi_score = max(self.hi_score,self.score)
        text4 = font.render("Highest Score: " + str(self.hi_score), True, WHITE)
        text5 = font.render("Speed: " + str(self.speed), True, WHITE)

        self.display.blit(text1, [6, 5])
        self.display.blit(text2, [6, 28])
        self.display.blit(text3, [6, 450])
        self.display.blit(text4, [111, 6])
        self.display.blit(text5, [6, 429])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)