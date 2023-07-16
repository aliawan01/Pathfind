import pygame
from pygame.locals import *

from animations import *
from grid import *
from copy import deepcopy

from enum import IntEnum
import json

class ColorNodeTypes(IntEnum):
    BORDER_COLOR = 0,
    BOARD_COLOR = 1,
    MARKED_NODE_COLOR = 2,
    PATH_NODE_FOREGROUND_COLOR = 3,
    PATH_NODE_BACKGROUND_COLOR = 4,
    CHECKED_NODE_FOREGROUND_COLOR = 5,
    CHECKED_NODE_BACKGROUND_COLOR = 6,
    # TODO(ali): May need to remove this once they are turned into images.
    WEIGHTED_NODE_COLOR = 7,
    START_NODE_COLOR = 8,
    END_NODE_COLOR = 9


class ColorManager:
    def __init__(self, screen_manager, rect_array_obj, animation_manager):
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.animation_manager = animation_manager
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'orange': (255, 165, 0),
            'neon_blue': (4, 217, 255),
            'yellow': (255, 255, 0),
            'purple': (238, 130, 238),
            'violet': (200, 116, 252),
            'crimson': (148, 31, 54),
            'light_green': (62, 222, 134),
            'bright_yellow': (255, 252, 0)
        }

        self.themes_list = []
        self.theme_colors = {}
        self.load_themes_into_themes_list()
        self.set_dark_theme()

    def get_theme_color(self, type):
        return pygame.Color(self.theme_colors[type])

    @property
    def BORDER_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.BORDER_COLOR)

    @property
    def BOARD_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.BOARD_COLOR)

    @property
    def MARKED_NODE_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.MARKED_NODE_COLOR)

    @property
    def WEIGHTED_NODE_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.WEIGHTED_NODE_COLOR)

    @property
    def PATH_NODE_FOREGROUND_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.PATH_NODE_FOREGROUND_COLOR)

    @property
    def PATH_NODE_BACKGROUND_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.PATH_NODE_BACKGROUND_COLOR)

    @property
    def CHECKED_NODE_FOREGROUND_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR)

    @property
    def CHECKED_NODE_BACKGROUND_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.CHECKED_NODE_BACKGROUND_COLOR)

    @property
    def START_NODE_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.START_NODE_COLOR)

    @property
    def END_NODE_COLOR(self):
        return self.get_theme_color(ColorNodeTypes.END_NODE_COLOR)

    def set_dark_theme(self):
        self.theme_colors = self.get_theme_from_themes_list("Dark Theme")

    def set_and_animate_dark_theme(self, current_pathfinding_algorithm):
        self.set_and_animate_theme_colors_dict(self.get_theme_from_themes_list("Dark Theme"), current_pathfinding_algorithm)

    def set_light_theme(self):
        self.theme_colors = self.get_theme_from_themes_list("Light Theme")

    def set_and_animate_light_theme(self, current_pathfinding_algorithm):
        self.set_and_animate_theme_colors_dict(self.get_theme_from_themes_list("Light Theme"), current_pathfinding_algorithm)

    def extract_rgb_color_from_pygame_color(self, color):
        return (color[0], color[1], color[2])

    def set_node_color(self, node_type, color):
        self.theme_colors[node_type] = self.extract_rgb_color_from_pygame_color(color)

    def set_theme_colors_dict(self, new_theme_colors_dict):
        self.theme_colors = new_theme_colors_dict.copy()

    def get_theme_colors_dict(self):
        return self.theme_colors

    def set_and_animate_theme_colors_dict(self, new_theme_colors_dict, current_pathfinding_algorithm=None):
        new_theme_colors_dict_copy = new_theme_colors_dict.copy()
        changed_color_node_types = []

        for color_node_type, color in new_theme_colors_dict_copy.items():
            if self.theme_colors[color_node_type] != color:
                changed_color_node_types.append(color_node_type)

        for changed_color_node in changed_color_node_types:
            self.set_and_animate_node_color(changed_color_node, new_theme_colors_dict_copy[changed_color_node], current_pathfinding_algorithm)


    def set_and_animate_node_color(self, node_type, color, current_pathfinding_algorithm=None):
        if self.theme_colors[node_type] != color:
            match node_type:
                case ColorNodeTypes.MARKED_NODE_COLOR:
                    for row in self.rect_array_obj.array:
                        for node in row:
                            if node.marked:
                                self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.MARKED_NODE_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

                case ColorNodeTypes.BOARD_COLOR:
                    self.animation_manager.interpolate_board_or_border(AnimationTypes.BOARD_LINEAR_INTERPOLATION, self.BOARD_COLOR, pygame.Color(color))

                case ColorNodeTypes.BORDER_COLOR:
                    self.animation_manager.interpolate_board_or_border(AnimationTypes.BORDER_LINEAR_INTERPOLATION, self.BORDER_COLOR, pygame.Color(color))

                case ColorNodeTypes.WEIGHTED_NODE_COLOR:
                    for row in self.rect_array_obj.array:
                        for node in row:
                            if node.is_user_weight:
                                self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.WEIGHTED_NODE_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

                case ColorNodeTypes.PATH_NODE_FOREGROUND_COLOR:
                    if current_pathfinding_algorithm != None:
                        for path_coord in current_pathfinding_algorithm.path:
                            self.animation_manager.add_coords_to_animation_dict(path_coord, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.PATH_NODE_FOREGROUND_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

                case ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR:
                    if current_pathfinding_algorithm != None:
                        for checked_coord in current_pathfinding_algorithm.checked_nodes:
                            if checked_coord not in current_pathfinding_algorithm.path.stack:
                                self.animation_manager.add_coords_to_animation_dict(checked_coord, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.CHECKED_NODE_FOREGROUND_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

                case ColorNodeTypes.START_NODE_COLOR:
                    start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
                    self.animation_manager.add_coords_to_animation_dict(start_node_coords, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.START_NODE_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

                case ColorNodeTypes.END_NODE_COLOR:
                    start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
                    self.animation_manager.add_coords_to_animation_dict(end_node_coords, AnimationTypes.LINEAR_COLOR_INTERPOLATION, (self.END_NODE_COLOR, pygame.Color(color)), self.theme_colors[ColorNodeTypes.BOARD_COLOR])

            self.theme_colors[node_type] = color

    def load_themes_into_themes_list(self):
        with open('data/themes/themes.json', 'r') as file:
            self.themes_list = json.loads(file.read())
            for theme_dict in self.themes_list:
                old_colors_dict = theme_dict['colors']
                new_colors_dict = {
                    0: old_colors_dict["0"],
                    1: old_colors_dict["1"],
                    2: old_colors_dict["2"],
                    3: old_colors_dict["3"],
                    4: old_colors_dict["4"],
                    5: old_colors_dict["5"],
                    6: old_colors_dict["6"],
                    7: old_colors_dict["7"],
                    8: old_colors_dict["8"],
                    9: old_colors_dict["9"]
                }

                for color_node_type, color in new_colors_dict.items():
                    if type(color) == list:
                        new_colors_dict[color_node_type] = tuple(color)
                    else:
                        if color in self.colors.keys():
                            new_colors_dict[color_node_type] = self.colors[color]
                        else:
                            new_colors_dict[color_node_type] = self.colors["bright_yellow"]

                theme_dict['colors'] = new_colors_dict

    def save_themes_list(self):
        with open('data/themes/themes.json', 'w') as file:
            file.write(json.dumps(self.themes_list))

    def save_theme_to_themes_list(self, name, colors_dict):
        for theme in self.themes_list:
            if theme['name'] == name:
                theme['colors'] = colors_dict
                break
        else:
            self.themes_list.append({"name": name, "custom_theme": True, "colors": colors_dict})

        self.save_themes_list()

    def delete_custom_theme_from_themes_list(self, name):
        removal_index = None
        for i in range(len(self.themes_list)):
            if self.themes_list[i]['name'] == name and self.themes_list[i]['custom_theme']:
                removal_index = i
                break

        if removal_index != None:
            self.themes_list.pop(removal_index)
            self.save_themes_list()

    def do_custom_themes_exists(self):
        for theme in self.themes_list:
            if theme['custom_theme']:
                return True

        return False

    def check_custom_theme_exists(self, name):
        for theme in self.themes_list:
            if theme['name'] == name and theme['custom_theme']:
                return True

        return False

    def get_theme_from_themes_list(self, name):
        for theme in self.themes_list:
            if theme['name'] == name:
                return deepcopy(theme['colors'])
        else:
            return None

    def get_all_theme_names_from_themes_list(self):
        theme_names = []
        for theme in self.themes_list:
            theme_names.append(theme['name'])

        return theme_names
