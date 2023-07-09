import pygame
from pygame.locals import *

import pygame_gui
import sys
import os

from grid import *
from pathfinding_algorithms import *
from maze_generation_algorithms import *
from networking import *

class GameUIManager:
    def __init__(self, screen_manager, rect_array_obj, grid, client, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict):
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.grid = grid
        self.client = client
        self.pathfinding_algorithms_dict = pathfinding_algorithms_dict
        self.maze_generation_algorithms_dict = maze_generation_algorithms_dict
        self.events_dict = events_dict
        self.screen_lock = False

        self.manager = pygame_gui.UIManager((screen_manager.screen_width, screen_manager.screen_height))
        self.run_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((800, 10), (130, 50)), text="Run", manager=self.manager)

        self.pathfinding_algorithms_options = ['Depth First Search', 'Breadth First Search', 'Dijkstra', 'A*', 'Greedy Best First Search', 'Bidirectional Best First Search']
        self.pathfinding_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 10), (200, 50)),
                                                                              options_list=self.pathfinding_algorithms_options,
                                                                              starting_option="A*",
                                                                              manager=self.manager)

        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 10), (200, 50)),
                                                                  options_list=['Manhattan Distance', 'Euclidean Distance'],
                                                                  starting_option='Manhattan Distance',
                                                                  manager=self.manager)

        self.maze_generation_algorithms_options = ['Random Maze', 'Random Weighted Maze', 'RD(Recursive Division)', 'RD Horizontal Skew', 'RD Vertical Skew']
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((480, 10), (220, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option='Random Maze',
                                                                                  manager=self.manager)

        # TODO(ali): Could remove this label if it isn't needed later
        self.resolution_divider_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 65), (200, 30)),
                                                                    text='Resolution Divider Slider',
                                                                    manager=self.manager)

        self.resolution_divider_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 95), (280, 25)),
                                                                                start_value=4,
                                                                                value_range=(1, 8),
                                                                                manager=self.manager)

        # TODO(ali): Could remove this label it isn't needed later
        self.pathfinding_algorithm_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((370, 65), (220, 30)),
                                                                             text='Pathfinding Algorithm Speed',
                                                                             manager=self.manager)

        self.pathfinding_algorithm_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((340, 95), (280, 25)),
                                                                                         start_value=25,
                                                                                         value_range=(12, 100),
                                                                                         manager=self.manager)

        # TODO(ali): Could remove this label if it isn't needed later
        self.recursive_division_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((660, 65), (220, 30)),
                                                                          text='Recursive Division speed',
                                                                          manager=self.manager)

        self.recursive_division_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((640, 95), (280, 25)),
                                                                                      start_value=15,
                                                                                      value_range=(10, 50),
                                                                                      manager=self.manager)

        self.marked_or_weighted_node_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 130), (150, 35)),
                                                                              options_list=['Marked', 'Weighted'],
                                                                              starting_option='Marked',
                                                                              manager=self.manager)

        self.weighted_node_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((185, 130), (100, 35)),
                                                                                 manager=self.manager)
        self.weighted_node_text_entry_line.set_text_length_limit(10)
        self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
        self.weighted_node_text_entry_line.disable()
        self.weighted_node_text_entry_line.set_text('   None')

        self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.ASTAR
        self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE
        self.recursive_division_skew = None
        self.pathfinding_algorithm_speed = 25
        self.recursive_division_speed = 15
        self.cursor_node_type = CursorNodeTypes.MARKED_NODE
        self.weight = 1

    def run_pathfinding_algorithm(self, pathfinding_algorithm, heuristic=None):
        self.rect_array_obj.reset_rect_array_adjacent_nodes()
        self.rect_array_obj.gen_rect_array_with_adjacent_nodes()
        self.rect_array_obj.reset_non_user_weights()

        pathfinding_algorithm.reset_checked_nodes_pointer()
        pathfinding_algorithm.reset_path_pointer()

        pathfinding_algorithm.reset_animated_checked_coords_stack()
        pathfinding_algorithm.reset_animated_path_coords_stack()

        pathfinding_algorithm.heuristic = heuristic
        pathfinding_algorithm.run()


    def create_empty_heuristics_menu(self):
        self.heuristics_menu.kill()
        self.heuristic = None
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((240, 10), (200, 50)),
                                                                  options_list=['None'],
                                                                  starting_option='None',
                                                                  manager=self.manager)
        self.heuristics_menu.disable()

    def create_heuristics_menu_with_distances(self, starting_value='Manhattan Distance'):
        self.heuristics_menu.kill()
        self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((240, 10), (200, 50)),
                                                                  options_list=['Manhattan Distance', 'Euclidean Distance'],
                                                                  starting_option=starting_value,
                                                                  manager=self.manager)

    def run_current_maze_generation_algorithm(self):
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()

        self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()
        # screen_lock = True

        match self.current_maze_generation_algorithm:
            case MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE:
                self.grid.reset_marked_nodes(False)
                self.grid.reset_all_weights(False)
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].create_random_marked_maze()
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

            case MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE:
                self.grid.reset_marked_nodes(False)
                self.grid.reset_all_weights(False)
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].create_random_weighted_maze()
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

            case MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION:
                self.grid.reset_marked_nodes()
                self.grid.reset_all_weights()

                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_animated_coords_stack()
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].skew = self.recursive_division_skew
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].run_recursive_division()

                pygame.time.set_timer(self.events_dict['DRAW_MAZE'], self.recursive_division_speed)
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.recursive_division_skew, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

    def get_current_pathfinding_algorithm(self):
        return self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm]

    def update_current_pathfinding_algorithm(self, pathfinding_algorithm):
        self.current_pathfinding_algorithm = pathfinding_algorithm
        match self.current_maze_generation_algorithm:
            case PathfindingAlgorithmTypes.DFS:
                starting_option = 'Depth First Search'
            case PathfindingAlgorithmTypes.BFS:
                starting_option = 'Breadth First Search'
            case PathfindingAlgorithmTypes.DIJKASTRA:
                starting_option = 'Dijkstra'
            case PathfindingAlgorithmTypes.ASTAR:
                starting_option = 'A*'
            case PathfindingAlgorithmTypes.GREEDY_BFS:
                starting_option = 'Greedy Best First Search'
            case PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS:
                starting_option = 'Bidirectional Best First Search'

        self.pathfinding_algorithms_menu.kill()
        self.pathfinding_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 10), (200, 50)),
                                                                              options_list=self.pathfinding_algorithms_options,
                                                                              starting_option=starting_option,
                                                                              manager=self.manager)

        if self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].heuristic == None:
            self.create_empty_heuristics_menu()
        else:
            self.heuristic = self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].heuristic
            match self.heuristic:
                case PathfindingHeuristics.EUCLIDEAN_DISTANCE:
                    self.create_heuristics_menu_with_distances('Euclidean Distance')
                case PathfindingHeuristics.MANHATTAN_DISTANCE:
                    self.create_heuristics_menu_with_distances()

    def get_current_maze_generation_algorithm(self):
        return self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm]

    def update_current_maze_generation_algorithm(self, maze_generation_algorithm):
        self.current_maze_generation_algorithm = maze_generation_algorithm
        match self.current_maze_generation_algorithm:
            case MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE:
                starting_value = 'Random Maze'
            case MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE:
                starting_value = 'Random Weighted Maze'
            case MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION:
                skew = self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].skew

                if skew == None:
                    starting_value = 'RD(Recursive Division)'
                elif skew == RecursiveDivisionSkew.HORIZONTAL:
                    starting_value = 'RD Horizontal Skew'
                elif skew == RecursiveDivisionSkew.VERTICAL:
                    starting_value = 'RD Vertical Skew'

        self.maze_generation_algorithms_menu.kill()
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((480, 10), (220, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option=starting_value,
                                                                                  manager=self.manager)
    def update_resolution_divider(self):
        self.resolution_divider_slider.set_current_value(self.screen_manager.resolution_divider)

    def update_screen_lock(self, screen_lock):
        self.screen_lock = screen_lock

    def get_pathfinding_algorithm_speed(self):
        return self.pathfinding_algorithm_speed

    def get_recursive_division_speed(self):
        return self.recursive_division_speed

    def get_cursor_node_type(self):
        return self.cursor_node_type

    def get_weight(self):
        return self.weight

    def update_pathfinding_algorithm_speed(self, pathfinding_algorithm_speed):
        self.pathfinding_algorithm_speed = pathfinding_algorithm_speed
        self.pathfinding_algorithm_speed_slider.set_current_value(self.pathfinding_algorithm_speed)

    def update_recursive_division_speed(self, recursive_division_speed):
        self.recursive_division_speed = recursive_division_speed
        self.recursive_division_speed_slider.set_current_value(self.recursive_division_speed)


    def handle_ui_drop_down_menu_changed_event(self, event):
        if event.ui_element == self.pathfinding_algorithms_menu:
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()

            match event.text:
                case 'Depth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DFS
                    self.create_empty_heuristics_menu()
                case 'Breadth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.BFS
                    self.create_empty_heuristics_menu()
                case 'Dijkstra':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DIJKASTRA
                    self.create_heuristics_menu_with_distances()
                case 'A*':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.ASTAR
                    self.create_heuristics_menu_with_distances()
                case 'Greedy Best First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.GREEDY_BFS
                    self.create_heuristics_menu_with_distances()
                case 'Bidirectional Best First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS
                    self.create_empty_heuristics_menu()

        if event.ui_element == self.heuristics_menu:
            match event.text:
                case 'Manhattan Distance':
                    self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
                case 'Euclidean Distance':
                    self.heuristic = PathfindingHeuristics.EUCLIDEAN_DISTANCE

        if event.ui_element == self.maze_generation_algorithms_menu:
            match event.text:
                case 'Random Maze':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE
                    self.run_current_maze_generation_algorithm()
                case 'Random Weighted Maze':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE
                    self.run_current_maze_generation_algorithm()
                case 'RD(Recursive Division)':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = None
                    self.run_current_maze_generation_algorithm()
                case 'RD Horizontal Skew':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = RecursiveDivisionSkew.HORIZONTAL
                    self.run_current_maze_generation_algorithm()
                case 'RD Vertical Skew':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = RecursiveDivisionSkew.VERTICAL
                    self.run_current_maze_generation_algorithm()

        if event.ui_element == self.marked_or_weighted_node_menu:
            match event.text:
                case 'Marked':
                    self.cursor_node_type = CursorNodeTypes.MARKED_NODE
                    self.weighted_node_text_entry_line.disable()
                    self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
                    self.weighted_node_text_entry_line.set_text('   None')
                case 'Weighted':
                    self.cursor_node_type = CursorNodeTypes.WEIGHTED_NODE
                    self.weighted_node_text_entry_line.enable()
                    self.weighted_node_text_entry_line.set_allowed_characters('numbers')
                    self.weighted_node_text_entry_line.set_text('1')
                    self.weight = 1

    def handle_ui_button_pressed_event(self, event):
        if event.ui_element == self.run_button:
            self.run_pathfinding_algorithm(self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm], self.heuristic)
            self.client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, self.current_pathfinding_algorithm, self.heuristic)

            pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], self.pathfinding_algorithm_speed)

    def handle_ui_horizontal_slider_moved_event(self, event):
        if event.ui_element == self.resolution_divider_slider:
            self.screen_manager.set_resolution_divider(event.value)
            self.rect_array_obj.reset_rect_array()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
            self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()
            self.client.create_network_event(NetworkingEventTypes.SET_RESOLUTION_DIVIDER, event.value)

        if event.ui_element == self.pathfinding_algorithm_speed_slider:
            if event.value != self.pathfinding_algorithm_speed:
                self.pathfinding_algorithm_speed = event.value
                self.client.create_network_event(NetworkingEventTypes.SET_PATHFINDING_ALGORITHM_SPEED, self.pathfinding_algorithm_speed)

        if event.ui_element == self.recursive_division_speed_slider:
            if event.value != self.recursive_division_speed:
                self.recursive_division_speed = event.value
                self.client.create_network_event(NetworkingEventTypes.SET_RECURSIVE_DIVISION_SPEED, self.recursive_division_speed)

    def handle_ui_text_entry_finished_event(self, event):
        if event.ui_element == self.weighted_node_text_entry_line:
            self.weight = int(event.text)

    def draw(self):
        self.manager.draw_ui(self.screen_manager.screen)