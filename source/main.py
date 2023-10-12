import pygame
import pygame_gui
import sys
import faulthandler

from animations import *
from color_manager import *
from grid import *
from ui_manager import *

from networking import *

from pathfinding_algorithms import *
from maze_generation_algorithms import *

def main():
    """
    This is the main function which will run the game.
    """
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 1100
    screen_height = 800

    grid_width = screen_width
    # grid_height = screen_height
    grid_height = 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfind")
    pygame.display.set_icon(pygame.image.load('data/icon/game_icon.png'))

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

    DRAW_CHECKED_NODES = pygame.event.custom_type()
    DRAW_PATH = pygame.event.custom_type()
    DRAW_MAZE = pygame.event.custom_type()

    events_dict = {
        'DRAW_CHECKED_NODES': DRAW_CHECKED_NODES,
        'DRAW_PATH': DRAW_PATH,
        'DRAW_MAZE': DRAW_MAZE
    }

    server = Server(grid, color_manager)
    client = Client(screen_manager, grid, rect_array, pathfinding_algorithms_dict, maze_generation_algorithms_dict, animation_manager, events_dict, color_manager)

    ui_manager = GameUIManager(screen_manager, rect_array, color_manager, animation_manager, grid, client, server, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict)
    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_pathfinding_algorithm = None
    current_maze_generation_algorithm = None

    pathfinding_algorithm_speed = ui_manager.get_pathfinding_algorithm_speed()
    recursive_division_speed = ui_manager.get_recursive_division_speed()

    while True:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.create_network_event(NetworkingEventTypes.DISCONNECT_FROM_SERVER)
                server.shutdown()
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

            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                ui_manager.handle_ui_window_closed_event(event)

            if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                ui_manager.handle_ui_color_picker_color_picked_event(event)

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                ui_manager.handle_ui_selection_list_new_selection(event)

            if event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
                ui_manager.handle_ui_selection_list_dropped_selection(event)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                ui_manager.handle_ui_file_dialog_path_picked_event(event)

            if event.type == pygame.KEYDOWN:
                if screen_lock == False:
                    # NOTE(ali): Clearing the entire board
                    if event.key == pygame.K_c:
                        grid.reset_marked_nodes()
                        grid.reset_all_weights()

                        if current_pathfinding_algorithm != None:
                            current_pathfinding_algorithm.reset_path_pointer()
                            current_pathfinding_algorithm.reset_checked_nodes_pointer()

                        if current_maze_generation_algorithm != None:
                            current_maze_generation_algorithm.reset_maze_pointer()

                        client.create_network_event(NetworkingEventTypes.CLEAR_GRID)

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
                        ui_manager.build_ui_normal_state()
                    else:
                        pygame.time.set_timer(DRAW_PATH, pathfinding_algorithm_speed)

            if event.type == DRAW_MAZE:
                if current_maze_generation_algorithm != None:
                    flag = current_maze_generation_algorithm.update_maze_pointer()
                    if flag == -1:
                        pygame.time.set_timer(DRAW_MAZE, 0)
                        ui_manager.build_ui_normal_state()
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
        ui_manager.handle_ui_colour_animations()

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
            ui_manager.update_current_pathfinding_algorithm(current_pathfinding_algorithm.type, current_pathfinding_algorithm.heuristic, True)

        new_maze_generation_algorithm = client.update_current_maze_generation_algorithm(current_maze_generation_algorithm)
        if new_maze_generation_algorithm[0]:
            current_maze_generation_algorithm = new_maze_generation_algorithm[1]
            ui_manager.update_current_maze_generation_algorithm(current_maze_generation_algorithm.type, True)

        if client.cancel_pathfinding_algorithm:
            ui_manager.cancel_pathfinding_algorithm()
            client.reset_cancel_pathfinding_algorithm()

        if client.cancel_recursive_division:
            ui_manager.cancel_recursive_division(client.recursive_division_cut_off_point)
            client.reset_cancel_recursive_division()

        server.set_pathfinding_algorithm_speed_and_recursive_division_speed(pathfinding_algorithm_speed, recursive_division_speed)
        ui_manager.update_networking_server_connection_broken()
        ui_manager.update_client_received_new_theme()
        ui_manager.handle_ui_border_width_changed()

        if ui_manager.handle_bottom_ui_drop_down_menus_open() or ui_manager.handle_ui_window_open() or ui_manager.not_normal_state():
            screen_lock = True
        else:
            screen_lock = False

        ui_manager.draw()
        pygame.display.flip()


if __name__ == '__main__':
    faulthandler.enable()
    main()