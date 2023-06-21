import pygame
from pygame.locals import *
import time

from animations import *

class ScreenManager:
    def __init__(self, screen, screen_width, screen_height, grid_width, grid_height, resolution_divider):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.resolution_divider = resolution_divider

    @property
    def num_of_rows(self):
        return self.grid_height//100*self.resolution_divider

    @property
    def num_of_columns(self):
        return self.grid_width//100*self.resolution_divider

    @property
    def row_width(self):
        return self.grid_height/self.num_of_rows

    @property
    def column_width(self):
        return self.grid_width/self.num_of_columns

    @property
    def row_width_int(self):
        return self.grid_height//self.num_of_rows

    @property
    def column_width_int(self):
        return self.grid_width//self.num_of_columns

    def increment_resolution_divider(self):
        if self.resolution_divider < 8:
            self.resolution_divider += 1

    def decrement_resolution_divider(self):
        if self.resolution_divider > 1:
            self.resolution_divider -= 1


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
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.array = self.gen_rect_array()

    def gen_rect_array(self):
        column_width = self.screen_manager.column_width
        row_width = self.screen_manager.row_width

        if self.screen_manager.resolution_divider > 4:
            column_width += 1
            row_width += 1

        rect_array = []

        pos_x = 0
        pos_y = 0
        # pos_y = self.screen_manager.screen_height - self.screen_manager.grid_height

        for y in range(self.screen_manager.num_of_rows):
            rect_array.append([])
            for x in range(self.screen_manager.num_of_columns):
                square_pygame_rect = pygame.Rect(pos_x, pos_y, column_width, row_width)
                rect_array[-1].append(RectNode(square_pygame_rect, [y, x]))
                pos_x += self.screen_manager.column_width
            else:
                pos_x = 0
                pos_y += self.screen_manager.row_width

        rect_array[0][0].is_start_node = True
        rect_array[0][0].weight = 0
        rect_array[-1][-1].is_end_node = True

        return rect_array

    def gen_rect_array_with_adjacent_nodes(self):
        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                # Right
                if x+1 < self.screen_manager.num_of_columns:
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
                if y+1 < self.screen_manager.num_of_rows:
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

    def reset_rect_array(self):
        self.array = self.gen_rect_array()
        
    def get_start_and_end_node_coords(self):
        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
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
    def __init__(self, screen_manager, rect_array_obj,  color_manager, animation_manager):
        self.screen_manager = screen_manager
        self.color_manager = color_manager
        self.rect_array_obj = rect_array_obj
        self.animation_manager = animation_manager

    def draw_grid(self):
        pos_x = self.screen_manager.column_width
        pos_y = self.screen_manager.row_width
        # pos_y = (self.screen_manager.screen_height - self.screen_manager.grid_height) + self.screen_manager.row_width

        for x in range(self.screen_manager.num_of_columns):
            pygame.draw.line(self.screen_manager.screen, self.color_manager.BORDER_COLOR, (pos_x, 0), (pos_x, self.screen_manager.grid_height))
            pos_x += self.screen_manager.column_width

        for x in range(self.screen_manager.num_of_rows):
            pygame.draw.line(self.screen_manager.screen, self.color_manager.BORDER_COLOR, (0, pos_y), (self.screen_manager.grid_width, pos_y))
            pos_y += self.screen_manager.row_width


    def draw_rect_nodes(self):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.is_start_node:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.START_NODE_COLOR, node.rect)
                elif node.is_end_node:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.END_NODE_COLOR, node.rect)
                elif node.marked:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.MARKED_NODE_COLOR, node.rect)
                elif node.is_user_weight:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.WEIGHTED_NODE_COLOR, node.rect)


    def mark_rect_node(self, node):
        if node.marked == False:
            node.marked = True
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)

    def unmark_rect_node(self, node):
        if node.marked:
            node.marked = False
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.MARKED_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)

    def mark_rect_node_at_mouse_pos(self, mouse_coords):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_rect_node(node)
                    break


    def unmark_rect_node_at_mouse_pos(self, mouse_coords):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.unmark_rect_node(node)
                    break


    def mark_weighted_node(self, node, weight):
        if node.is_user_weight == False and node.marked == False:
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)
            node.is_user_weight = True
            node.weight = weight

    def mark_weighted_node_at_mouse_pos(self, mouse_coords, weight):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_weighted_node(node, weight)
                    break

    def unmark_weighted_node(self, node):
        if node.is_user_weight:
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)
            node.is_user_weight = False
            node.weight = 1

    def unmark_weighted_node_at_mouse_pos(self, mouse_coords):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.unmark_weighted_node(node)
                    break

    def mark_start_node(self, node):
        original_start_node = None

        for row in self.rect_array_obj.array:
            for new_node in row:
                if new_node.is_start_node:
                    original_start_node = new_node

        if not node.is_start_node and not node.is_end_node:
            node.is_start_node = True
            original_start_node.is_start_node = False

            self.animation_manager.add_coords_to_animation_dict(original_start_node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.START_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.START_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)

    def mark_start_node_at_mouse_pos(self, mouse_coords):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_start_node(node)
                    break

    def mark_end_node(self, node):
        original_end_node = None

        for row in self.rect_array_obj.array:
            for new_node in row:
                if new_node.is_end_node:
                    original_end_node = new_node

        if not node.is_end_node and not node.is_start_node:
            node.is_end_node = True
            original_end_node.is_end_node = False

            self.animation_manager.add_coords_to_animation_dict(original_end_node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.END_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.END_NODE_COLOR, self.color_manager.BOARD_COLOR, 2)


    def mark_end_node_at_mouse_pos(self, mouse_coords):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_end_node(node)
                    break

    def reset_marked_nodes(self, animate=True):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.marked:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.MARKED_NODE_COLOR, self.color_manager.BOARD_COLOR)
                    node.marked = False

    def reset_all_weights(self, animate=True):
        for row in self.rect_array_obj.array:
            for node in row:
                if node.is_user_weight:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, self.color_manager.BOARD_COLOR)
                    node.is_user_weight = False
                    node.weight = 1

        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        self.rect_array_obj.array[start_node_coords[0]][start_node_coords[1]].weight = 0

    def get_board_info(self):
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        marked_coords = []
        weighted_coords = []

        for row in self.rect_array_obj.array:
            for node in row:
                if node.marked:
                    marked_coords.append(node.coords)
                elif node.is_user_weight:
                    weighted_coords.append([node.coords, node.weight])

        return [start_node_coords, end_node_coords, marked_coords, weighted_coords]