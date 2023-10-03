import pygame
from pygame.locals import *

import socket
import threading
import json

from pathfinding_algorithms import PathfindingAlgorithmTypes, PathfindingHeuristics
from maze_generation_algorithms import MazeGenerationAlgorithmTypes
from animations import AnimationTypes
from color_manager import *

from enum import IntEnum

class NetworkingEventTypes(IntEnum):
    DISCONNECT_FROM_SERVER = 0,
    ADD_NODE = 1,
    REMOVE_NODE = 2,
    SET_RESOLUTION_DIVIDER = 3,
    RUN_PATHFINDING_ALGORITHM = 4,
    RUN_MAZE_GENERATION_ALGORITHM = 5,
    CLEAR_GRID = 6,
    CLEAR_PATH = 7,
    CLEAR_CHECKED_NODES = 8,
    CLEAR_MARKED_NODES = 9,
    CLEAR_WEIGHTED_NODES = 10,
    SET_START_NODE = 11,
    SET_END_NODE = 12,
    SEND_GRID_UPON_CONNECTION = 13,
    SEND_THEME = 14,
    SET_PATHFINDING_ALGORITHM_SPEED = 15,
    SET_RECURSIVE_DIVISION_SPEED = 16,
    CANCEL_PATHFINDING_ALGORITHM = 17,
    CANCEL_RECURSIVE_DIVISION = 18

class Client:
    def __init__(self, screen_manager, grid, rect_array_obj, pathfinding_algorithms_dict, maze_generation_algorithms_dict, animation_manager, events_dict, color_manager):
        """
        Initalizes the Client class.

        @param screen_manager: ScreenManager
        @param grid: Grid
        @param rect_array_obj: RectArray
        @param pathfinding_algorithms_dict: Dict
        @param maze_generation_algorithms_dict: Dict
        @param animation_manager: AnimationManager
        @param events_dict: Dict
        @param color_manager: ColorManager
        """
        self.grid = grid
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.pathfinding_algorithms_dict = pathfinding_algorithms_dict
        self.maze_generation_algorithms_dict = maze_generation_algorithms_dict
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_to_server = False
        self.server_connection_broken = False
        self.received_new_theme = False
        self.pathfinding_algorithms_dict = pathfinding_algorithms_dict
        self.animation_manager = animation_manager
        self.color_manager: ColorManager = color_manager
        self.events_dict = events_dict

        self.changed_resolution_divider = False
        self.changed_pathfinding_algorithm_speed = False
        self.changed_recursive_division_speed = False
        self.changed_current_pathfinding_algorithm = False
        self.changed_current_maze_generation_algorithm = False

        self.cancel_pathfinding_algorithm = False
        self.cancel_recursive_division = False
        self.recursive_division_cut_off_point = None

        self.resolution_divider = None
        self.pathfinding_algorithm_speed = 25
        self.recursive_division_speed = 15
        self.current_pathfinding_algorithm = None
        self.current_maze_generation_algorithm = None

    def connect_to_server(self, server_ip_address, port):
        """
        If the connected_to_server attribute is set to False, this function
        will try to establish TCP connection with the server at the IP Address
        and Port Number given. If we are able to successfully connect to the server
        we will set the connected_to_server attribute to True and start a new Thread
        running the handle_server_events method. However, if we are unable to connect
        to the server we will return False.

        @param server_ip_address: Str
        @param port: int
        @return: bool or None
        """

        if self.connected_to_server == False:
            self.server_connection_broken = False
            try:
                self.client_socket = socket.create_connection((server_ip_address, port), 5)
                self.client_socket.settimeout(None)
            except:
                print(f"[CLIENT] Unable to connect to server with ip address: {server_ip_address} on port: {port}")
                return False

            print(f"[CLIENT] Connected to server with ip address: {server_ip_address} on port: {port}")
            self.connected_to_server = True
            threading.Thread(target=self.handle_server_events, daemon=True).start()

    def create_network_event(self, event_type, *args):
        """
        If the connected_to_server attribute is set to True, this function will
        send the data for the event we are creating to the server. This will be
        done by first identifying what NetworkingEventType the event_type variable
        we have been given is. Once we know which NetworkingEventType we are going
        to send we will create a dictionary called command which will contain a key
        which will be the event_type and the value for the key will the tuple args we
        are given if it is not empty, if args is empty we will simply make the value
        None. We will then turn the dictionary into json and send the json data to the
        server. However, if the event_type was NetworkingEventTypes.DISCONNECT_FROM_SERVER
        then we will also want to shut down the socket after sending the command to the server
        and set the connected_to_sever attribute to False.

        @param event_type: NetworkingEventTypes
        @param args: Tuple
        """
        if self.connected_to_server:
            match event_type:
                case NetworkingEventTypes.DISCONNECT_FROM_SERVER:
                    command = {NetworkingEventTypes.DISCONNECT_FROM_SERVER: None}
                    self.connected_to_server = False
                    print("[CLIENT] Disconnected from server...")

                case NetworkingEventTypes.ADD_NODE:
                    # args = mouse pos, node type, weight
                    command = {NetworkingEventTypes.ADD_NODE: args}

                case NetworkingEventTypes.REMOVE_NODE:
                    # args = mouse pos
                    command = {NetworkingEventTypes.REMOVE_NODE: args}

                case NetworkingEventTypes.SET_RESOLUTION_DIVIDER:
                    # args = value of resolution divider
                    command = {NetworkingEventTypes.SET_RESOLUTION_DIVIDER: args}

                case NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM:
                    # args = pathfinding algorithm, heuristic(None if the algorithm doesn't use heuristics)
                    command = {NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM: args}

                case NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM:
                    # If the maze generation algorithm is a random maze
                    # args = maze generation algorithm, coords in the maze
                    # If the maze generation algorithm is a random weighted maze
                    # args = maze generation algorithm, coords in the maze with weights
                    # If the maze generation algorithm is recursive division
                    # args = maze generation algorithm, skew, coords in the maze
                    command = {NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM: args}

                case NetworkingEventTypes.CLEAR_GRID:
                    command = {NetworkingEventTypes.CLEAR_GRID: None}

                case NetworkingEventTypes.CLEAR_PATH:
                    command = {NetworkingEventTypes.CLEAR_PATH: None}

                case NetworkingEventTypes.CLEAR_CHECKED_NODES:
                    command = {NetworkingEventTypes.CLEAR_CHECKED_NODES: None}

                case NetworkingEventTypes.CLEAR_MARKED_NODES:
                    command = {NetworkingEventTypes.CLEAR_MARKED_NODES: None}

                case NetworkingEventTypes.CLEAR_WEIGHTED_NODES:
                    command = {NetworkingEventTypes.CLEAR_WEIGHTED_NODES: None}

                case NetworkingEventTypes.SET_START_NODE:
                    # args = coords
                    command = {NetworkingEventTypes.SET_START_NODE: args}

                case NetworkingEventTypes.SET_END_NODE:
                    # args = coords
                    command = {NetworkingEventTypes.SET_END_NODE: args}

                case NetworkingEventTypes.SEND_GRID_UPON_CONNECTION:
                    # args = start node coords, end node coords, marked nodes, weighted nodes, resolution divider, pathfinding algorithm speed, recursive division speed
                    command = {NetworkingEventTypes.SEND_GRID_UPON_CONNECTION: args}

                case NetworkingEventTypes.SEND_THEME:
                    # command = theme name, theme keys, theme values
                    theme_name = self.color_manager.current_theme_name
                    theme_dict = self.color_manager.get_theme_colors_dict()

                    theme_keys = list(theme_dict.keys())
                    theme_values = list(theme_dict.values())

                    command = {NetworkingEventTypes.SEND_THEME: [theme_name, theme_keys, theme_values]}

                case NetworkingEventTypes.SET_PATHFINDING_ALGORITHM_SPEED:
                    # args = pathfinding algorithm speed
                    command = {NetworkingEventTypes.SET_PATHFINDING_ALGORITHM_SPEED: args}

                case NetworkingEventTypes.SET_RECURSIVE_DIVISION_SPEED:
                    # args = recursive division speed
                    command = {NetworkingEventTypes.SET_RECURSIVE_DIVISION_SPEED: args}

                case NetworkingEventTypes.CANCEL_PATHFINDING_ALGORITHM:
                    command = {NetworkingEventTypes.CANCEL_PATHFINDING_ALGORITHM: None}

                case NetworkingEventTypes.CANCEL_RECURSIVE_DIVISION:
                    # args = cut off point
                    command = {NetworkingEventTypes.CANCEL_RECURSIVE_DIVISION: args}

            print("[SOME CLIENT]: Created and sent event: ", command)
            try:
                self.client_socket.sendall(json.dumps(command).encode())
            except BrokenPipeError:
                print("[SOME CLIENT] Can't send information to server, it has been shut down.")

            if command == NetworkingEventTypes.DISCONNECT_FROM_SERVER:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
                self.client_socket = None

    def update_resolution_divider(self, resolution_divider):
        """
        If the changed_resolution_divider attribute is set to True,
        this function will set the changed_resolution_divider attribute
        to False and return a list contain 2 elements which is the boolean
        value True and the self.resolution_divider attribute. However,
        if the changed_resolution_divider attribute is set to False, we will
        return a list containing the boolean value False and resolution_divider
        variable we have been given.

        @param resolution_divider: int
        @return: List
        """
        if self.changed_resolution_divider:
            self.changed_resolution_divider = False
            return [True, self.resolution_divider]
        else:
            return [False, resolution_divider]

    def update_pathfinding_algorithm_speed(self, pathfinding_algorithm_speed):
        """
        If the changed_pathfinding_algorithm_speed attribute is set to True,
        this function will set the changed_pathfinding_algorithm_speed attribute
        to False and return a list containing 2 elements which is the boolean
        value True and the self.pathfinding_algorithm_speed attribute. However,
        if the changed_pathfinding_algorithm_speed attribute is set to False, we will
        return a list containing the boolean value False and pathfinding_algorithm_speed
        variable we have been given.

        @param pathfinding_algorithm_speed: int
        @return: List
        """
        if self.changed_pathfinding_algorithm_speed:
            self.changed_pathfinding_algorithm_speed = False
            return [True, self.pathfinding_algorithm_speed]
        else:
            return [False, pathfinding_algorithm_speed]

    def update_recursive_division_speed(self, recursive_division_speed):
        """
        If the changed_recursive_division_speed attribute is set to True,
        this function will set the changed_recursive_division_speed attribute
        to False and return a list containing 2 elements which is the boolean
        value True and the self.recursive_division_speed attribute. However,
        if the changed_recursive_division_speed attribute is set to False, we will
        return a list containing the boolean value False and recursive_division_speed
        variable we have been given.

        @param recursive_division_speed: int
        @return: List
        """
        if self.changed_recursive_division_speed:
            self.changed_recursive_division_speed = False
            return [True, self.recursive_division_speed]
        else:
            return [False, recursive_division_speed]

    def update_current_pathfinding_algorithm(self, pathfinding_algorithm):
        """
        If the changed_current_pathfinding_algorithm attribute is set to True,
        this function will set the changed_current_pathfinding_algorithm attribute
        to False and return a list containing 2 elements which is the boolean
        value True and the self.current_pathfinding_algorithm attribute. However,
        if the changed_current_pathfinding_algorithm attribute is set to False, we will
        return a list containing the boolean value False and current_pathfinding_algorithm
        variable we have been given.

        @param pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        @return: List
        """
        if self.changed_current_pathfinding_algorithm:
            self.changed_current_pathfinding_algorithm = False
            return [True, self.current_pathfinding_algorithm]
        else:
            return [False, pathfinding_algorithm]

    def update_current_maze_generation_algorithm(self, maze_generation_algorithm):
        """
        If the changed_current_maze_generation_algorithm attribute is set to True,
        this function will set the changed_current_maze_generation_algorithm attribute
        to False and return a list containing 2 elements which is the boolean
        value True and the self.current_maze_generation_algorithm attribute. However,
        if the changed_current_maze_generation_algorithm attribute is set to False, we will
        return a list containing the boolean value False and current_maze_generation_algorithm
        variable we have been given.

        @param maze_generation_algorithm: An instance of a child class of the MazeGenerationAlgorithm class.
        @return: List
        """
        if self.changed_current_maze_generation_algorithm:
            self.changed_current_maze_generation_algorithm = False
            return [True, self.current_maze_generation_algorithm]
        else:
            return [False, maze_generation_algorithm]

    def reset_cancel_pathfinding_algorithm(self):
        """
        This function will set the cancel_pathfinding_algorithm to False
        """
        self.cancel_pathfinding_algorithm = False

    def reset_cancel_recursive_division(self):
        """
        This function will set the cancel_recursive_division and
        recursive_division_cut_off_point attributes to False.
        """
        self.cancel_recursive_division = False
        self.recursive_division_cut_off_point = None

    def apply_resolution_divider(self):
        """
        This function will run the set_resolution_divider method in self.screen_manager
        and pass in the self.resolution_divider attribute so that resolution_divider attribute
        in self.screen_manager has been updated. We will then recreate the grid using the
        reset_rect_array method in self.rect_array_obj. If the current_pathfinding_algorithm attribute
        is not equal to None, we will also reset the path and checked nodes stacks using the reset_path_pointer
        and reset_checked_nodes_pointer methods respectively. Additionally, if the current_maze_generation_algorithm
        is not equal to None we will also reset the maze_pointer attribute using the reset_maze_pointer method.
        """
        self.screen_manager.set_resolution_divider(self.resolution_divider)
        self.rect_array_obj.reset_rect_array()

        if self.current_pathfinding_algorithm != None:
            self.current_pathfinding_algorithm.reset_path_pointer()
            self.current_pathfinding_algorithm.reset_checked_nodes_pointer()

        if self.current_maze_generation_algorithm != None:
            self.current_maze_generation_algorithm.reset_maze_pointer()

    def handle_server_events(self):
        """
        This function will be run in a separate thread. It will run a loop
        which will continuously check for new messages from the server as long as
        the connected_to_server attribute is set to True. If it receives and event
        from the server it will turn the json string into a dictionary and interpret
        the NetworkingEventType the dictionary contains. Depending upon what the
        NetworkingEventType is the function will then apply the event.

        @return: None
        """
        while self.connected_to_server:
            try:
                server_events = self.client_socket.recv(100000).decode()
            except (BrokenPipeError, ConnectionResetError):
                self.server_connection_broken = True
                self.connected_to_server = False
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
                self.client_socket = None
                return

            server_events_list = [event+'}' for event in server_events.split('}')]
            if server_events_list[-1] == '}':
                server_events_list.pop(-1)

            for server_event in server_events_list:
                print(f"[CLIENT RECEIVED EVENT]: Received an event -> {server_event}")

                command = json.loads(server_event)
                event_type = list(command.keys())[0]
                args = command[event_type]

                match NetworkingEventTypes(int(event_type)):
                    case NetworkingEventTypes.DISCONNECT_FROM_SERVER:
                        self.server_connection_broken = True
                        self.connected_to_server = False
                        self.client_socket.shutdown(socket.SHUT_RDWR)
                        self.client_socket.close()
                        self.client_socket = None
                        print("[CLIENT] Told to disconnect from the server...")

                    case NetworkingEventTypes.ADD_NODE:
                        mouse_pos = args[0]
                        node_type = args[1]
                        weight = args[2]
                        self.grid.mark_node_at_mouse_pos(mouse_pos, node_type, weight)

                    case NetworkingEventTypes.REMOVE_NODE:
                        mouse_pos = args[0]
                        self.grid.unmark_node_at_mouse_pos(mouse_pos)

                    case NetworkingEventTypes.SET_RESOLUTION_DIVIDER:
                        if args[0] != self.screen_manager.resolution_divider:
                            self.changed_resolution_divider = True
                            self.resolution_divider = args[0]

                    case NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM:
                        pathfinding_algorithm_type = PathfindingAlgorithmTypes(args[0])
                        if args[1] != None:
                            heuristic = PathfindingHeuristics(args[1])
                        else:
                            heuristic = None

                        self.rect_array_obj.reset_rect_array_adjacent_nodes()
                        self.rect_array_obj.gen_rect_array_with_adjacent_nodes()
                        self.rect_array_obj.reset_non_user_weights()

                        self.current_pathfinding_algorithm = self.pathfinding_algorithms_dict[pathfinding_algorithm_type]

                        self.current_pathfinding_algorithm.reset_animated_checked_coords_stack()
                        self.current_pathfinding_algorithm.reset_animated_path_coords_stack()

                        self.current_pathfinding_algorithm.heuristic = heuristic
                        self.current_pathfinding_algorithm.run()

                        pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], 25)

                        self.changed_current_pathfinding_algorithm = True

                    case NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM:
                        maze_generation_algorithm_type = args[0]
                        maze_generation_algorithm_skew = args[1]

                        self.current_maze_generation_algorithm = self.maze_generation_algorithms_dict[maze_generation_algorithm_type]
                        self.changed_current_maze_generation_algorithm = True

                        self.grid.reset_marked_nodes()
                        self.grid.reset_all_weights()

                        if self.current_pathfinding_algorithm != None:
                            self.current_pathfinding_algorithm.reset_path_pointer()
                            self.current_pathfinding_algorithm.reset_checked_nodes_pointer()

                        if self.current_maze_generation_algorithm != None:
                            self.current_maze_generation_algorithm.reset_maze_pointer()
                            self.current_maze_generation_algorithm.reset_animated_coords_stack()

                        if maze_generation_algorithm_type == MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE:
                            for coord, weight in args[1]:
                                self.rect_array_obj.array[coord[0]][coord[1]].is_user_weight = True
                                self.rect_array_obj.array[coord[0]][coord[1]].weight = weight
                                self.animation_manager.add_coords_to_animation_dict((coord[0], coord[1]), AnimationTypes.EXPANDING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)

                        elif maze_generation_algorithm_type == MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION:
                            self.current_maze_generation_algorithm.skew = maze_generation_algorithm_skew

                            self.current_maze_generation_algorithm.maze.stack = args[2]

                            pygame.time.set_timer(self.events_dict['DRAW_MAZE'], 15)

                        elif maze_generation_algorithm_type == MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE:
                            for y, x in args[1]:
                                self.rect_array_obj.array[y][x].marked = True
                                self.animation_manager.add_coords_to_animation_dict((y, x), AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)

                    case NetworkingEventTypes.CLEAR_GRID:
                        self.grid.reset_marked_nodes()
                        self.grid.reset_all_weights()

                        if self.current_pathfinding_algorithm != None:
                            self.current_pathfinding_algorithm.reset_path_pointer()
                            self.current_pathfinding_algorithm.reset_checked_nodes_pointer()

                        if self.current_maze_generation_algorithm != None:
                            self.current_maze_generation_algorithm.reset_maze_pointer()

                    case NetworkingEventTypes.CLEAR_PATH:
                        if self.current_pathfinding_algorithm != None:
                            self.current_pathfinding_algorithm.reset_path_pointer()

                    case NetworkingEventTypes.CLEAR_CHECKED_NODES:
                        if self.current_pathfinding_algorithm != None:
                            self.current_pathfinding_algorithm.reset_checked_nodes_pointer()

                    case NetworkingEventTypes.CLEAR_MARKED_NODES:
                        if self.current_maze_generation_algorithm != None:
                            self.current_maze_generation_algorithm.reset_maze_pointer()

                        self.grid.reset_marked_nodes()

                    case NetworkingEventTypes.CLEAR_WEIGHTED_NODES:
                        self.grid.reset_all_weights()

                    case NetworkingEventTypes.SET_START_NODE:
                        mouse_pos = args[0]
                        self.grid.mark_start_node_at_mouse_pos(mouse_pos)

                    case NetworkingEventTypes.SET_END_NODE:
                        mouse_pos = args[0]
                        self.grid.mark_end_node_at_mouse_pos(mouse_pos)

                    case NetworkingEventTypes.SEND_GRID_UPON_CONNECTION:
                        start_node_coord = args[0]
                        end_node_coord = args[1]
                        marked_nodes_coords = args[2]
                        weighted_nodes_coords = args[3]
                        resolution_divider = args[4]
                        pathfinding_algorithm_speed = args[5]
                        recursive_division_speed = args[6]

                        self.pathfinding_algorithm_speed = pathfinding_algorithm_speed
                        self.recursive_division_speed = recursive_division_speed

                        self.changed_pathfinding_algorithm_speed = True
                        self.changed_recursive_division_speed = True

                        self.screen_manager.set_resolution_divider(resolution_divider)
                        self.rect_array_obj.reset_rect_array()

                        self.grid.mark_start_node(self.rect_array_obj.array[start_node_coord[0]][start_node_coord[1]])
                        self.grid.mark_end_node(self.rect_array_obj.array[end_node_coord[0]][end_node_coord[1]])

                        self.grid.reset_marked_nodes()
                        self.grid.reset_all_weights()

                        if self.current_pathfinding_algorithm != None:
                            self.current_pathfinding_algorithm.reset_path_pointer()
                            self.current_pathfinding_algorithm.reset_checked_nodes_pointer()

                        if self.current_maze_generation_algorithm != None:
                            self.current_maze_generation_algorithm.reset_maze_pointer()

                        for coord in marked_nodes_coords:
                            self.grid.mark_node(CursorNodeTypes.MARKED_NODE, self.rect_array_obj.array[coord[0]][coord[1]], None)

                        for coord, weight in weighted_nodes_coords:
                            self.grid.mark_weighted_node(CursorNodeTypes.WEIGHTED_NODE, self.rect_array_obj.array[coord[0]][coord[1]], weight)

                    case NetworkingEventTypes.SEND_THEME:
                        theme_name = args[0]
                        theme_keys = args[1]
                        theme_values = args[2]

                        if self.color_manager.current_theme_name != theme_name:
                            self.received_new_theme = True

                        theme_colors_dict = {}
                        for i in range(len(theme_keys)):
                            theme_colors_dict[theme_keys[i]] = tuple(theme_values[i])

                        self.color_manager.current_theme_name = theme_name
                        self.color_manager.set_and_animate_theme_colors_dict(theme_colors_dict, self.current_pathfinding_algorithm)
                        self.color_manager.save_theme_to_themes_list(theme_name, theme_colors_dict)

                    case NetworkingEventTypes.SET_PATHFINDING_ALGORITHM_SPEED:
                        if args[0] != self.pathfinding_algorithm_speed:
                            self.pathfinding_algorithm_speed = args[0]
                            self.changed_pathfinding_algorithm_speed = True

                    case NetworkingEventTypes.SET_RECURSIVE_DIVISION_SPEED:
                        if args[0] != self.recursive_division_speed:
                            self.recursive_division_speed = args[0]
                            self.changed_recursive_division_speed = True

                    case NetworkingEventTypes.CANCEL_PATHFINDING_ALGORITHM:
                        self.cancel_pathfinding_algorithm = True

                    case NetworkingEventTypes.CANCEL_RECURSIVE_DIVISION:
                        self.recursive_division_cut_off_point = args[0]
                        self.cancel_recursive_division = True


class Server:
    def __init__(self, grid, color_manager):
        """
        Initalizes the Server class.

        @param grid: Grid
        @param color_manager: ColorManager
        """
        self.grid = grid
        self.color_manager = color_manager
        self.connected_clients_dict = {}
        self.server_running = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pathfinding_algorithm_speed = 25
        self.recursive_division_speed = 15

    def get_number_of_currently_connected_clients(self):
        """
        Returns the number of key-value pairs in the connected_clients_dict dictionary.

        @return: int
        """
        return len(self.connected_clients_dict.values())

    def handle_client(self, client_socket, client_address):
        """
        This function will be run in a separate thread. It will run a loop
        which will continuously check for new messages from the client_socket as long as
        the server_running attribute is set to True. When it receives a message from the client
        it will turn the json string into a dictionary and check if the event type of the dictionary is
        NetworkingEventTypes.DISCONNECT_FROM_SERVER in which case it will remove the client from the
        connected_clients_dict dictionary and exit the function. If the event is not
        NetworkingEventTypes.DISCONNECT_FROM_SERVER the server will send the dictionary to all the
        other clients in the connected_clients_dict dictionary.

        @param client_socket: socket.socket
        @param client_address: Str
        @return: None
        """
        print(f"[SERVER] Currently connected clients: {self.connected_clients_dict}")
        print(f"[SERVER] Length of currently connected clients: {self.get_number_of_currently_connected_clients()}")

        while self.server_running:
            try:
                client_info = client_socket.recv(100000).decode()
            except BrokenPipeError:
                return
            except ConnectionResetError:
                try:
                    self.connected_clients_dict.pop(client_address)
                except KeyError:
                    print("[SERVER] Disconnected client has already been removed from the connected_clients_dict dictionary.")
                print(f"[SERVER] Client disconnected: {client_address}")
                print(f"[SERVER] Currently connected clients: {self.connected_clients_dict}")
                print(f"[SERVER] Length of currently connected clients: {self.get_number_of_currently_connected_clients()}")
                return

            if client_info == '':
                return

            client_info_list = [event+'}' for event in client_info.split('}')]
            if client_info_list[-1] == '}':
                client_info_list.pop(-1)

            for client_info_event in client_info_list:
                command = json.loads(client_info_event)

                client_event_type = int(list(command.keys())[0])
                print("[SERVER] Received client event: ", NetworkingEventTypes(client_event_type))

                match client_event_type:
                    case NetworkingEventTypes.DISCONNECT_FROM_SERVER:
                        if len(self.connected_clients_dict) > 0:
                            self.connected_clients_dict.pop(client_address)
                            print(f"[SERVER] Client disconnected: {client_address}")
                            print(f"[SERVER] Currently connected clients: {self.connected_clients_dict}")

                    case _:
                        print("[SERVER] Other event recognized")
                        for other_client_socket in self.connected_clients_dict.values():
                            if other_client_socket != client_socket:
                                print("[SERVER] sent information to other client socket:", other_client_socket)
                                other_client_socket.sendall(client_info.encode())

    def set_pathfinding_algorithm_speed_and_recursive_division_speed(self, pathfinding_algorithm_speed, recursive_division_speed):
        """
        This function is a setter for both the pathfinding_algorithm_speed and recursive_division_speed attributes.

        @param pathfinding_algorithm_speed: int
        @param recursive_division_speed: int
        """
        self.pathfinding_algorithm_speed = pathfinding_algorithm_speed
        self.recursive_division_speed = recursive_division_speed

    def client_server_loop(self):
        """
        This function will be run in a separate thread. It will run a loop where it will
        continuously add clients who are trying to join the server to the connected_clients_dict
        dictionary as long as the server_running attribute is set to True. Once it has accepted a client
        it will get a list containing information about the grid from the get_board_info method in self.grid.
        It will append the pathfinding_algorithm_speed and recursive_division_speed attributes to this list and send
        it to the client. In addition to this, this function will get information about the current theme name using the
        current_theme_name attribute in self.color_manager as well as the dictionary containing the colours the theme uses
        from the get_theme_colors_dict method in self.color_manager, it will then send this information to the client.
        After this, the function will run the handle_client method in a separate thread and pass in information about the
        client's address and socket.

        @return: None
        """
        while self.server_running:
            try:
                client_socket, client_address = self.server_socket.accept()
            except:
                return

            self.connected_clients_dict[client_address] = client_socket

            if len(self.connected_clients_dict) > 1:
                board_info = self.grid.get_board_info()
                board_info.append(self.pathfinding_algorithm_speed)
                board_info.append(self.recursive_division_speed)

                theme_name = self.color_manager.current_theme_name
                theme_dict = self.color_manager.get_theme_colors_dict()

                theme_keys = list(theme_dict.keys())
                theme_values = list(theme_dict.values())

                grid_command = {NetworkingEventTypes.SEND_GRID_UPON_CONNECTION: board_info}
                theme_command = {NetworkingEventTypes.SEND_THEME: [theme_name, theme_keys, theme_values]}

                client_socket.sendall(json.dumps(grid_command).encode())
                client_socket.sendall(json.dumps(theme_command).encode())

            threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()

    def run_server(self, ip_address, port):
        """
        If the server_running variable is set to False, this function will set the
        server_running variable to True and create a new TCP socket on the server_socket
        attribute which will be bound to the IP Address and Port Number we have been given.
        We will then run the client_server_loop method in a separate thread.

        @param ip_address: Str
        @param port: int
        """
        if self.server_running == False:
            print(f"[SERVER] Running on ip address: {ip_address}, port: {port}")
            self.server_running = True
            if self.server_socket == None:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip_address, port))
            self.server_socket.listen(10)
            threading.Thread(target=self.client_server_loop, daemon=True).start()

    def kick_out_clients(self):
        """
        This function will go through each client in the connected_clients_dict dictionary
        and send them a dictionary whose key will be NetworkingEventTypes.DISCONNECT_FROM_SERVER
        and this key will have a value of None (this will tell all the clients to disconnect
        from the server).
        """
        if self.server_running:
            for client_socket in list(self.connected_clients_dict.values()):
                command = {NetworkingEventTypes.DISCONNECT_FROM_SERVER: None}
                client_socket.sendall(json.dumps(command).encode())

    def shutdown(self):
        """
        This function will shut down the server by doing the following:
        1) Running the kick_out_clients method.
        2) Closing the socket running on the server_socket attribute
        3) Set the connected_to_clients_dict dictionary to an empty dictionary.
        4) Set the server_running attribute to False
        5) Set the server_socket attribute to None.
        """
        if self.server_running:
            self.kick_out_clients()
            self.server_running = False
            self.connected_clients_dict = {}
            self.server_socket.close()
            self.server_socket = None
            print("[SERVER] Shutting down server...")