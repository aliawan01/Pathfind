import pygame
from pygame.locals import *
import sys

import grid

colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0)
}

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    num_of_squares = 20

    screen = pygame.display.set_mode((screen_width, screen_height))

    rect_array = grid.gen_rect_array(screen_height, screen_width, num_of_squares)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_coords = pygame.mouse.get_pos()
                    grid.mark_rect_node(screen, mouse_coords, rect_array)


        screen.fill(colors['black'])

        grid.draw_rect_nodes(screen, rect_array, colors['red'])
        grid.draw_grid(screen, screen_width, screen_height, num_of_squares, colors['white'])

        pygame.display.flip()


if __name__ == '__main__':
    main()

