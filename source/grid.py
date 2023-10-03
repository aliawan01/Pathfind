import pygame
from pygame.locals import *
import time
from enum import IntEnum

from animations import *

class ScreenManager(object):
    def __init__(self, screen, screen_width, screen_height, grid_width, grid_height, resolution_divider):
        """
        Initialises the ScreenManager class.

        @param screen: pygame.Surface
        @param screen_width: int
        @param screen_height: int
        @param grid_width: int
        @param grid_height: int
        @param resolution_divider: int
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.resolution_divider = resolution_divider

    @property
    def num_of_rows(self):
        """
        Calculates the number of rows that should be in the grid.

        @return: int
        """
        return self.grid_height//100*self.resolution_divider

    @property
    def num_of_columns(self):
        """
        Calculates the number of columns that should be in the grid.

        @return: int
        """
        return self.grid_width//100*self.resolution_divider

    @property
    def row_width(self):
        """
        Calculates the exact width of each row in the grid.

        @return: float
        """
        return self.grid_height/self.num_of_rows

    @property
    def column_width(self):
        """
        Calculates the exact width of each column in the grid.

        @return: float
        """
        return self.grid_width/self.num_of_columns

    @property
    def row_width_int(self):
        """
        Calculates the width of each row in the grid to the nearest integer.

        @return: int
        """
        return self.grid_height//self.num_of_rows

    @property
    def column_width_int(self):
        """
        Calculates the width of each column in the grid to the nearest integer.

        @return: int
        """
        return self.grid_width//self.num_of_columns

    @property
    def grid_height_offset(self):
        """
        Calculates the difference between the height of the screen and the height of the grid.

        @return: int
        """
        return self.screen_height - self.grid_height

    def set_resolution_divider(self, resolution_divider):
        """
        Setter to set the value of the self.resolution_divider attribute.

        @param resolution_divider: int
        """
        self.resolution_divider = resolution_divider

    def increment_resolution_divider(self):
        """
        This function will increment the value of self.resolution_divider as long as
        the value of self.resolution_divider is less than 8.
        """
        if self.resolution_divider < 8:
            self.resolution_divider += 1

    def decrement_resolution_divider(self):
        """
        This function will decrement the value of self.resolution_divider as long as
        the value of self.resolution_divider is greater than 1.
        """
        if self.resolution_divider > 1:
            self.resolution_divider -= 1


class RectNode:
    def __init__(self, rect, coords):
        """
        Initialises the RectNode class.

        @param rect: pygame.Rect
        @param coords: List
        @param is_start_node: bool
        @param is_end_node: bool
        @param is_user_weight: bool
        @param weight: int
        @param marked: bool
        @param adjacent_nodes: List
        """
        self.rect = rect
        self.coords = coords
        self.is_start_node = False
        self.is_end_node = False
        self.is_user_weight = False
        self.weight = 1
        self.marked = False
        self.adjacent_nodes = [None, None, None, None]

class RectArray:
    def __init__(self, screen_manager):
        """
        Initialises the RectArray class.

        @param screen_manager: ScreenManager
        """
        self.screen_manager = screen_manager
        self.array = []
        self.gen_rect_array()

    def gen_rect_array(self):
        """
        This function will make self.array into 2D array which represents the game's grid.
        Each row in self.array will contain multiple RectNode instances (each row should have
        enough RectNode instances to match the number of columns in the grid) which will
        represent each cell on the grid. The top left most node should be set as the start node
        and the bottom right most node should be set as the end node.
        """

        column_width = self.screen_manager.column_width
        row_width = self.screen_manager.row_width

        if self.screen_manager.resolution_divider > 4:
            column_width += 1
            row_width += 1

        self.array = []

        pos_x = 0
        pos_y = self.screen_manager.grid_height_offset

        for y in range(self.screen_manager.num_of_rows):
            self.array.append([])
            for x in range(self.screen_manager.num_of_columns):
                square_pygame_rect = pygame.Rect(pos_x, pos_y, column_width, row_width)
                self.array[-1].append(RectNode(square_pygame_rect, [y, x]))
                pos_x += self.screen_manager.column_width
            else:
                pos_x = 0
                pos_y += self.screen_manager.row_width

        self.array[0][0].is_start_node = True
        self.array[0][0].weight = 0
        self.array[-1][-1].is_end_node = True

    def gen_rect_array_with_adjacent_nodes(self):
        """
        This function will go through each RectNode in self.array and calculate
        the coordinates of its adjacent nodes (i.e. if any node exists above,
        below, to the right or to the left of the current node and that node is
        not marked, then that node will be considered an adjacent node to our current
        node). It will then fill in the adjacent_nodes attribute of the RectNode with the
        coordinates of its adjacent nodes if they exist.
        """
        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                # Right
                if x+1 < self.screen_manager.num_of_columns:
                    if self.array[y][x+1].marked == False:
                        self.array[y][x].adjacent_nodes[0] = [y, x+1]
                # Up
                if y-1 > -1:
                    if self.array[y-1][x].marked == False:
                        self.array[y][x].adjacent_nodes[1] = [y-1, x]
                # Left
                if x-1 > -1:
                    if self.array[y][x-1].marked == False:
                        self.array[y][x].adjacent_nodes[2] = [y, x-1]
                # Down
                if y+1 < self.screen_manager.num_of_rows:
                    if self.array[y+1][x].marked == False:
                        self.array[y][x].adjacent_nodes[3] = [y+1, x]

    def reset_rect_array_adjacent_nodes(self):
        """
        This function will go through each RectNode in self.array
        and set the adjacent_nodes attribute of each RectNode to
        the list [None, None, None, None].
        """
        for row in self.array:
            for node in row:
                node.adjacent_nodes = [None, None, None, None]

    def get_valid_adjacent_nodes(self, coords):
        """
        This function will find the RectNode at the coordinates given in self.array,
        and then go through the adjacent_nodes attribute of the RectNode and return
        a new array only containing the coordinates of the adjacent nodes (this list
        will not contain any 'None' values which may exist in the adjacent_nodes attribute).

        @param coords: List
        @return: List
        """
        node = self.array[coords[0]][coords[1]]
        valid_adjacent_nodes = [i for i in node.adjacent_nodes if i != None] 
        return valid_adjacent_nodes

    def reset_rect_array(self):
        """
        This function will call the gen_rect_array() method.
        """
        self.gen_rect_array()
        
    def get_start_and_end_node_coords(self):
        """
        This function will go through self.array and find the coordinates
        of the start the end nodes and then return those coordinates.

        @return: Tuple
        """
        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                if self.array[y][x].is_start_node:
                    start_node_coords = [y, x]
                elif self.array[y][x].is_end_node:
                    end_node_coords = [y, x]

        return start_node_coords, end_node_coords

    def reset_non_user_weights(self):
        """
        This function will go through each RectNode in the grid and will
        set the weight attribute of the RectNode to 1 if the is_user_weight attribute
        is set to False.
        """
        for row in self.array:
            for node in row:
                if node.is_user_weight == False:
                    node.weight = 1

        start_node_coords, end_node_coords = self.get_start_and_end_node_coords()
        self.array[start_node_coords[0]][start_node_coords[1]].weight = 0

    def get_weight_at_node(self, coord):
        """
        This function will return the value of the weight attribute of the RectNode
        at the given coordinates from self.array.

        @param coord: List
        @return: int
        """
        return self.array[coord[0]][coord[1]].weight

    def set_weight_at_node(self, coord, weight):
        """
        This function will get the RectNode at the coordinates given from self.array
        and set the weight attribute of the RectNode to the weight given if the
        is_user_weight attribute is set to False.

        @param coord: List
        @param weight: bool
        """
        if self.array[coord[0]][coord[1]].is_user_weight == False:
            self.array[coord[0]][coord[1]].weight = weight


class CursorNodeTypes(IntEnum):
    MARKED_NODE = 0,
    WEIGHTED_NODE = 1

class Grid:
    def __init__(self, screen_manager, rect_array_obj,  color_manager, animation_manager):
        """
        Initializes the Grid class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        self.screen_manager = screen_manager
        self.color_manager = color_manager
        self.rect_array_obj = rect_array_obj
        self.animation_manager = animation_manager
        self.line_width = 1

    def draw_grid(self):
        """
        This function will draw the lines for the grid onto the screen.

        The number of columns and rows on the grid should be the same as
        the values of the num_of_columns and num_of_rows attributes in self.screen_manager.

        The width between each column and row should also be the same as the values
        of the column_width and row_width attributes in self.screen_manager.
        """
        pos_x = self.screen_manager.column_width
        pos_y = self.screen_manager.grid_height_offset

        for x in range(self.screen_manager.num_of_columns):
            pygame.draw.line(self.screen_manager.screen, self.color_manager.BORDER_COLOR, (pos_x, self.screen_manager.grid_height_offset), (pos_x, self.screen_manager.screen_height), width=self.line_width)
            pos_x += self.screen_manager.column_width

        for x in range(self.screen_manager.num_of_rows):
            pygame.draw.line(self.screen_manager.screen, self.color_manager.BORDER_COLOR, (0, pos_y), (self.screen_manager.grid_width, pos_y), width=self.line_width)
            pos_y += self.screen_manager.row_width

    def draw_rect_nodes(self):
        """
        This function will draw the different types of nodes onto the screen.
        It will do this by going through each RectNode in self.rect_array_obj.array
        and depending upon which attributes are set to True in the RectNode they will
        be drawn with their relevant colours onto the screen (you will be able to get
        these colours using self.color_manager).

        The priority of these attributes are as follows:
        1) is_start_node
        2) is_end_node
        3) marked
        4) is_user_weight

        I have highlighted this order of properties because a RectNode may have more than
        one of these attributes set to True at the same time (for example a RectNode might have
        the is_start_node attribute and the marked attribute both set to True, in this case
        the node should be drawn as the start node because that is the attribute with the higher
        priority). If this is the case then the node will be drawn as the attribute it has set to
        True with the highest priority.
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.is_start_node:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.START_NODE_COLOR, node.rect)
                elif node.is_end_node:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.END_NODE_COLOR, node.rect)
                elif node.marked:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.MARKED_NODE_COLOR, node.rect)
                elif node.is_user_weight:
                    pygame.draw.rect(self.screen_manager.screen, self.color_manager.WEIGHTED_NODE_COLOR, node.rect)

    def mark_node(self, node_type, node, weight):
        """
        Depending upon the node_type given the RectNode given will be marked as either
        a marked node or a weighted node.

        If node_type is CursorNodeTypes.MARKED_NODE then the RectNode will have it's 'marked'
        attribute set to True and it will be animated using the add_coords_to_animation_dict
        method in self.animation_manager.

        If node_type is CursorNodeTypes.WEIGHTED_NODE then the RectNode will have it's 'is_user_weight'
        attribute set to True and the 'weight' attribute will be set the to weight we have been given.
        This node will also be animated using the add_coords_to_animation_dict method in self.animation_manager.

        @param node_type: CursorNodeTypes
        @param node: RectNode
        @param weight: int
        """
        if node_type == CursorNodeTypes.MARKED_NODE:
            if node.marked == False and node.is_user_weight == False:
                node.marked = True
                self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)

            elif node.marked == False and node.is_user_weight:
                node.marked = True
                node.is_user_weight = False
                self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, self.color_manager.WEIGHTED_NODE_COLOR, 2)

        elif node_type == CursorNodeTypes.WEIGHTED_NODE:
            if node.is_user_weight == False and node.marked == False:
                self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)
                node.is_user_weight = True
                node.weight = weight

    def unmark_node(self, node):
        """
        If the RectNode given has the 'is_user_weight' attribute set to True then the
        'is_user_weight' attribute will be set to False and the 'weight' attribute will be
        set to 1, the node will then be animated using the add_coords_to_animation_dict method
        in self.animation_manager.

        However, if the RectNode given has the 'marked' attribute set to True then the
        'marked' attribute will be set to False and the node will also be animated using
        the add_coords_to_animation_dict method in self.animation_manager.

        @param node: RectNode
        """
        if node.is_user_weight:
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)
            node.is_user_weight = False
            node.weight = 1
        elif node.marked:
            node.marked = False
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)

    def mark_node_at_mouse_pos(self, mouse_coords, node_type, weight):
        """
        This function will find the RectNode in self.rect_array_obj.array
        whose rect collides with the mouse coordinates given, it will then
        pass this RectNode along with the node_type and weight given into
        the mark_node method.

        @param mouse_coords: Tuple
        @param node_type: CursorNodeTypes
        @param weight: int
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_node(node_type, node, weight)
                    break

    def unmark_node_at_mouse_pos(self, mouse_coords):
        """
        This function will find the RectNode in self.rect_array_obj.array
        whose rect collides with the mouse coordinates given, it will then
        pass this RectNode into the unmark_node method.

        @param mouse_coords: Tuple
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.unmark_node(node)
                    break

    def mark_start_node(self, node):
        """
        This function will find the current RectNode which has the 'is_start_node' attribute
        set to True in self.rect_array_obj.array and it will set it to False. It will then
        set the 'is_start_node' attribute of the RectNode passed into the function to True, and
        then animate both the old and new start nodes using the add_coords_to_animation_dict in
        self.animation_manager.

        @param node: RectNode
        """
        original_start_node = None

        for row in self.rect_array_obj.array:
            for new_node in row:
                if new_node.is_start_node:
                    original_start_node = new_node

        if not node.is_start_node and not node.is_end_node:
            node.is_start_node = True
            original_start_node.is_start_node = False

            self.animation_manager.add_coords_to_animation_dict(original_start_node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.START_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.START_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)

    def mark_start_node_at_mouse_pos(self, mouse_coords):
        """
        This function will find the RectNode in self.rect_array_obj.array
        whose rect collides with the mouse coordinates given, it will then
        pass this RectNode into the mark_start_node method.

        @param mouse_coords: Tuple
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_start_node(node)
                    break

    def mark_end_node(self, node):
        """
        This function will find the current RectNode which has the 'is_end_node' attribute
        set to True in self.rect_array_obj.array and it will set it to False. It will then
        set the 'is_end_node' attribute of the RectNode passed into the function to True, and
        then animate both the old and new end nodes using the add_coords_to_animation_dict in
        self.animation_manager.

        @param node: RectNode
        """
        original_end_node = None

        for row in self.rect_array_obj.array:
            for new_node in row:
                if new_node.is_end_node:
                    original_end_node = new_node

        if not node.is_end_node and not node.is_start_node:
            node.is_end_node = True
            original_end_node.is_end_node = False

            self.animation_manager.add_coords_to_animation_dict(original_end_node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.END_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)
            self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.EXPANDING_SQUARE, self.color_manager.END_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND, 2)


    def mark_end_node_at_mouse_pos(self, mouse_coords):
        """
        This function will find the RectNode in self.rect_array_obj.array
        whose rect collides with the mouse coordinates given, it will then
        pass this RectNode into the mark_end_node method.

        @param mouse_coords: Tuple
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.rect.collidepoint(mouse_coords):
                    self.mark_end_node(node)
                    break

    def reset_marked_nodes(self, animate=True):
        """
        This function will go through each RectNode in self.rect_array_obj.array
        and check if the 'marked' attribute is set to True. If the attribute is set
        to True then it will be set to False and the node will be animated using the
        add_coords_to_animation_dict in self.animation_manager if the animate variable
        given is set to True.

        @param animate: bool
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.marked:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)
                    node.marked = False

    def reset_all_weights(self, animate=True):
        """
        This function will go through each RectNode in self.rect_array_obj.array
        and check if the 'is_user_weight' attribute is set to True. If the 'is_user_weight'
        attribute is set to True then it will be set to False and the 'weight' attribute will
        be set to 1. The node will then be animated using the add_coords_to_animation_dict in
        self.animation_manager if the animate variable given is set to True.

        @param animate: Bool
        """
        for row in self.rect_array_obj.array:
            for node in row:
                if node.is_user_weight:
                    if animate:
                        self.animation_manager.add_coords_to_animation_dict(node.coords, AnimationTypes.SHRINKING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)
                    node.is_user_weight = False
                    node.weight = 1

        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        self.rect_array_obj.array[start_node_coords[0]][start_node_coords[1]].weight = 0

    def get_board_info(self):
        """
        This function will go through each RectNode in self.rect_array_obj.array and get information
        about the start node's coordinates, the end node's coordinates, a list containing the coordinates
        of all the nodes with the 'marked' attribute set to True and a list containing the coordinates of
        all the nodes with the 'is_user_weight' attribute set to True. All this information will be added
        to a list along with the value of the resolution_divider attribute in self.screen_manager. The
        function will then return this list.

        @return: List
        """
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        marked_coords = []
        weighted_coords = []

        for row in self.rect_array_obj.array:
            for node in row:
                if node.marked:
                    marked_coords.append(node.coords)
                elif node.is_user_weight:
                    weighted_coords.append([node.coords, node.weight])

        return [start_node_coords, end_node_coords, marked_coords, weighted_coords, self.screen_manager.resolution_divider]