import pygame
from pygame.locals import *

from stack import Stack
from queue_classes import PriorityQueue

class SortingAlgorithm:
    def __init__(self, screen, num_of_rows, num_of_columns):
        self.screen = screen
        self.num_of_columns = num_of_columns
        self.num_of_rows = num_of_rows
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)
        self.drawn_checked_nodes = False
        self.checked_nodes_pointer = -1
        self.path_pointer = -1

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


class DFS(SortingAlgorithm):
    def __init__(self, screen, num_of_rows, num_of_columns):
        super().__init__(screen, num_of_rows, num_of_columns)

    def run_dfs(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = rect_array_obj.get_start_and_end_node_coords()
        
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



class BFS(SortingAlgorithm):
    def __init__(self, screen, num_of_rows, num_of_columns):
        super().__init__(screen, num_of_rows, num_of_columns)

    def run_bfs(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1
        # TODO(ali): Make it a queue.
        frontier = []

        parent_child_dict = {}

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = rect_array_obj.get_start_and_end_node_coords()

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

            parent_child_dict[tuple(current_coord)] = adjacent_coord_list 
            frontier.pop(0)

        
        if running == False:
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
            for key in reversed(parent_child_dict.keys()):
                for value in parent_child_dict[key]:
                    if list(value) == self.path.peek():
                        self.path.push(list(key))
                    if list(value) == start_node_coords:
                        run = False
                        break
                        

        self.path.remove_empty_values()
        self.path.reverse()

class Dijkastra(SortingAlgorithm):
    def __init__(self, screen, num_of_rows, num_of_columns):
        super().__init__(screen, num_of_rows,  num_of_columns)

    def run_dijkastra(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        distance_and_parent_dict = {}
        # TODO(ali): Technically this should be a priority queue will be useful 
        #            when adding weights.
        frontier = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                distance_and_parent_dict[(y, x)] = {"parentNodeCoords": None, "distance": None}
        

        distance_and_parent_dict[tuple(start_node_coords)]["distance"] = 0

        self.checked_nodes.push(start_node_coords)
        frontier.append(start_node_coords)
        running = True
        while len(frontier) > 0 and running:
            # self.sort_frontier()
            current_coords = frontier[0]
            for coord in rect_array_obj.get_valid_adjacent_nodes(rect_array[current_coords[0]][current_coords[1]]):
                if distance_and_parent_dict[tuple(coord)]["distance"] == None:
                    current_distance = distance_and_parent_dict[tuple(current_coords)]["distance"]
                    # TODO(ali): Will need to change this to actually check if the node has a
                    #           predefined distance (could add it to the node class) when we 
                    #           add weights, this will also need a priority queue.
                    distance_and_parent_dict[tuple(coord)]["distance"] = current_distance + 1
                    distance_and_parent_dict[tuple(coord)]["parentNodeCoords"] = current_coords

                    self.checked_nodes.push(coord)
                    frontier.append(coord)

                    if coord == end_node_coords:
                        running = False
                        break
            else:
                frontier.pop(0)


        self.checked_nodes.remove_empty_values()
        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = distance_and_parent_dict[tuple(coord)]["parentNodeCoords"]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


class AStar(SortingAlgorithm):
    def __init__(self, screen, num_of_rows, num_of_columns):
        super().__init__(screen, num_of_rows,  num_of_columns)
        self.g_h_parent_dict = {}
        self.frontier = PriorityQueue()
        self.expanded_nodes = []

    def get_euclidean_distance(self, coords, end_node_coords):
        diff_row = end_node_coords[0]+1 - coords[0]
        diff_column = end_node_coords[1]+1 - coords[1]
        return (diff_row**2) + (diff_column**2)

    def get_manhattan_distance(self, coords, end_node_coords):
        diff_row = abs(end_node_coords[0] - coords[0])
        diff_column = abs(end_node_coords[1] - coords[1])
        manhattan_distance = diff_row + diff_column
        return manhattan_distance*2

    def calculate_f_value(self, coords):
        g = self.g_h_parent_dict[tuple(coords)]["g"]
        h = self.g_h_parent_dict[tuple(coords)]["h"]
        return g + h

    def run_astar(self, rect_array_obj):
        rect_array = rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns*100)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        self.g_h_parent_dict = {}

        self.frontier = PriorityQueue()
        self.expanded_nodes = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                distance = self.get_manhattan_distance([y, x], end_node_coords)
                self.g_h_parent_dict[(y, x)] = {"g": None, "h": distance, "parentNodeCoords": None}

        self.g_h_parent_dict[tuple(start_node_coords)]["g"] = 0
        self.frontier.enqueue(start_node_coords, self.calculate_f_value(start_node_coords))

        old_x = 0
        print("\n---------------------------------")
        print("h values.\n")
        for coord in self.g_h_parent_dict.keys():
            if coord[0] > old_x:
                old_x += 1
                print()

            print(self.g_h_parent_dict[coord]["h"], end=' ')
            
        print()
        running = True
        while not self.frontier.is_empty() and running:
            current_coord = self.frontier.dequeue()
            self.expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in rect_array_obj.get_valid_adjacent_nodes(rect_array[current_coord[0]][current_coord[1]]):
                if coord not in self.expanded_nodes:
                    current_distance = self.g_h_parent_dict[tuple(current_coord)]["g"]
                    coord_distance = self.g_h_parent_dict[tuple(coord)]["g"]
                    # self.checked_nodes.push(coord)

                    # if coord_distance == None:
                        # coord_distance = 0

                    # if self.frontier.check_exists(coord) == False or current_distance + 1 < coord_distance:
                    if current_distance == 28:
                        print(f"need to break here, current_coord: {current_coord}, coord: {coord}, current_coord_distance: {current_distance}, coord_distance: {coord_distance} ")

                    if coord_distance == None:
                        self.g_h_parent_dict[tuple(coord)]["g"] = current_distance + 1
                        self.g_h_parent_dict[tuple(coord)]["parentNodeCoords"] = current_coord
                        # if current_distance + 1 < coord_distance:
                            # self.fronter.enqueue(coord, self.calculate_f_value(coord))
                            # self.frontier.replace(coord, current_h_value, current_h_value + 1)
                        # else:
                        self.frontier.enqueue(coord, self.calculate_f_value(coord))
                        self.checked_nodes.push(coord)
                    elif current_distance + 1 < coord_distance:
                        # self.frontier.enqueue(coord, self.calculate_f_value(coord))
                        self.g_h_parent_dict[tuple(coord)]["g"] = current_distance + 1
                        self.g_h_parent_dict[tuple(coord)]["parentNodeCoords"] = current_coord

                        self.frontier.replace(coord, self.calculate_f_value(coord))


        self.checked_nodes.remove_empty_values()
        print("\n---------------------------------")
        old_x = 0
        print("g values\n")
        for coord in self.g_h_parent_dict.keys():
            if coord[0] > old_x:
                old_x += 1
                print()

            print(self.g_h_parent_dict[coord]["g"], end=' ')

        print("\n---------------------------------")
        old_x = 0
        print("f = g + h\n")
        for coord in self.g_h_parent_dict.keys():
            if coord[0] > old_x:
                old_x += 1
                print()

            if self.g_h_parent_dict[coord]["g"] == None:
                g = 0
            else:
                g = self.g_h_parent_dict[coord]["g"]
                

            print(self.g_h_parent_dict[coord]["h"] + g, end=' ')

        # self.checked_nodes.remove_empty_values()
        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = self.g_h_parent_dict[tuple(coord)]["parentNodeCoords"]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


