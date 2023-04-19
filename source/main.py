import pygame
import sys

from animations import *

from grid import RectArray, Grid
from stack import Stack

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

def set_current_pathfinding_algorithm(pathfinding_algorithm, rect_array):
    rect_array.reset_rect_array_adjacent_nodes()
    rect_array.gen_rect_array_with_adjacent_nodes()
    rect_array.reset_non_user_weights()

    pathfinding_algorithm.reset_animated_checked_coords_stack()
    pathfinding_algorithm.reset_animated_path_coords_stack()

    pathfinding_algorithm.run()
    return pathfinding_algorithm

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 1000
    screen_height = 800

    resolution_divider = 4
    num_of_rows = screen_height//100*resolution_divider
    num_of_columns = screen_width//100*resolution_divider

    print("Number of columns:", num_of_columns)
    print("Number of rows: ", num_of_rows)

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfinding Visualizer")

    rect_array = RectArray(screen_width, screen_height, num_of_rows, num_of_columns)
    animation_manager = AnimationManager(screen, rect_array, screen_width, screen_height, num_of_rows, num_of_columns, resolution_divider)
    grid = Grid(screen, rect_array, screen_width, screen_height, num_of_rows, num_of_columns, colors, animation_manager)

    dfs = DFS(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    bfs = BFS(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    dijkastra = Dijkastra(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    astar = AStar(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    greedy_bfs = GreedyBFS(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    bidirectional_bfs = BidirectionalBFS(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)

    random_weighted_maze = RandomWeightedMaze(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    random_marked_maze = RandomMarkedMaze(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)
    recursive_division_maze = RecursiveDivisionMaze(screen, rect_array, num_of_rows, num_of_columns, colors, animation_manager)

    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_pathfinding_algorithm = None
    current_maze_generation_algorithm = None

    DRAW_CHECKED_NODES = pygame.USEREVENT + 0
    DRAW_PATH = pygame.USEREVENT + 1
    DRAW_MAZE = pygame.USEREVENT + 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                # TODO(ali): Toggle this if statement to make sure screen_lock works
                #            after you've finished testing the algorithms.
                # if screen_lock == False:
                if event.key == pygame.K_c:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                if event.key == pygame.K_s:
                    grid.mark_weighted_node(pygame.mouse.get_pos(), 10)

                if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_s:
                    grid.unmark_weighted_node(pygame.mouse.get_pos())

                if event.key == pygame.K_d:
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(dfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_b:
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(bfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_j:
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(dijkastra, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_a:
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(astar, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_g:
                    current_pathfinding_algorithm = set_current_pathfinding_algorithm(greedy_bfs, rect_array)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_w:
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

                if event.key == pygame.K_2:
                    grid.reset_marked_nodes(False)
                    grid.reset_all_weights(False)

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    if current_maze_generation_algorithm != None:
                        current_maze_generation_algorithm.reset_maze_pointer()

                    random_marked_maze.create_random_marked_maze()

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

                if event.key == pygame.K_4:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    current_maze_generation_algorithm = recursive_division_maze
                    current_maze_generation_algorithm.reset_animated_coords_stack()
                    current_maze_generation_algorithm.reset_maze_pointer()

                    recursive_division_maze.run_recursive_division(RecursiveDivisionSkew.VERTICAL)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_MAZE, 15)

                if event.key == pygame.K_5:
                    grid.reset_marked_nodes()
                    grid.reset_all_weights()

                    if current_pathfinding_algorithm != None:
                        current_pathfinding_algorithm.reset_checked_nodes_pointer()
                        current_pathfinding_algorithm.reset_path_pointer()

                    current_maze_generation_algorithm = recursive_division_maze
                    current_maze_generation_algorithm.reset_animated_coords_stack()
                    current_maze_generation_algorithm.reset_maze_pointer()

                    recursive_division_maze.run_recursive_division(RecursiveDivisionSkew.HORIZONTAL)
                    screen_lock = True

                    pygame.time.set_timer(DRAW_MAZE, 15)

            if screen_lock == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mark_spray = True

                    elif event.button == 2:
                        grid.mark_start_node(pygame.mouse.get_pos())

                    elif event.button == 3:
                        unmark_spray = True

                if event.type == pygame.MOUSEBUTTONUP:
                    mark_spray = False
                    unmark_spray = False
                    
                if event.type == pygame.MOUSEWHEEL:
                    grid.mark_end_node(pygame.mouse.get_pos())

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
            grid.mark_rect_node(pygame.mouse.get_pos())
        elif unmark_spray:
            grid.unmark_rect_node(pygame.mouse.get_pos())

        screen.fill(colors['black'])
        if current_pathfinding_algorithm != None:
            current_pathfinding_algorithm.draw(colors['neon_blue'], colors['orange'])

        if current_maze_generation_algorithm != None:
            current_maze_generation_algorithm.draw(colors['red'])

        grid.draw_rect_nodes(current_pathfinding_algorithm, colors['blue'], colors['green'], colors['red'], colors['purple'])
        animation_manager.update()
        grid.draw_grid(colors['white'])

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
