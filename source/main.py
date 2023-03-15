import pygame
from pygame.locals import *
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
    'yellow': (255, 255, 0) 
}

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 800
    screen_height = 600
    num_of_rows = screen_height//100*4
    num_of_columns = screen_width//100*4

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pathfinding Visualizer")

    grid = Grid(screen, screen_width, screen_height, num_of_rows, num_of_columns)
    rect_array = RectArray(screen_width, screen_height, num_of_rows, num_of_columns)

    dfs = DFS(screen, num_of_rows, num_of_columns)
    bfs = BFS(screen, num_of_rows, num_of_columns)


    screen_lock = False

    mark_spray = False
    unmark_spray = False

    current_algorithm = None

    DRAW_CHECKED_NODES = pygame.USEREVENT + 0
    DRAW_PATH = pygame.USEREVENT + 1

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_c:
                    if screen_lock == False:
                        grid.reset_marked_nodes(rect_array.array)
                        if current_algorithm != None:
                            current_algorithm.reset_checked_nodes_pointer()
                            current_algorithm.reset_path_pointer()

                if event.key == pygame.K_d:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()

                    dfs.run_dfs(rect_array)
                    current_algorithm = dfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

                if event.key == pygame.K_b:
                    rect_array.reset_rect_array_adjacent_nodes()
                    rect_array.gen_rect_array_with_adjacent_nodes()

                    bfs.run_bfs(rect_array)
                    current_algorithm = bfs
                    screen_lock = True

                    pygame.time.set_timer(DRAW_CHECKED_NODES, 25)

            if screen_lock == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mark_spray = True

                    elif event.button == 2:
                        grid.mark_start_node(rect_array.array, pygame.mouse.get_pos())

                    elif event.button == 3:
                        unmark_spray = True

                if event.type == pygame.MOUSEBUTTONUP:
                    mark_spray = False
                    unmark_spray = False
                    
                if event.type == pygame.MOUSEWHEEL:
                    grid.mark_end_node(rect_array.array, pygame.mouse.get_pos())

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
            grid.mark_rect_node(rect_array.array, pygame.mouse.get_pos())
        elif unmark_spray:
            grid.unmark_rect_node(rect_array.array, pygame.mouse.get_pos())

        screen.fill(colors['black'])
        if current_algorithm != None:
            current_algorithm.draw(rect_array.array, colors['neon_blue'], colors['orange'])

        grid.draw_rect_nodes(current_algorithm, rect_array.array, colors['blue'], colors['green'], colors['red'])
        grid.draw_grid(colors['white'])

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()

