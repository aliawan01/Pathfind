import json
from copy import deepcopy

import pygame
from pygame.locals import *

from grid import *


class ColorNodeTypes(IntEnum):
    BORDER_COLOR = 0,
    BOARD_COLOR = 1,
    MARKED_NODE_COLOR = 2,
    PATH_NODE_FOREGROUND_COLOR = 3,
    PATH_NODE_BACKGROUND_COLOR = 4,
    CHECKED_NODE_FOREGROUND_COLOR = 5,
    CHECKED_NODE_BACKGROUND_COLOR = 6,
    WEIGHTED_NODE_COLOR = 7,
    START_NODE_COLOR = 8,
    END_NODE_COLOR = 9

class ColorUITypes(IntEnum):
    UI_BACKGROUND_COLOR = 10,
    UI_HOVERED_BACKGROUND_COLOR = 11,
    UI_DISABLED_BACKGROUND_COLOR = 12,
    UI_PRESSED_BACKGROUND_COLOR = 13,
    UI_BORDER_COLOR = 14,
    UI_HOVERED_BORDER_COLOR = 15,
    UI_DISABLED_BORDER_COLOR = 16,
    UI_PRESSED_BORDER_COLOR = 17,
    UI_SELECTED_COLOR = 18,
    UI_WINDOW_BACKGROUND_COLOR = 19,
    UI_TEXT_ENTRY_LINE_BORDER_COLOR = 20,
    UI_TEXT_COLOR = 21,
    UI_TEXT_HOVERED_COLOR = 22,
    UI_TEXT_PRESSED_COLOR = 23,
    UI_TEXT_SELECTED_FOREGROUND_COLOR = 24,
    UI_TEXT_SELECTED_BACKGROUND_COLOR = 25,
    UI_TEXT_DISABLED_COLOR = 26,
    UI_TITLE_TEXT_COLOR = 27

class ColorManager:
    def __init__(self, screen_manager, rect_array_obj, animation_manager):
        """
        Initialises the ColorManager class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param animation_manager: AnimationManager
        """
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.animation_manager: AnimationManager = animation_manager
        self.current_theme_name = 'Dark Theme'
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
        """
        This function will return a colour of specified type from
        the theme colours dictionary as a pygame.Color object.

        @param type: Int

        @return: pygame.Color
        """
        return pygame.Color(self.theme_colors[type])

    @property
    def BORDER_COLOR(self):
        """
        Returns the BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.BORDER_COLOR)

    @property
    def BOARD_COLOR(self):
        """
        Returns the BOARD_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.BOARD_COLOR)

    @property
    def MARKED_NODE_COLOR(self):
        """
        Returns the MARKED_NODE_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.MARKED_NODE_COLOR)

    @property
    def WEIGHTED_NODE_COLOR(self):
        """
        Returns the WEIGHTED_NODE_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.WEIGHTED_NODE_COLOR)

    @property
    def PATH_NODE_FOREGROUND_COLOR(self):
        """
        Returns the PATH_NODE_FOREGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.PATH_NODE_FOREGROUND_COLOR)

    @property
    def PATH_NODE_BACKGROUND_COLOR(self):
        """
        Returns the PATH_NODE_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.PATH_NODE_BACKGROUND_COLOR)

    @property
    def CHECKED_NODE_FOREGROUND_COLOR(self):
        """
        Returns the CHECKED_NODE_FOREGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR)

    @property
    def CHECKED_NODE_BACKGROUND_COLOR(self):
        """
        Returns the CHECKED_NODE_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.CHECKED_NODE_BACKGROUND_COLOR)

    @property
    def START_NODE_COLOR(self):
        """
        Returns the START_NODE_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.START_NODE_COLOR)

    @property
    def END_NODE_COLOR(self):
        """
        Returns the END_NODE_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorNodeTypes.END_NODE_COLOR)

    @property
    def UI_BACKGROUND_COLOR(self):
        """
        Returns the UI_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_BACKGROUND_COLOR)

    @property
    def UI_HOVERED_BACKGROUND_COLOR(self):
        """
        Returns the UI_HOVERED_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_HOVERED_BACKGROUND_COLOR)

    @property
    def UI_DISABLED_BACKGROUND_COLOR(self):
        """
        Returns the UI_DISABLED_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_DISABLED_BACKGROUND_COLOR)

    @property
    def UI_PRESSED_BACKGROUND_COLOR(self):
        """
        Returns the UI_PRESSED_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_PRESSED_BACKGROUND_COLOR)

    @property
    def UI_BORDER_COLOR(self):
        """
        Returns the UI_BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_BORDER_COLOR)

    @property
    def UI_HOVERED_BORDER_COLOR(self):
        """
        Returns the UI_HOVERED_BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_HOVERED_BORDER_COLOR)

    @property
    def UI_DISABLED_BORDER_COLOR(self):
        """
        Returns the UI_DISABLED_BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_DISABLED_BORDER_COLOR)

    @property
    def UI_PRESSED_BORDER_COLOR(self):
        """
        Returns the UI_PRESSED_BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_PRESSED_BORDER_COLOR)

    @property
    def UI_SELECTED_COLOR(self):
        """
        Returns the UI_SELECTED_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_SELECTED_COLOR)

    @property
    def UI_WINDOW_BACKGROUND_COLOR(self):
        """
        Returns the UI_WINDOW_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_WINDOW_BACKGROUND_COLOR)

    @property
    def UI_TEXT_ENTRY_LINE_BORDER_COLOR(self):
        """
        Returns the UI_TEXT_ENTRY_LINE_BORDER_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_ENTRY_LINE_BORDER_COLOR)

    @property
    def UI_TEXT_COLOR(self):
        """
        Returns the UI_TEXT_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_COLOR)

    @property
    def UI_TEXT_HOVERED_COLOR(self):
        """
        Returns the UI_TEXT_HOVERED_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_HOVERED_COLOR)

    @property
    def UI_TEXT_PRESSED_COLOR(self):
        """
        Returns the UI_TEXT_PRESSED_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_PRESSED_COLOR)

    @property
    def UI_TEXT_SELECTED_FOREGROUND_COLOR(self):
        """
        Returns the UI_TEXT_SELECTED_FOREGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_SELECTED_FOREGROUND_COLOR)

    @property
    def UI_TEXT_SELECTED_BACKGROUND_COLOR(self):
        """
        Returns the UI_TEXT_SELECTED_BACKGROUND_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_SELECTED_BACKGROUND_COLOR)

    @property
    def UI_TEXT_DISABLED_COLOR(self):
        """
        Returns the UI_TEXT_DISABLED_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TEXT_DISABLED_COLOR)

    @property
    def UI_TITLE_TEXT_COLOR(self):
        """
        Returns the UI_TITLE_TEXT_COLOR from the theme colours dictionary
        as a pygame.Color object using the self.get_theme_color method.

        @return: pygame.Color
        """
        return self.get_theme_color(ColorUITypes.UI_TITLE_TEXT_COLOR)

    def set_dark_theme(self):
        """
        Will set the current theme to be the default 'Dark Theme'
        """
        self.theme_colors = self.get_theme_from_themes_list("Dark Theme")

    def set_and_animate_dark_theme(self, current_pathfinding_algorithm):
        """
        Will set the current theme to be the default 'Dark Theme' and also
        animate the theme using the set_and_animate_theme_colors_dict method.

        @param current_pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        """
        self.set_and_animate_theme_colors_dict(self.get_theme_from_themes_list("Dark Theme"), current_pathfinding_algorithm)

    def set_light_theme(self):
        """
        Will set the current theme to be the default 'Light Theme'
        """
        self.theme_colors = self.get_theme_from_themes_list("Light Theme")

    def set_and_animate_light_theme(self, current_pathfinding_algorithm):
        """
        Will set the current theme to be the default 'Light Theme' and also
        animate the theme using the set_and_animate_theme_colors_dict method.

        @param current_pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        """
        self.set_and_animate_theme_colors_dict(self.get_theme_from_themes_list("Light Theme"), current_pathfinding_algorithm)

    def extract_rgb_color_from_pygame_color(self, color):
        """
        Will take in a pygame.Color instance and extract the rgb values of the
        pygame.Color instance into a tuple and it will then return the tuple.

        @param color: pygame.Color

        @return: Tuple
        """
        return (color[0], color[1], color[2])

    def set_node_color(self, node_type, color):
        """
        Will set the specified node type (either from ColorNodeTypes
        or ColorUITypes) with the specified color in the theme colors dictionary.

        @param node_type: Int
        @param color: pygame.Color
        """
        self.theme_colors[node_type] = self.extract_rgb_color_from_pygame_color(color)

    def set_theme_colors_dict(self, new_theme_colors_dict):
        """
        Will replace the contents of the theme colors dictionary
        with the dictionary provided.

        @param new_theme_colors_dict: Dict
        """
        self.theme_colors = new_theme_colors_dict.copy()

    def get_theme_colors_dict(self):
        """
        Will return the theme colors dictionary

        @return: Dict
        """
        return self.theme_colors

    def set_and_animate_theme_colors_dict(self, new_theme_colors_dict, current_pathfinding_algorithm=None):
        """
        Will replace the theme colours dictionary with the dictionary provided and any colours which are different
        from the original theme colours dictionary will be animated (this will be done by using the set_and_animate_node_color
        method from the instance of the AnimationManager class).

        @param new_theme_colors_dict: Dict
        @param current_pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        """
        new_theme_colors_dict_copy = new_theme_colors_dict.copy()
        changed_color_node_types = []

        for color_node_type, color in new_theme_colors_dict_copy.items():
            if self.theme_colors[color_node_type] != color:
                changed_color_node_types.append(color_node_type)

        for changed_color_node in changed_color_node_types:
            self.set_and_animate_node_color(changed_color_node, new_theme_colors_dict_copy[changed_color_node], current_pathfinding_algorithm)


    def set_and_animate_node_color(self, node_type, color, current_pathfinding_algorithm=None):
        """
        This function will set the specified node type in the theme colors dictionary with the specified colour if it
        is different from the colour the node type already has. Additionally, if the colour is different then it will be
        animated based upon what node type it has been set to:

        If the node type is either ColorNodeTypes.BOARD_COLOR or ColorNodeTypes.BORDER_COLOR then the interpolate_board_or_border method
        from the instance of the Animation Manager will be used. If it is any other value in ColorNodeTypes then the
        add_coords_to_animation_dict method from the instance of the AnimationManager will be used. If the node type is in ColorUITypes
        then the add_ui_element_to_ui_element_interpolation_dict method from the instance of the AnimationManager will be used.


        @param node_type: Int
        @param color: pygame.Color
        @param current_pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        """
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

                case ColorUITypes.UI_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_BACKGROUND_COLOR, self.UI_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_HOVERED_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_HOVERED_BACKGROUND_COLOR, self.UI_HOVERED_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_DISABLED_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_DISABLED_BACKGROUND_COLOR, self.UI_DISABLED_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_PRESSED_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_PRESSED_BACKGROUND_COLOR, self.UI_PRESSED_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_BORDER_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_BORDER_COLOR, self.UI_BORDER_COLOR, color)

                case ColorUITypes.UI_HOVERED_BORDER_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_HOVERED_BORDER_COLOR, self.UI_HOVERED_BORDER_COLOR, color)

                case ColorUITypes.UI_DISABLED_BORDER_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_DISABLED_BORDER_COLOR, self.UI_DISABLED_BORDER_COLOR, color)

                case ColorUITypes.UI_PRESSED_BORDER_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_PRESSED_BORDER_COLOR, self.UI_PRESSED_BORDER_COLOR, color)

                case ColorUITypes.UI_SELECTED_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_SELECTED_COLOR, self.UI_SELECTED_COLOR, color)

                case ColorUITypes.UI_WINDOW_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_WINDOW_BACKGROUND_COLOR, self.UI_WINDOW_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_TEXT_ENTRY_LINE_BORDER_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_ENTRY_LINE_BORDER_COLOR, self.UI_TEXT_ENTRY_LINE_BORDER_COLOR, color)

                case ColorUITypes.UI_TEXT_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_COLOR, self.UI_TEXT_COLOR, color)

                case ColorUITypes.UI_TEXT_HOVERED_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_HOVERED_COLOR, self.UI_TEXT_HOVERED_COLOR, color)

                case ColorUITypes.UI_TEXT_PRESSED_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_PRESSED_COLOR, self.UI_TEXT_PRESSED_COLOR, color)

                case ColorUITypes.UI_TEXT_SELECTED_FOREGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_SELECTED_FOREGROUND_COLOR, self.UI_TEXT_SELECTED_FOREGROUND_COLOR, color)

                case ColorUITypes.UI_TEXT_SELECTED_BACKGROUND_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_SELECTED_BACKGROUND_COLOR, self.UI_TEXT_SELECTED_BACKGROUND_COLOR, color)

                case ColorUITypes.UI_TEXT_DISABLED_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TEXT_DISABLED_COLOR, self.UI_TEXT_DISABLED_COLOR, color)

                case ColorUITypes.UI_TITLE_TEXT_COLOR:
                    self.animation_manager.add_ui_element_to_ui_element_interpolation_dict(ColorUITypes.UI_TITLE_TEXT_COLOR, self.UI_TITLE_TEXT_COLOR, color)

            self.theme_colors[node_type] = color

    def load_themes_into_themes_list(self):
        """
        This function will read all the json data containing information about themes
        in the data/themes/themes.json file and then load it into the self.themes_list dictionary.
        """
        with open('data/themes/themes.json', 'r') as file:
            self.themes_list = json.loads(file.read())
            for theme_dict in self.themes_list:
                old_colors_dict = theme_dict['colors']

                new_colors_dict = {}
                for i in range(len(ColorNodeTypes) + len(ColorUITypes)):
                    new_colors_dict[i] = old_colors_dict[str(i)]

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
        """
        This function will json.dumps method to save all of the information in the self.themes_list
        into the data/themes.themes.json file.
        """
        with open('data/themes/themes.json', 'w') as file:
            file.write(json.dumps(self.themes_list))

    def save_theme_to_themes_list(self, name, colors_dict):
        """
        This function will add a new theme to the self.themes_list dictionary, and it will
        save all of these changes to the data/themes/themes.json file using the save_themes_list method.

        @param name: Str
        @param colors_dict: Dict
        """
        for theme in self.themes_list:
            if theme['name'] == name:
                theme['colors'] = colors_dict
                break
        else:
            self.themes_list.append({"name": name, "custom_theme": True, "colors": colors_dict})

        self.save_themes_list()

    def delete_custom_theme_from_themes_list(self, name):
        """
        This function will delete a custom theme from self.themes_list dictionary if the custom theme exists.
        It will also save any changes done the self.themes_list dictionary to the data/themes/themes.json file
        using the save_themes_list method.

        @param name: Str
        """
        removal_index = None
        for i in range(len(self.themes_list)):
            if self.themes_list[i]['name'] == name and self.themes_list[i]['custom_theme']:
                removal_index = i
                break

        if removal_index != None:
            self.themes_list.pop(removal_index)
            self.save_themes_list()

    def do_custom_themes_exists(self):
        """
        This function will search the self.themes_list dictionary for any custom themes,
        if a custom theme exists it will return True or else it will return False.

        @return: Bool
        """
        for theme in self.themes_list:
            if theme['custom_theme']:
                return True

        return False

    def check_custom_theme_exists(self, name):
        """
        This function will search the self.themes_list dictionary to see if a custom theme
        with the specified name exists if it does the function will return True or else the function
        will return False.

        @param name: Str

        @return: Bool
        """
        for theme in self.themes_list:
            if theme['name'] == name and theme['custom_theme']:
                return True

        return False

    def get_theme_from_themes_list(self, name):
        """
        This function will return the theme dictionary of the theme with the specified name
        from the self.themes_list dictionary if it exists (otherwise it will return None).

        @param name: Str

        @return: Dict or None
        """
        for theme in self.themes_list:
            if theme['name'] == name:
                return deepcopy(theme['colors'])
        else:
            return None

    def get_all_theme_names_from_themes_list(self):
        """
        This will go through all the themes in the self.themes_list dictionary and append
        their names to a list and then return that list.

        @return: List
        """
        theme_names = []
        for theme in self.themes_list:
            theme_names.append(theme['name'])

        return theme_names

    def get_all_custom_theme_names_from_themes_list(self):
        """
        This function will go through the self.themes_list dictionary search for any custom themes
        and append the names of the custom themes to a list and then return that list.

        @return: List
        """
        custom_theme_names = []
        for theme in self.themes_list:
            if theme['custom_theme']:
                custom_theme_names.append(theme['name'])

        return custom_theme_names
