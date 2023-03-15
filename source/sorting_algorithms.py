import pygame
from pygame.locals import *

from stack import Stack

class DFS:
    def __init__(self, screen, num_of_rows, num_of_columns):
        self.screen = screen
        self.num_of_columns = num_of_columns
        self.num_of_rows = num_of_rows
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)
        self.drawn_checked_nodes = False
        self.checked_nodes_pointer = -1
        self.path_pointer = -1

    def run_dfs(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        # Getting the coordinates of the start and end nodes.
        start_node_coords = False
        end_node_coords = False
        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                if rect_array[y][x].is_start_node:
                    start_node_coords = [y, x]
                elif rect_array[y][x].is_end_node:
                    end_node_coords = [y, x]

        
        self.checked_nodes.push(start_node_coords)
        self.path.push(start_node_coords)
        running = True
        while running:
            if self.path.peek(False) == -1:
                return Stack(0)
            for coords in rect_array_obj.get_valid_adjacent_nodes(rect_array[self.path.peek()[0]][self.path.peek()[1]]):
                if coords == end_node_coords:
                    running = False
                    break
                if coords not in self.checked_nodes.stack:
                    self.checked_nodes.push(coords)
                    self.path.push(coords)
                    break
            else:
                if self.path.get_size() == 0:
                    return Stack(0)
                else:
                    self.path.pop()

        self.checked_nodes.remove_empty_values()
        self.path.remove_empty_values()

    def get_checked_nodes(self):
        if self.checked_nodes == Stack(0):
            return None
        else:
            return self.checked_nodes

    def get_path(self):
        if self.path == Stack(0):
            return None
        else:
            return self.path

    def reset_checked_nodes_pointer(self):
        self.checked_nodes_pointer = -1

    def update_checked_nodes_pointer(self):
        if self.checked_nodes_pointer != self.checked_nodes.get_size():
            self.checked_nodes_pointer += 1
            return 0
        else:
            return -1

    def reset_path_pointer(self):
        self.path_pointer = -1

    def update_path_pointer(self):
        if self.path_pointer != self.path.get_size():
            self.path_pointer += 1
            return 0
        else:
            return -1

    def draw(self, rect_array, checked_node_color, path_node_color):
        for x in range(self.checked_nodes_pointer):
            coord = self.checked_nodes.stack[x]
            pygame.draw.rect(self.screen, checked_node_color, rect_array[coord[0]][coord[1]]) 

        if self.checked_nodes_pointer == self.checked_nodes.get_size():
            self.drawn_checked_nodes = True

        if self.drawn_checked_nodes:
            for x in range(self.path_pointer):
                coord = self.path.stack[x]
                pygame.draw.rect(self.screen, path_node_color, rect_array[coord[0]][coord[1]]) 


class BFS(DFS):
    def __init__(self, screen, num_of_rows, num_of_columns):
        super().__init__(screen, num_of_rows, num_of_columns)
        self.parent_child_dict = {}


    def run_bfs(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)
        self.parent_child_dict = {}

        self.checked_nodes_pointer = -1
        self.path_pointer = -1
        # TODO(ali): Make it a queue.
        frontier = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords = False
        end_node_coords = False
        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                if rect_array[y][x].is_start_node:
                    start_node_coords = [y, x]
                elif rect_array[y][x].is_end_node:
                    end_node_coords = [y, x]

        
        frontier.append(start_node_coords) 
        self.checked_nodes.push(start_node_coords)
        running = True
        while running and len(frontier) > 0:
            adjacent_coord_list = []
            current_coord = frontier[0]

            if current_coord == end_node_coords:
                running = False
                break
            adjacent_nodes = rect_array_obj.get_valid_adjacent_nodes(rect_array[current_coord[0]][current_coord[1]])
            for coord in adjacent_nodes:
                if coord not in self.checked_nodes.stack:
                    adjacent_coord_list.append(coord)
                    frontier.append(coord)
                    self.checked_nodes.push(coord)

            self.parent_child_dict[tuple(current_coord)] = adjacent_coord_list 
            frontier.pop(0)

        
        if len(frontier) > 0:
            # NOTE(ali): Making sure that we only show visited nodes up to the end node.
            cut_off_point = None
            checked_nodes_up_to_end_coord = None

            for i in range(self.checked_nodes.get_size()):
                if self.checked_nodes.stack[i] == frontier[0]:
                    checked_nodes_up_to_end_coord = self.checked_nodes.stack[:i]
                    break

            self.checked_nodes.stack = checked_nodes_up_to_end_coord
            self.checked_nodes.remove_empty_values()

            # NOTE(ali): Backtracking to find the path.
            self.path.push(end_node_coords)
            run = True
            for key in reversed(self.parent_child_dict.keys()):
                for value in self.parent_child_dict[key]:
                    if list(value) == self.path.peek():
                        self.path.push(list(key))
                    if list(value) == start_node_coords:
                        run = False
                        break
                        

        self.path.remove_empty_values()
        self.path.reverse()
