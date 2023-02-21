import pygame
from pygame.locals import *
from dataclasses import dataclass


@dataclass
class RectNode:
    rect: pygame.Rect
    marked: bool = False
 

def draw_grid(screen, screen_width, screen_height, square_num, color):
    rows_num = screen_width//square_num
    column_num = screen_height//square_num

    pos_x = square_num
    pos_y = square_num

    for x in range(rows_num):
        pygame.draw.line(screen, color, (pos_x, 0), (pos_x, screen_height))
        pos_x += square_num

    for x in range(column_num):
        pygame.draw.line(screen, color, (0, pos_y), (screen_width, pos_y))
        pos_y += square_num

def gen_rect_array(screen_width, screen_height, square_num):
    rows_num = screen_width//square_num
    column_num = screen_height//square_num

    rect_array = []

    pos_x = 0
    pos_y = 0

    for y in range(rows_num):
        rect_array.append([])
        for x in range(column_num):
            square_pygame_rect = pygame.Rect(pos_x, pos_y, square_num, square_num)
            rect_array[-1].append(RectNode(square_pygame_rect))
            pos_x += square_num
        else:
            pos_x = 0
            pos_y += square_num

    return rect_array

def draw_rect_nodes(screen, rect_array, color):
    for row in rect_array:
        for node in row:
            if node.marked:
                pygame.draw.rect(screen, color, node)


def mark_rect_node(screen, mouse_coords, rect_array):
    for row in rect_array:
        for node in row:
            if node.rect.collidepoint(mouse_coords):
                node.marked = True


