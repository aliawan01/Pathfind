import pygame
import pygame_gui
import sys

from animations import *
from color_manager import *
from grid import *
from ui_manager import *

from networking import *

from pathfinding_algorithms import *
from maze_generation_algorithms import *

import math

def set_current_pathfinding_algorithm(pathfinding_algorithm, rect_array, heuristic=None):
    rect_array.reset_rect_array_adjacent_nodes()
    rect_array.gen_rect_array_with_adjacent_nodes()
    rect_array.reset_non_user_weights()

    pathfinding_algorithm.reset_animated_checked_coords_stack()
    pathfinding_algorithm.reset_animated_path_coords_stack()

    pathfinding_algorithm.heuristic = heuristic
    pathfinding_algorithm.run()

    return pathfinding_algorithm

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 1000
    screen_height = 800

    grid_width = screen_width
    # grid_height = screen_height
    grid_height = 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfinding Visualizer")

    screen_manager = ScreenManager(screen, screen_width, screen_height, grid_width, grid_height, 4)

    print("Number of columns:", screen_manager.num_of_columns)
    print("Number of rows:", screen_manager.num_of_rows)

    rect_array = RectArray(screen_manager)
    animation_manager = AnimationManager(screen_manager, rect_array)
    color_manager = ColorManager(screen_manager, rect_array, animation_manager)

    grid = Grid(screen_manager, rect_array, color_manager, animation_manager)

    dfs = DFS(screen_manager, rect_array, color_manager, animation_manager)
    bfs = BFS(screen_manager, rect_array, color_manager, animation_manager)
    dijkastra = Dijkastra(screen_manager, rect_array, color_manager, animation_manager)
    astar = AStar(screen_manager, rect_array, color_manager, animation_manager)
    greedy_bfs = GreedyBFS(screen_manager, rect_array, color_manager, animation_manager)
    bidirectional_bfs = BidirectionalBFS(screen_manager, rect_array, color_manager, animation_manager)

    pathfinding_algorithms_dict = {
        PathfindingAlgorithmTypes.DFS: dfs,
        PathfindingAlgorithmTypes.BFS: bfs,
        PathfindingAlgorithmTypes.DIJKASTRA: dijkastra,
        PathfindingAlgorithmTypes.ASTAR: astar,
        PathfindingAlgorithmTypes.GREEDY_BFS: greedy_bfs,
        PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS: bidirectional_bfs
    }

    random_weighted_maze = RandomWeightedMaze(screen_manager, rect_array, color_manager, animation_manager)
    random_marked_maze = RandomMarkedMaze(screen_manager, rect_array, color_manager, animation_manager)
    recursive_division_maze = RecursiveDivisionMaze(screen_manager, rect_array, color_manager, animation_manager)

    maze_generation_algorithms_dict = {
        MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE: random_weighted_maze,
        MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE: random_marked_maze,
        MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION: recursive_division_maze,
    }

    DRAW_CHECKED_NODES = pygame.USEREVENT + 5
    DRAW_PATH = pygame.USEREVENT + 6
    DRAW_MAZE = pygame.USEREVENT + 7

    events_dict = {
        'DRAW_CHECKED_NODES': DRAW_CHECKED_NODES,
        'DRAW_PATH': DRAW_PATH,
        'DRAW_MAZE': DRAW_MAZE
    }

    server = Server(grid, color_manager)
    client = Client(screen_manager, grid, rect_array, pathfinding_algorithms_dict, maze_generation_algorithms_dict, animation_manager, events_dict, color_manager)

    ui_manager = GameUIManager(screen_manager, rect_array, grid, client, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict)
    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_pathfinding_algorithm = None
    current_maze_generation_algorithm = None

    pathfinding_algorithm_speed = ui_manager.get_pathfinding_algorithm_speed()
    recursive_division_speed = ui_manager.get_recursive_division_speed()

    # TODO(ali): Remove this when it is not needed
    rotation_matrix = [math.cos(math.radians(5)), -1*math.sin(math.radians(5)),
                       math.sin(math.radians(5)), math.cos(math.radians(5))]
    centerx = 670
    centery = 130

    top_left = (-20, 20)
    top_right = (20, 20)
    bottom_left = (-20, -20)
    bottom_right = (20, -20)

    while True:
        top_left = (rotation_matrix[0]*top_left[0] + rotation_matrix[1]*top_left[1],
                    rotation_matrix[2]*top_left[0] + rotation_matrix[3]*top_left[1])

        top_right = (rotation_matrix[0]*top_right[0] + rotation_matrix[1]*top_right[1],
                     rotation_matrix[2]*top_right[0] + rotation_matrix[3]*top_right[1])

        bottom_left = (rotation_matrix[0]*bottom_left[0] + rotation_matrix[1]*bottom_left[1],
                       rotation_matrix[2]*bottom_left[0] + rotation_matrix[3]*bottom_left[1])

        bottom_right = (rotation_matrix[0]*bottom_right[0] + rotation_matrix[1]*bottom_right[1],
                        rotation_matrix[2]*bottom_right[0] + rotation_matrix[3]*bottom_right[1])

        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                ui_manager.handle_ui_button_pressed_event(event)

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                ui_manager.handle_ui_drop_down_menu_changed_event(event)

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                ui_manager.handle_ui_horizontal_slider_moved_event(event)

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                ui_manager.handle_ui_text_entry_finished_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F6:
                    print("Set light theme!")
                    color_manager.set_and_animate_light_theme(current_pathfinding_algorithm)
                    client.create_network_event(NetworkingEventTypes.SEND_THEME)

                if event.key == pygame.K_F7:
                    print("Set dark theme")
                    color_manager.set_and_animate_dark_theme(current_pathfinding_algorithm)
                    client.create_network_event(NetworkingEventTypes.SEND_THEME)

                if event.key == pygame.K_F8:
                    # color_manager.set_and_animate_node_color(ColorNodeTypes.WEIGHTED_NODE_COLOR, color_manager.colors['purple'])
                    color_manager.set_and_animate_node_color(ColorNodeTypes.BORDER_COLOR, color_manager.colors['white'])
                    color_manager.set_and_animate_node_color(ColorNodeTypes.BOARD_COLOR, color_manager.colors['black'])
                    color_manager.set_and_animate_node_color(ColorNodeTypes.MARKED_NODE_COLOR, color_manager.colors['red'])

                if event.key == pygame.K_F9:
                    color_manager.set_and_animate_node_color(ColorNodeTypes.WEIGHTED_NODE_COLOR, color_manager.colors['violet'])

                if event.key == pygame.K_q:
                    client.create_network_event(NetworkingEventTypes.DISCONNECT_FROM_SERVER)
                    server.shutdown()
                    pygame.quit()
                    sys.exit()

                # TODO(ali): Toggle this if statement to make sure screen_lock works
                #            after you've finished testing the algorithms.
                # if screen_lock == False:
                if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_EQUALS:
                    screen_manager.increment_resolution_divider()
                    client.create_network_event(NetworkingEventTypes.SET_RESOLUTION_DIVIDER, screen_manager.resolution_divider)
                    rect_array.reset_rect_array()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                if event.key == pygame.K_MINUS:
                    screen_manager.decrement_resolution_divider()
                    client.create_network_event(NetworkingEventTypes.SET_RESOLUTION_DIVIDER, screen_manager.resolution_divider)
                    rect_array.reset_rect_array()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                # NOTE(ali): Clearing the entire board
                if event.key == pygame.K_c:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    client.create_network_event(NetworkingEventTypes.CLEAR_GRID)

                # # NOTE(ali): Clearing marked nodes
                if event.key == pygame.K_F3:
                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    grid.reset_marked_nodes()
                    client.create_network_event(NetworkingEventTypes.CLEAR_MARKED_NODES)

                # NOTE(ali): Clearing weighted nodes
                if event.key == pygame.K_F4:
                    grid.reset_all_weights()
                    client.create_network_event(NetworkingEventTypes.CLEAR_WEIGHTED_NODES)
                #
                # # NOTE(ali): Clearing checked nodes
                # if event.key == pygame.K_F3:
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #
                #     client.create_network_event(NetworkingEventTypes.CLEAR_CHECKED_NODES)
                #
                # # NOTE(ali): Clearing the path
                # if event.key == pygame.K_F4:
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     client.create_network_event(NetworkingEventTypes.CLEAR_PATH)

                # if event.key == pygame.K_s:
                #     mouse_pos = pygame.mouse.get_pos()
                #     grid.mark_weighted_node_at_mouse_pos(mouse_pos, 10)
                #     client.create_network_event(NetworkingEventTypes.ADD_WEIGHTED_NODE, mouse_pos, 10)
                #
                # if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_s:
                #     mouse_pos = pygame.mouse.get_pos()
                #     grid.unmark_weighted_node_at_mouse_pos(mouse_pos)
                #     client.create_network_event(NetworkingEventTypes.REMOVE_WEIGHTED_NODE, mouse_pos)
                #
                # if event.key == pygame.K_d:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.DFS, None)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(dfs, rect_array)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_b:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.BFS, None)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(bfs, rect_array)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_j:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.DIJKASTRA, None)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(dijkastra, rect_array)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_a:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.ASTAR, PathfindingHeuristics.MANHATTAN_DISTANCE)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(astar, rect_array, PathfindingHeuristics.MANHATTAN_DISTANCE)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_g:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.GREEDY_BFS, PathfindingHeuristics.MANHATTAN_DISTANCE)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(greedy_bfs, rect_array, PathfindingHeuristics.MANHATTAN_DISTANCE)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_w:
                #     client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS, None)
                #     current_pathfinding_algorithm = set_current_pathfinding_algorithm(bidirectional_bfs, rect_array)
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)
                #
                # if event.key == pygame.K_1:
                #     grid.reset_marked_nodes(False)
                #     grid.reset_all_weights(False)
                #
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     if current_maze_generation_algorithm != None:
                #         current_maze_generation_algorithm.reset_maze_pointer()
                #
                #     random_weighted_maze.reset_maze_pointer()
                #     random_weighted_maze.create_random_weighted_maze()
                #     client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE, random_weighted_maze.maze.to_list())
                #
                # if event.key == pygame.K_2:
                #     grid.reset_marked_nodes(False)
                #     grid.reset_all_weights(False)
                #
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     if current_maze_generation_algorithm != None:
                #         current_maze_generation_algorithm.reset_maze_pointer()
                #
                #     random_weighted_maze.reset_maze_pointer()
                #     random_marked_maze.create_random_marked_maze()
                #     client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE, random_marked_maze.maze.to_list())
                #
                # if event.key == pygame.K_3:
                #     grid.reset_marked_nodes()
                #     grid.reset_all_weights()
                #
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     current_maze_generation_algorithm = recursive_division_maze
                #     current_maze_generation_algorithm.reset_animated_coords_stack()
                #     current_maze_generation_algorithm.reset_maze_pointer()
                #
                #     recursive_division_maze.run_recursive_division()
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_MAZE, 15)
                #     print("Recursive division No skew:", recursive_division_maze.maze.to_list())
                #     client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())
                #
                # if event.key == pygame.K_4:
                #     grid.reset_marked_nodes()
                #     grid.reset_all_weights()
                #
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     current_maze_generation_algorithm = recursive_division_maze
                #     current_maze_generation_algorithm.reset_animated_coords_stack()
                #     current_maze_generation_algorithm.reset_maze_pointer()
                #
                #     recursive_division_maze.skew = RecursiveDivisionSkew.VERTICAL
                #     recursive_division_maze.run_recursive_division()
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_MAZE, 15)
                #     print("Recursive division Vertical skew:", recursive_division_maze.maze.to_list())
                #     client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())
                #
                # if event.key == pygame.K_5:
                #     grid.reset_marked_nodes()
                #     grid.reset_all_weights()
                #
                #     if current_pathfinding_algorithm != None:
                #         current_pathfinding_algorithm.reset_checked_nodes_pointer()
                #         current_pathfinding_algorithm.reset_path_pointer()
                #
                #     current_maze_generation_algorithm = recursive_division_maze
                #     current_maze_generation_algorithm.reset_animated_coords_stack()
                #     current_maze_generation_algorithm.reset_maze_pointer()
                #
                #     recursive_division_maze.skew = RecursiveDivisionSkew.HORIZONTAL
                #     recursive_division_maze.run_recursive_division()
                #     screen_lock = True
                #
                #     pygame.time.set_timer(DRAW_MAZE, 15)
                #     print("Recursive division Horizontal skew:", recursive_division_maze.maze.to_list())
                #     print(recursive_division_maze.maze.to_list())
                #
                #     client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())

                if event.key == pygame.K_F2:
                    client.connect_to_server("127.0.0.1", 5000)

                if event.key == pygame.K_F1:
                    server.run_server()
                    client.connect_to_server("127.0.0.1", 5000)

            if screen_lock == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mark_spray = True

                    elif event.button == 2:
                        mouse_pos = pygame.mouse.get_pos()
                        grid.mark_start_node_at_mouse_pos(mouse_pos)
                        client.create_network_event(NetworkingEventTypes.SET_START_NODE, mouse_pos)

                    elif event.button == 3:
                        unmark_spray = True

                if event.type == pygame.MOUSEBUTTONUP:
                    mark_spray = False
                    unmark_spray = False
                    
                if event.type == pygame.MOUSEWHEEL:
                    mouse_pos = pygame.mouse.get_pos()
                    grid.mark_end_node_at_mouse_pos(mouse_pos)
                    client.create_network_event(NetworkingEventTypes.SET_END_NODE, mouse_pos)

            if event.type == DRAW_CHECKED_NODES:
                if current_maze_generation_algorithm != None:
                    flag = current_pathfinding_algorithm.update_checked_nodes_pointer()
                    if flag == -1:
                        pygame.time.set_timer(DRAW_CHECKED_NODES, 0)
                        pygame.time.set_timer(DRAW_PATH, pathfinding_algorithm_speed)
                    else:
                        pygame.time.set_timer(DRAW_CHECKED_NODES, pathfinding_algorithm_speed)

            if event.type == DRAW_PATH:
                if current_maze_generation_algorithm != None:
                    flag = current_pathfinding_algorithm.update_path_pointer()
                    if flag == -1:
                        pygame.time.set_timer(DRAW_PATH, 0)
                        screen_lock = False
                    else:
                        pygame.time.set_timer(DRAW_PATH, pathfinding_algorithm_speed)

            if event.type == DRAW_MAZE:
                if current_maze_generation_algorithm != None:
                    flag = current_maze_generation_algorithm.update_maze_pointer()
                    if flag == -1:
                        pygame.time.set_timer(DRAW_MAZE, 0)
                        screen_lock = False
                    else:
                        pygame.time.set_timer(DRAW_MAZE, recursive_division_speed)

            ui_manager.manager.process_events(event)


        ui_manager.manager.update(time_delta)

        if mark_spray:
            mouse_pos = pygame.mouse.get_pos()
            node_type = ui_manager.get_cursor_node_type()
            weight = ui_manager.get_weight()
            grid.mark_node_at_mouse_pos(mouse_pos, node_type, weight)
            client.create_network_event(NetworkingEventTypes.ADD_NODE, mouse_pos, node_type, weight)

        elif unmark_spray:
            mouse_pos = pygame.mouse.get_pos()
            grid.unmark_node_at_mouse_pos(mouse_pos)
            client.create_network_event(NetworkingEventTypes.REMOVE_NODE, mouse_pos)

        screen.fill(color_manager.BOARD_COLOR)
        border_or_background_color = animation_manager.update_border_and_board_interpolation()

        if current_pathfinding_algorithm != None:
            current_pathfinding_algorithm.draw()

        if current_maze_generation_algorithm != None:
            current_maze_generation_algorithm.draw()

        grid.draw_rect_nodes()

        if border_or_background_color['BACKGROUND_COLOR'] != None:
            animation_manager.update_coords_animations(border_or_background_color['BACKGROUND_COLOR'])
        else:
            animation_manager.update_coords_animations(color_manager.BOARD_COLOR)

        if border_or_background_color['BORDER_COLOR'] != None:
            color_manager.set_node_color(ColorNodeTypes.BORDER_COLOR, border_or_background_color['BORDER_COLOR'])

        grid.draw_grid()

        pathfinding_algorithm_speed = ui_manager.get_pathfinding_algorithm_speed()
        recursive_division_speed = ui_manager.get_recursive_division_speed()
        current_pathfinding_algorithm = ui_manager.get_current_pathfinding_algorithm()
        current_maze_generation_algorithm = ui_manager.get_current_maze_generation_algorithm()

        new_resolution_divider = client.update_resolution_divider(screen_manager.resolution_divider)
        if new_resolution_divider[0]:
            client.apply_resolution_divider()
            ui_manager.update_resolution_divider()

        new_pathfinding_algorithm_speed = client.update_pathfinding_algorithm_speed(pathfinding_algorithm_speed)
        if new_pathfinding_algorithm_speed[0]:
            pathfinding_algorithm_speed = new_pathfinding_algorithm_speed[1]
            ui_manager.update_pathfinding_algorithm_speed(pathfinding_algorithm_speed)

        new_recursive_division_speed = client.update_recursive_division_speed(recursive_division_speed)
        if new_recursive_division_speed[0]:
            recursive_division_speed = new_recursive_division_speed[1]
            ui_manager.update_recursive_division_speed(recursive_division_speed)

        new_pathfinding_algorithm = client.update_current_pathfinding_algorithm(current_pathfinding_algorithm)
        if new_pathfinding_algorithm[0]:
            current_pathfinding_algorithm = new_pathfinding_algorithm[1]
            ui_manager.update_current_pathfinding_algorithm(current_pathfinding_algorithm.type)

        new_maze_generation_algorithm = client.update_current_maze_generation_algorithm(current_maze_generation_algorithm)
        if new_maze_generation_algorithm[0]:
            current_maze_generation_algorithm = new_maze_generation_algorithm[1]
            ui_manager.update_current_maze_generation_algorithm(current_maze_generation_algorithm.type)

        new_screen_lock = client.update_screen_lock(screen_lock)
        if new_screen_lock[0]:
            screen_lock = new_screen_lock[1]
            ui_manager.update_screen_lock(screen_lock)

        server.get_pathfinding_algorithm_speed_and_recursive_division_speed(pathfinding_algorithm_speed, recursive_division_speed)

        ui_manager.draw()
        # pygame.draw.rect(screen, color_manager.colors['green'], my_rect)
        pygame.draw.aaline(screen, color_manager.colors['green'], (top_left[0] + centerx, top_left[1] + centery), (top_right[0] + centerx, top_right[1] + centery))
        pygame.draw.aaline(screen, color_manager.colors['green'], (top_right[0] + centerx, top_right[1] + centery), (bottom_right[0] + centerx, bottom_right[1] + centery))
        pygame.draw.aaline(screen, color_manager.colors['green'], (bottom_right[0] + centerx, bottom_right[1] + centery), (bottom_left[0] + centerx, bottom_left[1] + centery))
        pygame.draw.aaline(screen, color_manager.colors['green'], (bottom_left[0] + centerx, bottom_left[1] + centery), (top_left[0] + centerx, top_left[1] + centery))

        pygame.display.flip()


if __name__ == '__main__':
    main()