import pygame
import sys

from grid import RectArray, Grid
from stack import Stack

from sorting_algorithms import *

colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'orange': (255, 165, 0),
    'neon_blue': (4, 217, 255),
    'yellow': (255, 255, 0),
    'purple': (238, 130, 238)
}

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 800
    screen_height = 600
    num_of_rows = screen_height//100*4
    num_of_columns = screen_width//100*4

    print("Number of columns:", num_of_columns)
    print("Number of rows: ", num_of_rows)

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfinding Visualizer")

    rect_array = RectArray(screen_width, screen_height, num_of_rows, num_of_columns)
    grid = Grid(screen, rect_array, screen_width, screen_height, num_of_rows, num_of_columns)

    dfs = DFS(screen, rect_array, num_of_rows, num_of_columns)
    bfs = BFS(screen, rect_array, num_of_rows, num_of_columns)
    dijkastra = Dijkastra(screen, rect_array, num_of_rows, num_of_columns)
    astar = AStar(screen, rect_array, num_of_rows, num_of_columns)
    greedy_bfs = GreedyBFS(screen, rect_array, num_of_rows, num_of_columns)
    bidirectional_bfs = BidirectionalBFS(screen, rect_array, num_of_rows, num_of_columns)

    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_algorithm = None

    DRAW_CHECKED_NODES = pygame.USEREVENT + 0
    DRAW_PATH = pygame.USEREVENT + 1

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
                    rect_array.reset_all_weights()

                    if current_algorithm != None:
                        current_algorithm.reset_checked_nodes_pointer()
                        current_algorithm.reset_path_pointer()

                if event.key == pygame.K_s:
                    grid.mark_weighted_node(pygame.mouse.get_pos(), 10)

                if event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_s:
                    grid.unmark_weighted_node(pygame.mouse.get_pos())

                if event.key == pygame.K_d:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    dfs.run_dfs()
                    current_algorithm = dfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_b:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    bfs.run_bfs()
                    current_algorithm = bfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_j:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    dijkastra.run_dijkastra()
                    current_algorithm = dijkastra
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_a:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    astar.run_astar()
                    current_algorithm = astar
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_g:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    greedy_bfs.run_greedy_bfs()
                    current_algorithm = greedy_bfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_w:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()
                    rect_array.reset_non_user_weights()

                    bidirectional_bfs.run_bidirectional_bfs()
                    current_algorithm = bidirectional_bfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)


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
                flag = current_algorithm.update_checked_nodes_pointer()
                if flag == -1:
                    pygame.time.set_timer(DRAW_CHECKED_NODES, 0)
                    pygame.time.set_timer(DRAW_PATH, 10)

            if event.type == DRAW_PATH:
                flag = current_algorithm.update_path_pointer()
                if flag == -1:
                    pygame.time.set_timer(DRAW_PATH, 0)
                    screen_lock = False


        if mark_spray:
            grid.mark_rect_node(pygame.mouse.get_pos())
        elif unmark_spray:
            grid.unmark_rect_node(pygame.mouse.get_pos())

        screen.fill(colors['black'])
        if current_algorithm != None:
            current_algorithm.draw(colors['neon_blue'], colors['orange'])

        grid.draw_rect_nodes(current_algorithm, colors['blue'], colors['green'], colors['red'], colors['purple'])
        grid.draw_grid(colors['white'])

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
