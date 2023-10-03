import pygame
from pygame.locals import *

from animations import *

from stack import Stack
from queue_classes import Queue, PriorityQueue

from enum import IntEnum

class PathfindingAlgorithmTypes(IntEnum):
    DFS = 0,
    BFS = 1,
    DIJKASTRA = 2,
    ASTAR = 3,
    GREEDY_BFS = 4,
    BIDIRECTIONAL_BFS = 5

class PathfindingHeuristics(IntEnum):
    MANHATTAN_DISTANCE = 0,
    EUCLIDEAN_DISTANCE = 1

class PathfindingAlgorithm:
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the PathfindingAlgorithm class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.animation_manager = animation_manager
        self.color_manager = color_manager
        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.drawn_checked_nodes = False
        self.checked_nodes_pointer = -1
        self.path_pointer = -1
        self.animated_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.animated_checked_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.animated_path_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.heuristic = None
        self.reset_checked_nodes = False
        self.reset_path_nodes = False
        self.type = type

    def reset_animated_checked_coords_stack(self):
        """
        This function will set the value of the self.animated_checked_coords attribute to be a new stack which
        will have a size that is the same as the number of nodes in the grid (we can calculate this by multiplying
        the num_of_rows attribute by the num_of_columns attribute which are both found in self.screen_manager.
        """
        self.animated_checked_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def reset_animated_path_coords_stack(self):
        """
        This function will set the value of the self.animated_path_coords attribute to be a new stack which
        will have a size that is the same as the number of nodes in the grid (we can calculate this by multiplying
        the num_of_rows attribute by the num_of_columns attribute which are both found in self.screen_manager.
        """
        self.animated_path_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def get_checked_nodes(self):
        """
        If the checked_nodes attribute is an empty stack this function will return None, otherwise
        it will return the checked_nodes attribute.

        @return: Stack or None
        """
        if self.checked_nodes == Stack(0):
            return None
        else:
            return self.checked_nodes

    def get_path(self):
        """
        If the path attribute is an empty stack this function will return None, otherwise
        it will return the path attribute.

        @return: Stack or None
        """
        if self.path == Stack(0):
            return None
        else:
            return self.path

    def reset_checked_nodes_pointer(self, check_for_colliding_path_nodes=False):
        """
        This function will first check if the reset_checked_nodes attribute is set to False.
        If it is then we will loop through all the coordinates in the checked_nodes stack
        up to the index of the checked_nodes_pointer attribute. In each iteration we will
        first check if the check_for_colliding_path_nodes variable is set to True, if it is
        we will check if the coordinate is in the path stack and if it is not in the path
        stack we will animate it using the add_coords_to_animation_dict in self.animation_manager.
        If the check_for_colliding_path_nodes variable is set to False we will animate the coordinates
        directly instead of checking if it is in the path stack. After this we will set the
        checked_nodes_pointer attribute to -1, the reset_checked_nodes attribute to True, and we will also
        reset the checked_nodes stack.

        @param check_for_colliding_path_nodes: Bool
        """
        if self.reset_checked_nodes == False:
            for coord in self.checked_nodes.gen_copy_without_empty_values()[:self.checked_nodes_pointer]:
                if check_for_colliding_path_nodes:
                    if coord not in self.path.gen_copy_without_empty_values():
                        self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.SHRINKING_SQUARE, self.color_manager.CHECKED_NODE_FOREGROUND_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)
                else:
                    self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.SHRINKING_SQUARE, self.color_manager.CHECKED_NODE_FOREGROUND_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)

        self.checked_nodes_pointer = -1
        self.reset_checked_nodes = True
        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def update_checked_nodes_pointer(self):
        """
        This function will increment the checked_nodes_pointer attribute and return 0 if
        the checked_nodes_pointer attribute is smaller than the total size of the checked_nodes
        stack (we can get the total size of the stack by using the get_size method in self.checked_nodes),
        otherwise we will return -1.

        @return: int
        """
        if self.checked_nodes_pointer != self.checked_nodes.get_size():
            self.checked_nodes_pointer += 1
            return 0
        else:
            return -1

    def reset_path_pointer(self, use_checked_nodes_foreground_color=False):
        """
        This function will first check if the reset_path_nodes attribute is set to False and
        the path_pointer attribute is not equal to -1. If this is true we will loop through all
        the coordinates in the path stack up to the index of the path_pointer attribute. In each
        iteration we will first check if the use_checked_nodes_foreground_color variable is set to
        True, if it is we will then check if the coordinate is in the checked_nodes stack, and if this
        condition is also true we will then animate the coordinates using the add_coords_to_animation_dict
        method in self.animation_manager with the background colour being ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR,
        and we will move onto the next iteration from there. If the iteration has not been continued we will animate
        the coordinates with the normal background colour. After this, we will set the path_pointer attribute to -1,
        the reset_path_nodes attribute to True, and we will also reset the path stack.

        @param use_checked_nodes_foreground_color: Bool
        """
        if self.reset_path_nodes == False:
            if self.path_pointer != -1:
                for coord in self.path.gen_copy_without_empty_values()[:self.path_pointer]:
                    if use_checked_nodes_foreground_color:
                        if coord in self.checked_nodes.gen_copy_without_empty_values():
                            self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.SHRINKING_SQUARE, self.color_manager.PATH_NODE_FOREGROUND_COLOR, self.color_manager.CHECKED_NODE_FOREGROUND_COLOR)
                            continue

                    self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.SHRINKING_SQUARE, self.color_manager.PATH_NODE_FOREGROUND_COLOR, self.color_manager.BOARD_COLOR)

        self.path_pointer = -1
        self.reset_path_nodes = True
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def update_path_pointer(self):
        """
        This function will increment the path_pointer attribute and return 0 if the path_pointer
        attribute is smaller than the total size of the path stack (we can get the total size of
        the stack by using the get_size method in self.path), otherwise we will return -1.

        @return: int
        """
        if self.path_pointer != self.path.get_size():
            self.path_pointer += 1
            return 0
        else:
            return -1

    def get_euclidean_distance(self, coords, end_node_coords):
        """
        This function will calculate the Euclidean distance between
        2 coordinates.

        @param coords: List
        @param end_node_coords: List
        @return: int
        """
        diff_row = end_node_coords[0]+1 - coords[0]
        diff_column = end_node_coords[1]+1 - coords[1]
        return (diff_row**2) + (diff_column**2)

    def get_manhattan_distance(self, coords, end_node_coords):
        """
        This function will calculate the Manhattan distance between
        two coordinates.

        @param coords: List
        @param end_node_coords: List
        @return: int
        """
        diff_row = abs(end_node_coords[0] - coords[0])
        diff_column = abs(end_node_coords[1] - coords[1])
        manhattan_distance = diff_row + diff_column
        # NOTE(ali): This makes sure that the heuristic and distance values
        #            don't mess each other up.
        return manhattan_distance*3

    def draw(self):
        """
        This function is called every frame when we need to draw a pathfinding algorithm.

        When we first start drawing a pathfinding algorithm the self.checked_nodes_pointer attribute
        is set to 0. Over time, we increment the value of self.checked_nodes_pointer (this process is handled
        separately and not by this function) and start drawing and animating checked nodes onto the screen.

        Once the checked_nodes_pointer is equal to the total size of the checked_nodes stack (we can get the size of
        the stack using the get_size method in self.checked_nodes) we will then set the drawn_checked_nodes variable to
        True, and then we will start to draw and animate path nodes in the same way we drew and animated the checked nodes,
        but instead we will use the path_pointer attribute and path stack.
        """
        for x in range(self.checked_nodes_pointer):
            coord = self.checked_nodes.stack[x]

            if self.animated_checked_coords.exists(coord) == False:
                if self.rect_array_obj.array[coord[0]][coord[1]].is_user_weight == False:
                    self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.CIRCLE_TO_SQUARE, (self.color_manager.CHECKED_NODE_BACKGROUND_COLOR, self.color_manager.CHECKED_NODE_FOREGROUND_COLOR), AnimationBackgroundTypes.THEME_BACKGROUND)
                self.animated_checked_coords.push(coord)
            else:
                if self.rect_array_obj.array[coord[0]][coord[1]].is_user_weight == False:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.CHECKED_NODE_FOREGROUND_COLOR, self.rect_array_obj.array[coord[0]][coord[1]])

        if self.checked_nodes_pointer == self.checked_nodes.get_size() and self.drawn_checked_nodes == False:
            self.drawn_checked_nodes = True

        if self.drawn_checked_nodes:
            for x in range(self.path_pointer):
                coord = self.path.stack[x]

                if self.animated_path_coords.exists(coord) == False:
                    self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.EXPANDING_SQUARE, self.color_manager.PATH_NODE_FOREGROUND_COLOR, self.color_manager.PATH_NODE_BACKGROUND_COLOR)
                    self.animated_path_coords.push(coord)
                else:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.PATH_NODE_FOREGROUND_COLOR, self.rect_array_obj.array[coord[0]][coord[1]])


class DFS(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the DFS class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj, color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.DFS

    def run(self):
        """
        Runs the DFS (Depth First Search) pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_checked_nodes = False
        self.reset_path_nodes = False

        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        
        self.checked_nodes.push(start_node_coords)
        self.path.push(start_node_coords)

        running = True
        while running:
            if self.path.peek(False) == -1:
                running = False
                break

            for coords in self.rect_array_obj.get_valid_adjacent_nodes(self.path.peek()):
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


class BFS(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the BFS (Breadth First Search) class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj, color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.BFS

    def run(self):
        """
        Runs the BFS (Breadth First Search) pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        frontier = Queue()

        parent_child_dict = {}

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                parent_child_dict[(y, x)] = None

        self.checked_nodes.push(start_node_coords)
        frontier.enqueue(start_node_coords) 

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if self.checked_nodes.exists(coord) == False:
                    frontier.enqueue(coord)
                    self.checked_nodes.push(coord)
                    parent_child_dict[tuple(coord)] = current_coord

        
        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == start_node_coords:
                    break

                self.path.push(parent_coord)
                coord = parent_coord


        self.path.remove_empty_values()
        self.path.reverse()

class Dijkastra(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the Dijkastra class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj,  color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.DIJKASTRA

    def run(self):
        """
        Runs the Dijkastra pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        parent_child_dict = {}
        expanded_nodes = []
        frontier = PriorityQueue()

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                parent_child_dict[(y, x)] = None

        self.checked_nodes.push(start_node_coords)
        frontier.enqueue(start_node_coords, self.rect_array_obj.get_weight_at_node(start_node_coords))

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    current_distance = self.rect_array_obj.get_weight_at_node(current_coord)
                    coord_distance = self.rect_array_obj.get_weight_at_node(coord)

                    if frontier.exists(coord) == False:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + coord_distance)
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, current_distance + coord_distance)

                        self.checked_nodes.push(coord)
                    elif current_distance + 1 < coord_distance:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord

                        frontier.replace(coord, current_distance + 1)


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


class AStar(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the AStar class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj,  color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.ASTAR
        self.heuristic_dict = {}
        frontier = PriorityQueue()
        expanded_nodes = []

    def calculate_f_value(self, coords):
        """
        This function will calculate the f-value of the RectNode at the given coordinates.
        The f-value will be calculated by adding the weight of the RectNode at the coordinates
        given (we can get this information by passing in the coordinates given into the get_weight_at_node
        method in self.rect_array_obj) with the heuristic we have calculated for the RectNode at the coordinate
        (we can get the heuristic for the coordinate by passing the coordinate as a key into the heuristic_dict
        dictionary). We will then return this f-value.

        @param coords: List
        @return: int
        """
        g = self.rect_array_obj.get_weight_at_node(coords)
        h = self.heuristic_dict[tuple(coords)]
        return g + h

    def run(self):
        """
        Runs the A* pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        self.heuristic_dict = {}
        parent_child_dict = {}

        frontier = PriorityQueue()
        expanded_nodes = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                if self.heuristic == PathfindingHeuristics.MANHATTAN_DISTANCE:
                    distance = self.get_manhattan_distance([y, x], end_node_coords)
                else:
                    distance = self.get_euclidean_distance([y, x], end_node_coords)

                self.heuristic_dict[(y, x)] = distance
                parent_child_dict[(y, x)] = None

        frontier.enqueue(start_node_coords, self.calculate_f_value(start_node_coords))

        running = True
        while not frontier.is_empty() and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    current_distance = self.rect_array_obj.get_weight_at_node(current_coord)
                    coord_distance = self.rect_array_obj.get_weight_at_node(coord)

                    if frontier.exists(coord) == False:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, self.calculate_f_value(coord))

                        self.checked_nodes.push(coord)
                    elif current_distance + 1 < coord_distance:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord

                        frontier.replace(coord, self.calculate_f_value(coord))


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()



class GreedyBFS(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the GreedyBFS class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj,  color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.GREEDY_BFS
        self.h_parent_dict = {}

    def run(self):
        """
        Runs the Greedy BFS (Best First Search) pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        heuristic_dict = {}
        parent_child_dict = {}

        frontier = PriorityQueue()
        expanded_nodes = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                if self.heuristic == PathfindingHeuristics.MANHATTAN_DISTANCE:
                    distance = self.get_manhattan_distance([y, x], end_node_coords)
                else:
                    distance = self.get_euclidean_distance([y, x], end_node_coords)

                heuristic_dict[(y, x)] = distance
                parent_child_dict[(y, x)] = None

        frontier.enqueue(start_node_coords, heuristic_dict[tuple(start_node_coords)])

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    if frontier.exists(coord) == False:
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, heuristic_dict[tuple(coord)])

                        self.checked_nodes.push(coord)


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


class BidirectionalBFS(PathfindingAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the BidirectionalBFS class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj,  color_manager, animation_manager)
        self.type = PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS
        self.search_a_checked_nodes = Queue()
        self.search_b_checked_nodes = Queue()

    def find_common_coord(self):
        """
        This function will return the first coordinate it finds which is in both the
        search_a_checked_nodes stack and the search_b_checked_nodes stack.

        @return: List
        """
        for item in self.search_a_checked_nodes:
            if self.search_b_checked_nodes.exists(item):
                return item

    def run(self):
        """
        Runs the Bidirectional BFS (Best First Search) pathfinding algorithm and saves the coordinates of the
        checked nodes in the checked_nodes stack and the coordinates of the path nodes in the path stack.

        @return: Stack
        """
        self.reset_path_nodes = False
        self.reset_checked_nodes = False

        self.search_a_checked_nodes = Queue()
        self.search_b_checked_nodes = Queue()
        self.checked_nodes = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.path = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        search_a_frontier = Queue()
        search_b_frontier = Queue()

        search_a_parent_child_dict = {}
        search_b_parent_child_dict = {}

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                search_a_parent_child_dict[(y, x)] = None
                search_b_parent_child_dict[(y, x)] = None

        self.search_a_checked_nodes.enqueue(start_node_coords)

        search_a_frontier.enqueue(start_node_coords) 
        search_b_frontier.enqueue(end_node_coords) 

        running = True
        while (search_a_frontier.is_empty() == False and search_b_frontier.is_empty() == False) and running:
            search_a_current_coord = search_a_frontier.dequeue()
            search_b_current_coord = search_b_frontier.dequeue()

            common_coord = self.find_common_coord()
            if common_coord != None:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(search_a_current_coord):
                if self.search_a_checked_nodes.exists(coord) == False:
                    search_a_frontier.enqueue(coord)
                    self.search_a_checked_nodes.enqueue(coord)
                    search_a_parent_child_dict[tuple(coord)] = search_a_current_coord

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(search_b_current_coord):
                if self.search_b_checked_nodes.exists(coord) == False:
                    search_b_frontier.enqueue(coord)
                    self.search_b_checked_nodes.enqueue(coord)
                    search_b_parent_child_dict[tuple(coord)] = search_b_current_coord

        
        if running == False:
            common_coord = self.find_common_coord()

            path_a = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
            path_b = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

            search_a_coord = common_coord
            search_b_coord = common_coord

            path_a.push(common_coord)
            coord = common_coord
            while True:
                parent_coord = search_a_parent_child_dict[tuple(coord)]
                if parent_coord == start_node_coords:
                    break

                path_a.push(parent_coord)
                coord = parent_coord

            path_a.reverse()

            coord = common_coord
            while True:
                parent_coord = search_b_parent_child_dict[tuple(coord)]
                if parent_coord == end_node_coords:
                    break

                path_b.push(parent_coord)
                coord = parent_coord

            self.path.merge(path_a, path_b)

        # NOTE(ali): Getting the checked nodes.
        while True:
            coord_a = self.search_a_checked_nodes.dequeue()
            coord_b = self.search_b_checked_nodes.dequeue()

            if coord_a != None:
                self.checked_nodes.push(coord_a)
            if coord_b != None:
                self.checked_nodes.push(coord_b)

            if coord_a == None and coord_b == None:
                self.checked_nodes.remove_empty_values()
                break
