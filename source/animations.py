import pygame
from pygame.locals import *

from enum import Enum, IntEnum

from stack import Stack
from queue_classes import Queue, PriorityQueue

class AnimationTypes(Enum):
    EXPANDING_SQUARE = 0
    SHRINKING_SQUARE = 1
    CIRCLE_TO_SQUARE = 2
    LINEAR_COLOR_INTERPOLATION = 3
    BOARD_LINEAR_INTERPOLATION = 4
    BORDER_LINEAR_INTERPOLATION = 5

class AnimationBackgroundTypes(Enum):
    THEME_BACKGROUND = 0

class AnimationNode:
    def __init__(self, coords, animation_type, foreground_color, background_color, speed, column_width, row_width, row_width_int, grid_height_offset):
        self.type = animation_type
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.speed = speed
        self.center = ((row_width*coords[1])+(row_width//2), (row_width*coords[0])+(row_width//2)+grid_height_offset)
        self.fraction = 0
        self.increment = row_width_int//2
        self.finished = False
        self.width = 0
        self.rect = pygame.Rect(0, 0, column_width, row_width)

class UIAnimationNode:
    def __init__(self, initial_colour, final_colour):
        self.initial_colour = initial_colour
        self.final_colour = final_colour
        self.fraction = 0

class AnimationManager:
    def __init__(self, screen_manager, rect_array_obj):
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.start_node_coords, self.end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        self.animation_dict = {}
        self.board_and_border_interpolation_dict = {AnimationTypes.BOARD_LINEAR_INTERPOLATION: None, AnimationTypes.BORDER_LINEAR_INTERPOLATION: None}
        self.ui_element_interpolation_dict = {}

    def add_coords_to_animation_dict(self, coords, animation_type, foreground_color, background_color, speed=1):
        if tuple(coords) in self.animation_dict.keys():
            if self.animation_dict[tuple(coords)].type == animation_type:
                return

        self.animation_dict[tuple(coords)] = AnimationNode(coords, animation_type, foreground_color, background_color, speed, self.screen_manager.column_width, self.screen_manager.row_width, self.screen_manager.row_width_int, self.screen_manager.grid_height_offset)

    def interpolate_board_or_border(self, interpolation_type, initial_color, final_color, speed=1):
        if self.board_and_border_interpolation_dict[interpolation_type] == None:
            self.board_and_border_interpolation_dict[interpolation_type] = [initial_color, final_color, 0]

    def update_border_and_board_interpolation(self):
        events_to_remove = []
        background_color = None
        border_color = None

        for event, info in self.board_and_border_interpolation_dict.items():
            if info != None:
                fraction = info[2]
                fraction = round(fraction + (self.screen_manager.resolution_divider / 100), 2)

                initial_color = info[0]
                final_color = info[1]

                if fraction > 1:
                    events_to_remove.append(event)
                else:
                    self.board_and_border_interpolation_dict[event][2] = fraction
                    lerp_color = pygame.Color.lerp(initial_color, final_color, fraction)
                    if event == AnimationTypes.BOARD_LINEAR_INTERPOLATION:
                        self.screen_manager.screen.fill(lerp_color)
                        background_color = lerp_color
                    else:
                        border_color = lerp_color

            for event_to_remove in events_to_remove:
                self.board_and_border_interpolation_dict[event_to_remove] = None

        return {'BACKGROUND_COLOR': background_color, 'BORDER_COLOR': border_color}

    def update_coords_animations(self, background_color):
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        coords_to_remove = []

        for coords, node in list(self.animation_dict.items()):
            if list(coords) == start_node_coords or list(coords) == end_node_coords:
                continue

            if node.finished:
                coords_to_remove.append(coords)
                continue

            node.rect.center = node.center

            node.fraction = round(node.fraction+(self.screen_manager.resolution_divider/100), 2)
            if node.fraction > 1:
                node.fraction = 1

            if node.background_color == AnimationBackgroundTypes.THEME_BACKGROUND:
                node_background_color = background_color
            else:
                node_background_color = node.background_color

            if node.type == AnimationTypes.CIRCLE_TO_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node_background_color, node.rect)

                lerp_color = pygame.Color.lerp(node.foreground_color[0], node.foreground_color[1], node.fraction)

                if node.width <= self.screen_manager.row_width//2:
                    pygame.draw.circle(self.screen_manager.screen, lerp_color, node.center, node.width)
                    node.width += 1*node.speed
                else:
                    if node.increment <= 0:
                        node.finished = True
                    else:
                        node.increment -= 1*node.speed
                    
                    pygame.draw.rect(self.screen_manager.screen, lerp_color, node.rect, 0, node.increment)

            elif node.type == AnimationTypes.EXPANDING_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node_background_color, node.rect)
                if node.width <= self.screen_manager.row_width:
                    new_rect = pygame.Rect(0, 0, node.width, node.width)
                    new_rect.center = node.center
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, new_rect)

                    node.width += 1*node.speed
                else:
                    node.finished = True
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, node.rect)

            elif node.type == AnimationTypes.SHRINKING_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node_background_color, node.rect)
                if node.rect.width - node.width > 0:
                    new_rect = pygame.Rect(0, 0, node.rect.width-node.width, node.rect.height-node.width)
                    new_rect.center = node.center
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, new_rect)

                    node.width += 1*node.speed
                else:
                    node.finished = True

            elif node.type == AnimationTypes.LINEAR_COLOR_INTERPOLATION:
                lerp_color = pygame.Color.lerp(node.foreground_color[0], node.foreground_color[1], node.fraction)

                pygame.draw.rect(self.screen_manager.screen, lerp_color, node.rect)

                if node.fraction >= 1:
                    node.finished = True


        for removing_coord in coords_to_remove:
            self.animation_dict.pop(removing_coord)

    def add_ui_element_to_ui_element_interpolation_dict(self, ui_element_type, initial_colour, final_colour):
        if ui_element_type not in self.ui_element_interpolation_dict.keys():
            self.ui_element_interpolation_dict[ui_element_type] = UIAnimationNode(initial_colour, final_colour)

    def update_ui_element_interpolation_dict(self):
        ui_elements_to_remove = []
        ui_colors_to_return = []

        for ui_element_type, node in self.ui_element_interpolation_dict.items():
            node.fraction = round(node.fraction + (self.screen_manager.resolution_divider/100), 2)

            if node.fraction > 1:
                ui_elements_to_remove.append(ui_element_type)
            else:
                lerp_colour = node.initial_colour.lerp(node.final_colour, node.fraction)
                ui_colors_to_return.append({ui_element_type: lerp_colour})


        for ui_element in ui_elements_to_remove:
            self.ui_element_interpolation_dict.pop(ui_element)

        return ui_colors_to_return
