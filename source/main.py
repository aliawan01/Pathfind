import pygame
import sys

from animations import *
from grid import *

from networking import *

from pathfinding_algorithms import *
from maze_generation_algorithms import *


colors = {
    'white': pygame.Color(255, 255, 255),
    'black': pygame.Color(0, 0, 0),
    'red': pygame.Color(255, 0, 0),
    'blue': pygame.Color(0, 0, 255),
    'green': pygame.Color(0, 255, 0),
    'orange': pygame.Color(255, 165, 0),
    'neon_blue': pygame.Color(4, 217, 255),
    'yellow': pygame.Color(255, 255, 0),
    'purple': pygame.Color(238, 130, 238)
}

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

    # screen_width = 1000
    # screen_height = 800
    screen_width = 500
    screen_height = 400

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfinding Visualizer")

    screen_manager = ScreenManager(screen, screen_width, screen_height, 4)

    print("Number of columns:", screen_manager.num_of_columns)
    print("Number of rows: ", screen_manager.num_of_rows)

    rect_array = RectArray(screen_manager)
    animation_manager = AnimationManager(screen_manager, rect_array)
    grid = Grid(screen_manager, rect_array, colors, animation_manager)

    dfs = DFS(screen_manager, rect_array, colors, animation_manager)
    bfs = BFS(screen_manager, rect_array, colors, animation_manager)
    dijkastra = Dijkastra(screen_manager, rect_array, colors, animation_manager)
    astar = AStar(screen_manager, rect_array, colors, animation_manager)
    greedy_bfs = GreedyBFS(screen_manager, rect_array, colors, animation_manager)
    bidirectional_bfs = BidirectionalBFS(screen_manager, rect_array, colors, animation_manager)

    pathfinding_algorithms_dict = {
        PathfindingAlgorithmTypes.DFS: dfs,
        PathfindingAlgorithmTypes.BFS: bfs,
        PathfindingAlgorithmTypes.DIJKASTRA: dijkastra,
        PathfindingAlgorithmTypes.ASTAR: astar,
        PathfindingAlgorithmTypes.GREEDY_BFS: greedy_bfs,
        PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS: bidirectional_bfs
    }

    random_weighted_maze = RandomWeightedMaze(screen_manager, rect_array, colors, animation_manager)
    random_marked_maze = RandomMarkedMaze(screen_manager, rect_array, colors, animation_manager)
    recursive_division_maze = RecursiveDivisionMaze(screen_manager, rect_array, colors, animation_manager)

    maze_generation_algorithms_dict = {
        MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE: random_weighted_maze,
        MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE: random_marked_maze,
        MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION: recursive_division_maze,
    }


    DRAW_CHECKED_NODES = pygame.USEREVENT + 0
    DRAW_PATH = pygame.USEREVENT + 1
    DRAW_MAZE = pygame.USEREVENT + 2

    events_dict = {
        'DRAW_CHECKED_NODES': DRAW_CHECKED_NODES,
        'DRAW_PATH': DRAW_PATH,
        'DRAW_MAZE': DRAW_MAZE
    }

    server = Server(grid)
    client = Client(screen_manager, grid, rect_array, pathfinding_algorithms_dict, maze_generation_algorithms_dict, animation_manager, events_dict, colors)

    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_pathfinding_algorithm = None
    current_maze_generation_algorithm = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    client.create_network_event(NetworkingEventTypes.DISCONNECT_FROM_SERVER)
                    server.shutdown()
                    pygame.quit()
                    sys.exit()

                # TODO(ali): Toggle this if statement to make sure screen_lock works
                #            after you've finished testing the algorithms.
                # if screen_lock == False:
                if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_EQUALS:
                    client.create_network_event(NetworkingEventTypes.INCREMENT_RESOLUTION_DIVIDER)
                    screen_manager.increment_resolution_divider()
                    rect_array.reset_rect_array()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                if event.key == pygame.K_MINUS:
                    client.create_network_event(NetworkingEventTypes.DECREMENT_RESOLUTION_DIVIDER)
                    screen_manager.decrement_resolution_divider()
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

                # NOTE(ali): Clearing marked nodes
                if event.key == pygame.K_F1:
                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    grid.reset_marked_nodes()
                    client.create_network_event(NetworkingEventTypes.CLEAR_MARKED_NODES)

                # NOTE(ali): Clearing weighted nodes
                if event.key == pygame.K_F2:
                    grid.reset_all_weights()
                    client.create_network_event(NetworkingEventTypes.CLEAR_WEIGHTED_NODES)

                # NOTE(ali): Clearing checked nodes
                if event.key == pygame.K_F3:
                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()

                    client.create_network_event(NetworkingEventTypes.CLEAR_CHECKED_NODES)

                # NOTE(ali): Clearing the path
                if event.key == pygame.K_F4:
                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_path_pointer()

                    client.create_network_event(NetworkingEventTypes.CLEAR_PATH)

                if event.key == pygame.K_s:
                    mouse_pos = pygame.mouse.get_pos()
                    grid.mark_weighted_node_at_mouse_pos(mouse_pos, 10)
                    client.create_network_event(NetworkingEventTypes.ADD_WEIGHTED_NODE, mouse_pos, 10)

                if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_s:
                    mouse_pos = pygame.mouse.get_pos()
                    grid.unmark_weighted_node_at_mouse_pos(mouse_pos)
                    client.create_network_event(NetworkingEventTypes.REMOVE_WEIGHTED_NODE, mouse_pos)

                if event.key == pygame.K_d:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.DFS, None)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(dfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_b:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.BFS, None)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(bfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_j:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.DIJKASTRA, None)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(dijkastra, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_a:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.ASTAR, PathfindingHeuristics.MANHATTAN_DISTANCE)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(astar, rect_array, PathfindingHeuristics.MANHATTAN_DISTANCE)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_g:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.GREEDY_BFS, PathfindingHeuristics.MANHATTAN_DISTANCE)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(greedy_bfs, rect_array, PathfindingHeuristics.MANHATTAN_DISTANCE)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_w:
                    client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS, None)
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(bidirectional_bfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_1:
                    grid.reset_marked_nodes(False)
                    grid.reset_all_weights(False)

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    random_weighted_maze.reset_maze_pointer()
                    random_weighted_maze.create_random_weighted_maze()
                    client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE, random_weighted_maze.maze.to_list())

                if event.key == pygame.K_2:
                    grid.reset_marked_nodes(False)
                    grid.reset_all_weights(False)

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    random_marked_maze.create_random_marked_maze()
                    client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE, random_marked_maze.maze.to_list())

                if event.key == pygame.K_3:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    current_maze_generation_algorithm = recursive_division_maze
                    current_maze_generation_algorithm.reset_animated_coords_stack()
                    current_maze_generation_algorithm.reset_maze_pointer()

                    recursive_division_maze.run_recursive_division()
                    screen_lock = True

                    pygame.time.set_timer(DRAW_MAZE, 15)
                    print("Recursive division No skew:", recursive_division_maze.maze.to_list())
                    client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())

                if event.key == pygame.K_4:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    current_maze_generation_algorithm = recursive_division_maze
                    current_maze_generation_algorithm.reset_animated_coords_stack()
                    current_maze_generation_algorithm.reset_maze_pointer()

                    recursive_division_maze.skew = RecursiveDivisionSkew.VERTICAL
                    recursive_division_maze.run_recursive_division()
                    screen_lock = True

                    pygame.time.set_timer(DRAW_MAZE, 15)
                    print("Recursive division Vertical skew:", recursive_division_maze.maze.to_list())
                    client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())

                if event.key == pygame.K_5:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    current_maze_generation_algorithm = recursive_division_maze
                    current_maze_generation_algorithm.reset_animated_coords_stack()
                    current_maze_generation_algorithm.reset_maze_pointer()

                    recursive_division_maze.skew = RecursiveDivisionSkew.HORIZONTAL
                    recursive_division_maze.run_recursive_division()
                    screen_lock = True

                    pygame.time.set_timer(DRAW_MAZE, 15)
                    print("Recursive division Horizontal skew:", recursive_division_maze.maze.to_list())
                    print(recursive_division_maze.maze.to_list())

                    client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION, recursive_division_maze.maze.to_list())

                if event.key == pygame.K_9:
                    client.connect_to_server("127.0.0.1", 5000)

                if event.key == pygame.K_0:
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
                flag = current_pathfinding_algorithm.update_checked_nodes_pointer()
                if flag == -1:
                    pygame.time.set_timer(DRAW_CHECKED_NODES, 0)
                    pygame.time.set_timer(DRAW_PATH, 25)

            if event.type == DRAW_PATH:
                flag = current_pathfinding_algorithm.update_path_pointer()
                if flag == -1:
                    pygame.time.set_timer(DRAW_PATH, 0)
                    screen_lock = False

            if event.type == DRAW_MAZE:
                flag = current_maze_generation_algorithm.update_maze_pointer()
                if flag == -1:
                    pygame.time.set_timer(DRAW_MAZE, 0)
                    screen_lock = False


        if mark_spray:
            mouse_pos = pygame.mouse.get_pos()
            grid.mark_rect_node_at_mouse_pos(mouse_pos)
            client.create_network_event(NetworkingEventTypes.ADD_MARKED_NODE, mouse_pos)
        elif unmark_spray:
            mouse_pos = pygame.mouse.get_pos()
            grid.unmark_rect_node_at_mouse_pos(mouse_pos)
            client.create_network_event(NetworkingEventTypes.REMOVE_MARKED_NODE, mouse_pos)

        screen.fill(colors['black'])
        if current_pathfinding_algorithm != None:
            current_pathfinding_algorithm.draw(colors['neon_blue'], colors['orange'])

        if current_maze_generation_algorithm != None:
            current_maze_generation_algorithm.draw(colors['red'])

        grid.draw_rect_nodes(colors['blue'], colors['green'], colors['red'], colors['purple'])
        animation_manager.update()
        grid.draw_grid(colors['white'])

        current_pathfinding_algorithm = client.update_current_pathfinding_algorithm(current_pathfinding_algorithm)
        current_maze_generation_algorithm = client.update_current_maze_generation_algorithm(current_maze_generation_algorithm)
        screen_lock = client.update_screen_lock(screen_lock)


        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()