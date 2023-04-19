import pygame
from pygame.locals import *
import time

from animations import *

class RectNode:
    def __init__(self, rect, coords):
        self.rect = rect
        self.coords = coords
        self.is_start_node = False
        self.is_end_node = False
        self.is_user_weight = False
        self.weight = 1
        self.marked = False
        self.adjacent_nodes = [None, None, None, None]

class RectArray:
    def __init__(self, screen_width, screen_height, num_of_rows, num_of_columns):
        self.num_of_rows = num_of_rows
        self.num_of_columns = num_of_columns
        self.row_width = screen_height/num_of_rows
        self.column_width = screen_width/num_of_columns
        self.array = self.gen_rect_array()

    def gen_rect_array(self):
        rect_array = []

        pos_x = 0
        pos_y = 0

        for y in range(self.num_of_rows):
            rect_array.append([])
            for x in range(self.num_of_columns):
                square_pygame_rect = pygame.Rect(pos_x, pos_y, self.column_width, self.row_width)
                rect_array[-1].append(RectNode(square_pygame_rect, [y, x]))
                pos_x += self.column_width
            else:
                pos_x = 0
                pos_y += self.row_width

        rect_array[0][0].is_start_node = True
        rect_array[0][0].weight = 0
        rect_array[-1][-1].is_end_node = True

        return rect_array

    def gen_rect_array_with_adjacent_nodes(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                # Right
                if x+1 < self.num_of_columns:
                    if self.array[y][x+1].marked == False:
                        self.array[y][x].adjacent_nodes[0] = [y, x+1]
                # Up
                if y-1 > -1:
                    if self.array[y-1][x].marked == False:
                        self.array[y][x].adjacent_nodes[1] = [y-1, x]
                # Left
                if x-1 > -1:
                    if self.array[y][x-1].marked == False:
                        self.array[y][x].adjacent_nodes[2] = [y, x-1]
                # Down
                if y+1 < self.num_of_rows:
                    if self.array[y+1][x].marked == False:
                        self.array[y][x].adjacent_nodes[3] = [y+1, x]

    def reset_rect_array_adjacent_nodes(self):
        for row in self.array:
            for node in row:
                node.adjacent_nodes = [None, None, None, None]

    def get_valid_adjacent_nodes(self, coords):
        node = self.array[coords[0]][coords[1]]
        valid_adjacent_nodes = [i for i in node.adjacent_nodes if i != None] 
        return valid_adjacent_nodes

    def get_start_and_end_node_coords(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                if self.array[y][x].is_start_node:
                    start_node_coords = [y, x]
                elif self.array[y][x].is_end_node:
                    end_node_coords = [y, x]

        return start_node_coords, end_node_coords


    def reset_non_user_weights(self):
        for row in self.array:
            for node in row:
                if node.is_user_weight == False:
                    node.weight = 1

        start_node_coords, end_node_coords = self.get_start_and_end_node_coords()
        self.array[start_node_coords[0]][start_node_coords[1]].weight = 0

    def get_weight_at_node(self, coord):
        return self.array[coord[0]][coord[1]].weight

    def set_weight_at_node(self, coord, weight):
        if self.array[coord[0]][coord[1]].is_user_weight == False:
            self.array[coord[0]][coord[1]].weight = weight

 
class Grid:
    def __init__(self, screen, rect_array_obj, screen_width, screen_height, num_of_rows, num_of_columns, colors, animation_manager):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_of_rows = num_of_rows
        self.num_of_columns = num_of_columns
        self.row_width = screen_height/num_of_rows
        self.column_width = screen_width/num_of_columns
        self.colors = colors
        self.rect_array_obj = rect_array_obj
        self.rect_array = self.rect_array_obj.array
        self.animation_manager = animation_manager

    def draw_grid(self, color):
        pos_x = self.column_width
        pos_y = self.row_width

        for x in range(self.num_of_columns):
            pygame.draw.line(self.screen, color, (pos_x, 0), (pos_x, self.screen_height))
            pos_x += self.column_width

        for x in range(self.num_of_rows):
            pygame.draw.line(self.screen, color, (0, pos_y), (self.screen_width, pos_y))
            pos_y += self.row_width


    def draw_rect_nodes(self, algorithm, start_node_color, end_node_color, marked_node_color, weighted_node_color):
        for row in self.rect_array:
            for node in row:
                if node.is_start_node:
                    pygame.draw.rect(self.screen, start_node_color, node)
                elif node.is_end_node:
                    pygame.draw.rect(self.screen, end_node_color, node)
                elif node.marked:
                    pygame.draw.rect(self.screen, marked_node_color, node)
                elif node.is_user_weight:
                    pygame.draw.rect(self.screen, weighted_node_color, node)


    def mark_rect_node(self, mouse_coords):
        for row in self.rect_array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    if node.marked == False:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.colors['red'], self.colors['black'], 2)
                        node.marked = True

                    break


    def unmark_rect_node(self, mouse_coords):
        for row in self.rect_array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    if node.marked:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['red'], self.colors['black'], 2)
                        node.marked = False

                    break


    def mark_weighted_node(self, mouse_coords, weight):
        for row in self.rect_array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    if node.is_user_weight == False and node.marked == False:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.colors['purple'], self.colors['black'], 2)
                        node.is_user_weight = True
                        node.weight = weight

                    break


    def unmark_weighted_node(self, mouse_coords):
        for row in self.rect_array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    if node.is_user_weight:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['purple'], self.colors['black'], 2)
                        node.is_user_weight = False
                        node.weight = 1

                    break

    def mark_start_node(self, mouse_coords):
        original_start_node = None
        new_start_node = None
        found_new_start_node = False

        for row in self.rect_array:
            for node in row:
                if node.is_start_node:
                    original_start_node = node

                if node.rect.collidepoint(mouse_coords) and not node.is_start_node and not node.is_end_node:
                    node.is_start_node = True
                    new_start_node = node
                    found_new_start_node = True

        if found_new_start_node:
            original_start_node.is_start_node = False

            self.animation_manager.add_coords_to_animation_dict(original_start_node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['blue'], self.colors['black'], 2)
            self.animation_manager.add_coords_to_animation_dict(new_start_node.coords, AnimationTypes.EXPANDING_SQUARE, self.colors['blue'], self.colors['black'], 2)

    def mark_end_node(self, mouse_coords):
        original_end_node = None
        new_end_node = None
        found_new_end_node = False

        for row in self.rect_array:
            for node in row:
                if node.is_end_node:
                    original_end_node = node

                if node.rect.collidepoint(mouse_coords) and not node.is_start_node and not node.is_end_node:
                    node.is_end_node = True
                    new_end_node = node
                    found_new_end_node = True

        if found_new_end_node:
            original_end_node.is_end_node = False

            self.animation_manager.add_coords_to_animation_dict(original_end_node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['green'], self.colors['black'], 2)
            self.animation_manager.add_coords_to_animation_dict(new_end_node.coords, AnimationTypes.EXPANDING_SQUARE, self.colors['green'], self.colors['black'], 2)

    def reset_marked_nodes(self, animate=True):
        for row in self.rect_array:
            for node in row:
                if node.marked:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['red'], self.colors['black'])
                    node.marked = False

    def reset_all_weights(self, animate=True):
        for row in self.rect_array:
            for node in row:
                if node.is_user_weight:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.colors['purple'], self.colors['black'])
                    node.is_user_weight = False
                    node.weight = 1

        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        self.rect_array[start_node_coords[0]][start_node_coords[1]].weight = 0
