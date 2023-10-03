import pygame
from pygame.locals import *

import pygame_gui
import sys
import os
from enum import IntEnum
import random
import ipaddress
import json

from grid import *
from pathfinding_algorithms import *
from color_manager import *
from maze_generation_algorithms import *
from networking import *

class ThemeWindowStages(IntEnum):
    CUSTOM_THEME_CREATION_WELCOME_SCREEN = 0,
    CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN = 1,
    CUSTOM_THEME_CREATION_FINISH_SCREEN = 2,
    CUSTOM_THEME_EDITING_WELCOME_SCREEN = 3,
    CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN = 4,
    CUSTOM_THEME_EDITING_FINISH_SCREEN = 5,
    CUSTOM_THEME_DELETE_SCREEN = 6

class ThemeWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, color_manager, font_manager):
        """
        Initializes the ThemeWindow class.

        @param manager: pygame_gui.ui_manager.UIManager
        @param color_manager: ColorManager
        @param font_manager: FontManager
        """
        self.manager = manager
        self.color_manager = color_manager
        self.font_manager = font_manager
        self.window_width = 710
        self.window_height = 650
        self.window_running = False
        self.stage = None
        self.custom_theme_name = None
        self.inheriting_theme = None
        self.changed_custom_theme_name = False
        self.changed_inheriting_theme = False
        self.color_picker_index = None
        self.custom_theme_to_edit_name = None
        self.custom_theme_editing_dict = None
        self.changed_custom_theme_to_edit_name = False
        self.custom_theme_editing_color_picker_index = None
        self.custom_themes_to_delete_names = []
        self.edited_custom_theme = False
        self.deleted_themes = False

        self.node_type_and_name_dict = {
            ColorNodeTypes.BORDER_COLOR: 'Border',
            ColorNodeTypes.BOARD_COLOR: 'Board',
            ColorNodeTypes.MARKED_NODE_COLOR: 'Marked Node',
            ColorNodeTypes.PATH_NODE_FOREGROUND_COLOR: 'Path Foreground',
            ColorNodeTypes.PATH_NODE_BACKGROUND_COLOR: 'Path Background',
            ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR: 'Checked Foreground',
            ColorNodeTypes.CHECKED_NODE_BACKGROUND_COLOR: 'Checked Background',
            ColorNodeTypes.WEIGHTED_NODE_COLOR: 'Weighted Node',
            ColorNodeTypes.START_NODE_COLOR: 'Start Node',
            ColorNodeTypes.END_NODE_COLOR: 'End Node',
            ColorUITypes.UI_BACKGROUND_COLOR: 'UI Background',
            ColorUITypes.UI_HOVERED_BACKGROUND_COLOR: 'UI Hovered Background',
            ColorUITypes.UI_DISABLED_BACKGROUND_COLOR: 'UI Disabled Background',
            ColorUITypes.UI_PRESSED_BACKGROUND_COLOR: 'UI Pressed Background',
            ColorUITypes.UI_BORDER_COLOR: 'UI Border',
            ColorUITypes.UI_HOVERED_BORDER_COLOR: 'UI Hovered Border',
            ColorUITypes.UI_DISABLED_BORDER_COLOR: 'UI Disabled Border',
            ColorUITypes.UI_PRESSED_BORDER_COLOR: 'UI Pressed Border',
            ColorUITypes.UI_SELECTED_COLOR: 'UI Selected',
            ColorUITypes.UI_WINDOW_BACKGROUND_COLOR: 'UI Window Background',
            ColorUITypes.UI_TEXT_ENTRY_LINE_BORDER_COLOR: 'UI Text Entry Line Border',
            ColorUITypes.UI_TEXT_COLOR: 'UI Text',
            ColorUITypes.UI_TEXT_HOVERED_COLOR: 'UI Hovered Text',
            ColorUITypes.UI_TEXT_PRESSED_COLOR: 'UI Pressed Text',
            ColorUITypes.UI_TEXT_SELECTED_FOREGROUND_COLOR: 'UI Selected Text Foreground',
            ColorUITypes.UI_TEXT_SELECTED_BACKGROUND_COLOR: 'UI Selected Text Background',
            ColorUITypes.UI_TEXT_DISABLED_COLOR: 'UI Disabled Text',
            ColorUITypes.UI_TITLE_TEXT_COLOR: 'UI Title Text'
        }

        self.custom_theme_dict = {}
        for color_node_type in ColorNodeTypes:
            self.custom_theme_dict[color_node_type] = None

        for color_ui_type in ColorUITypes:
            self.custom_theme_dict[color_ui_type] = None


    def build_custom_theme_creation_welcome_screen(self):
        """
        It will first create a window and then create the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN

        if self.window_running == False:
            print("[THEME WINDOW] Set self.window_running to True")
            self.changed_custom_theme_name = False
            self.changed_inheriting_theme = False
            self.custom_theme_name = None
            self.inheriting_theme = None

            self.window_running = True
            super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                             window_display_title='Custom Theme Creation',
                             manager=self.manager)
            self.set_blocking(True)

            self.previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (50, 30)),
                                                                     text='<-',
                                                                     container=self,
                                                                     manager=self.manager)

            self.next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.window_width - 90, 5), (50, 30)),
                                                                 text='->',
                                                                 container=self,
                                                                 manager=self.manager)


        self.previous_page_button.disable()
        self.next_page_button.disable()

        self.welcome_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                              html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Custom Theme Creation Menu</var></font>",
                                                              object_id="#text_box_title",
                                                              container=self,
                                                              manager=self.manager)

        self.custom_theme_name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 80), (220, 80)),
                                                                   text='Custom Theme Name',
                                                                   container=self,
                                                                   manager=self.manager)

        self.custom_theme_name_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((230, 140), (200, 50)),
                                                                                     container=self,
                                                                                     manager=self.manager)

        self.custom_theme_inheriting_theme_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 250), (220, 80)),
                                                                               text='Inherit from Theme',
                                                                               container=self,
                                                                               manager=self.manager)

        custom_themes_names = self.color_manager.get_all_theme_names_from_themes_list()
        custom_themes_names.append('None')
        self.custom_theme_inheriting_theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 310), (200, 50)),
                                                                                     options_list=custom_themes_names,
                                                                                     starting_option='None',
                                                                                     container=self,
                                                                                     manager=self.manager)
    def clean_custom_theme_creation_welcome_screen(self):
        """
        Removes the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN.
        """
        self.stage = None
        self.welcome_text_box.kill()
        self.custom_theme_name_label.kill()
        self.custom_theme_name_text_entry_line.kill()
        self.custom_theme_inheriting_theme_label.kill()
        self.custom_theme_inheriting_theme_menu.kill()


    def build_custom_theme_creation_selection_screen(self):
        """
        Creates the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN
        self.previous_page_button.enable()
        self.next_page_button.enable()

        self.color_selection_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                      html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Color Selection</var></font>",
                                                                      object_id="#text_box_title",
                                                                      container=self,
                                                                      manager=self.manager)

        if self.changed_custom_theme_name or self.changed_inheriting_theme:
            self.changed_custom_theme_name = False
            self.changed_inheriting_theme = False
            self.color_surface_list = [pygame.Surface((100, 100)) for x in range(len(self.node_type_and_name_dict))]
            if self.inheriting_theme == None:
                for i in range(len(self.color_surface_list)):
                    self.color_surface_list[i].fill((0, 0, 0))
                    self.custom_theme_dict[list(self.custom_theme_dict)[i]] = (0, 0, 0)
            else:
                theme_colors = self.color_manager.get_theme_from_themes_list(self.inheriting_theme)
                self.custom_theme_dict = theme_colors.copy()

                for i in range(len(self.color_surface_list)):
                    self.color_surface_list[i].fill(theme_colors[list(self.node_type_and_name_dict)[i]])

        switch = False
        width = 40
        height = 20

        self.ui_images = []
        self.ui_text_boxes = []
        self.ui_buttons = []

        self.scrolling_container = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect((5, 60), (self.window_width-50, self.window_height-150)),
                                                                            container=self,
                                                                            manager=self.manager)

        self.scrolling_container.set_scrollable_area_dimensions((self.window_width-70, 1500))

        for i in range(len(self.color_surface_list)):
            surface = self.color_surface_list[i]

            self.ui_images.append(pygame_gui.elements.UIImage(relative_rect=pygame.Rect((width, height), (50, 50)),
                                                              image_surface=surface,
                                                              container=self.scrolling_container,
                                                              manager=self.manager))

            self.ui_text_boxes.append(pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((width + 60, height), (210, 30)),
                                                                    html_text=self.node_type_and_name_dict[list(self.node_type_and_name_dict)[i]],
                                                                    object_id='#text_box_edit_color',
                                                                    container=self.scrolling_container,
                                                                    manager=self.manager))

            self.ui_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width + 60, height + 30), (130, 30)),
                                                                text='Edit Color',
                                                                container=self.scrolling_container,
                                                                manager=self.manager))
            if width == 40:
                width = 360
                switch = True
            else:
                width = 40
                if switch:
                    height += 95
                    switch = False


    def clean_custom_theme_creation_selection_screen(self):
        """
        Removes the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN.
        """
        self.stage = None
        self.color_selection_text_box.kill()
        self.scrolling_container.kill()

        for image in self.ui_images:
            image.kill()

        for text_box in self.ui_text_boxes:
            text_box.kill()

        for button in self.ui_buttons:
            button.kill()

        self.ui_images = []
        self.ui_text_boxes = []
        self.ui_buttons = []

    def build_custom_theme_creation_finish_screen(self):
        """
        Creates the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_FINISH_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_CREATION_FINISH_SCREEN
        self.next_page_button.disable()
        self.finish_screen_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                    html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Create Theme</var></font>",
                                                                    object_id="#text_box_title",
                                                                    container=self,
                                                                    manager=self.manager)

        self.finish_button_info = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((140, 100), (400, 200)),
                                                                html_text=(f"Pressing the <b>Finish Button</b> will create "
                                                                           f"the New Custom Theme: <b>{self.custom_theme_name}</b> "
                                                                           f"and it will be set as the Current Theme."),
                                                                object_id="#text_box_info",
                                                                container=self,
                                                                manager=self.manager)

        self.finish_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((240, 500), (200, 50)),
                                                          text='Finish',
                                                          container=self,
                                                          manager=self.manager)

    def clean_custom_theme_creation_finish_screen(self):
        """
        Removes the widgets for ThemeWindowStages.CUSTOM_THEME_CREATION_FINISH_SCREEN.
        """
        self.stage = None
        self.finish_screen_text_box.kill()
        self.finish_button_info.kill()
        self.finish_button.kill()

    def build_custom_theme_editing_welcome_screen(self):
        """
        Creates widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_WELCOME_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_EDITING_WELCOME_SCREEN
        self.edited_custom_theme = False

        if self.window_running == False:
            self.window_running = True
            super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                             window_display_title='Edit Custom Themes',
                             manager=self.manager)

            self.set_blocking(True)

            self.custom_theme_editing_previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (50, 30)),
                                                                     text='<-',
                                                                     container=self,
                                                                     manager=self.manager)

            self.custom_theme_editing_next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.window_width - 90, 5), (50, 30)),
                                                                 text='->',
                                                                 container=self,
                                                                 manager=self.manager)

        self.custom_theme_editing_next_page_button.enable()
        self.custom_theme_editing_previous_page_button.disable()

        self.custom_theme_editing_welcome_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                                   html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Custom Theme Editing Menu</var></font>",
                                                                                   object_id="#text_box_title",
                                                                                   container=self,
                                                                                   manager=self.manager)

        self.custom_theme_editing_selection_list_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((190, 70), (300, 100)),
                                                                                          html_text=('Press the theme you want to edit and then'
                                                                                                     ' click on the <b>Next Page</b> button'),
                                                                                          object_id="#text_box_info",
                                                                                          container=self,
                                                                                          manager=self.manager)

        custom_theme_names = self.color_manager.get_all_custom_theme_names_from_themes_list()
        print("[THEME WINDOW] Custom theme names:", custom_theme_names)
        if self.custom_theme_to_edit_name == None:
            self.custom_theme_to_edit_name = custom_theme_names[0]
            self.changed_custom_theme_to_edit_name = True

        self.custom_theme_editing_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((210, 180), ((250, 250))),
                                                                                       item_list=custom_theme_names,
                                                                                       default_selection=self.custom_theme_to_edit_name,
                                                                                       container=self,
                                                                                       manager=self.manager)

    def clean_custom_theme_editing_welcome_screen(self):
        """
        Removes widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_WELCOME_SCREEN.
        """
        self.stage = None
        self.custom_theme_editing_welcome_text_box.kill()
        self.custom_theme_editing_selection_list_text_box.kill()
        self.custom_theme_editing_selection_list.kill()

    def build_custom_theme_editing_color_selection_screen(self):
        """
        Creates widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN
        self.custom_theme_editing_previous_page_button.enable()
        self.custom_theme_editing_next_page_button.enable()
        self.custom_theme_editing_color_selection_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                                           html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Edit Color Selection</var></font>",
                                                                                           object_id="#text_box_title",
                                                                                           container=self,
                                                                                           manager=self.manager)

        if self.changed_custom_theme_to_edit_name:
            self.changed_custom_theme_to_edit_name = False
            self.custom_theme_editing_dict = self.color_manager.get_theme_from_themes_list(self.custom_theme_to_edit_name)

            self.custom_theme_editing_color_surface_list = [pygame.Surface((100, 100)) for x in range(len(self.node_type_and_name_dict))]

            for i in range(len(self.custom_theme_editing_color_surface_list)):
                self.custom_theme_editing_color_surface_list[i].fill(self.custom_theme_editing_dict[list(self.node_type_and_name_dict)[i]])

        switch = False
        width = 40
        height = 20

        self.custom_theme_editing_ui_images = []
        self.custom_theme_editing_ui_text_boxes = []
        self.custom_theme_editing_ui_buttons = []

        self.custom_theme_scrolling_container = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect((5, 60), (self.window_width-50, self.window_height-150)),
                                                                                         container=self,
                                                                                         manager=self.manager)

        self.custom_theme_scrolling_container.set_scrollable_area_dimensions((self.window_width-70, 1500))

        for i in range(len(self.custom_theme_editing_color_surface_list)):
            surface = self.custom_theme_editing_color_surface_list[i]

            self.custom_theme_editing_ui_images.append(pygame_gui.elements.UIImage(relative_rect=pygame.Rect((width, height), (50, 50)),
                                                                                   image_surface=surface,
                                                                                   container=self.custom_theme_scrolling_container,
                                                                                   manager=self.manager))

            self.custom_theme_editing_ui_text_boxes.append(pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((width + 60, height), (210, 30)),
                                                                                         html_text=self.node_type_and_name_dict[list(self.node_type_and_name_dict)[i]],
                                                                                         object_id='#text_box_edit_color',
                                                                                         container=self.custom_theme_scrolling_container,
                                                                                         manager=self.manager))

            self.custom_theme_editing_ui_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width + 60, height + 30), (130, 30)),
                                                                                     text='Edit Color',
                                                                                     container=self.custom_theme_scrolling_container,
                                                                                     manager=self.manager))
            if width == 40:
                width = 360
                switch = True
            else:
                width = 40
                if switch:
                    height += 95
                    switch = False



    def clean_custom_theme_editing_color_selection_screen(self):
        """
        Removes widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN.
        """
        self.stage = None
        self.custom_theme_editing_color_selection_text_box.kill()
        self.custom_theme_scrolling_container.kill()

        for image in self.custom_theme_editing_ui_images:
            image.kill()

        for text_box in self.custom_theme_editing_ui_text_boxes:
            text_box.kill()

        for button in self.custom_theme_editing_ui_buttons:
            button.kill()

        self.custom_theme_editing_ui_images = []
        self.custom_theme_editing_ui_text_boxes = []
        self.custom_theme_editing_ui_buttons = []

    def build_custom_theme_editing_finish_screen(self):
        """
        Creates widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_FINISH_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_EDITING_FINISH_SCREEN
        print("Reached the theme editing finish screen")

        self.custom_theme_editing_next_page_button.disable()
        self.custom_theme_editing_finish_screen_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                                         html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Finish Editing Custom Theme</var></font>",
                                                                                         object_id="#text_box_title",
                                                                                         container=self,
                                                                                         manager=self.manager)

        self.custom_theme_editing_save_changes_button_info = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((130, 100), (400, 200)),
                                                                                     html_text=(f"Pressing the <b>Save Changes</b> button will save the changes"
                                                                                                f" you made to the Custom Theme: <b>{self.custom_theme_to_edit_name}</b>"
                                                                                                f" and it will be set as the Current Theme."),
                                                                                     object_id="#text_box_info",
                                                                                     container=self,
                                                                                     manager=self.manager)

        self.custom_theme_editing_save_changes_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((240, 500), (200, 50)),
                                                                                     text='Save Changes',
                                                                                     container=self,
                                                                                     manager=self.manager)

    def clean_custom_theme_editing_finish_screen(self):
        """
        Removes widgets for ThemeWindowStages.CUSTOM_THEME_EDITING_FINISH_SCREEN.
        """
        self.stage = None
        self.custom_theme_editing_finish_screen_text_box.kill()
        self.custom_theme_editing_save_changes_button_info.kill()
        self.custom_theme_editing_save_changes_button.kill()

    def build_custom_theme_delete_screen(self):
        """
        Creates widgets for ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN.
        """
        self.stage = ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN
        self.custom_themes_to_delete_names = []
        self.deleted_themes = False

        self.window_running = True
        super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                         window_display_title='Delete Custom Theme',
                         manager=self.manager)

        self.set_blocking(True)

        self.custom_theme_deletion_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 5), (self.window_width-50, 40)),
                                                                                  html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Custom Theme Deletion</var></font>",
                                                                                  object_id="#text_box_title",
                                                                                  container=self,
                                                                                  manager=self.manager)

        self.custom_theme_deletion_info_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 60), (self.window_width-50, 100)),
                                                                                 html_text= ("Select the Custom Theme you want to delete from the menu below"
                                                                                             " and press the <b>Delete Themes</b> button to delete the theme."),
                                                                                 object_id="#text_box_info",
                                                                                 container=self,
                                                                                 manager=self.manager)

        custom_theme_names = self.color_manager.get_all_custom_theme_names_from_themes_list()
        print("[THEME WINDOW] Custom theme names:", custom_theme_names)

        self.custom_themes_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((210, 150), ((250, 250))),
                                                                                item_list=custom_theme_names,
                                                                                allow_multi_select=True,
                                                                                container=self,
                                                                                manager=self.manager)

        self.custom_theme_delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((237, 420), (200, 50)),
                                                                       text='Delete Themes',
                                                                       container=self,
                                                                       manager=self.manager)


    def clean_custom_theme_delete_screen(self):
        """
        Removes widgets for ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN.
        """
        self.stage = None
        self.window_running = False
        self.custom_theme_deletion_title_text_box.kill()
        self.custom_theme_deletion_info_text_box.kill()
        self.custom_themes_selection_list.kill()
        self.custom_theme_delete_button.kill()


    def handle_theme_window_ui_text_entry_finished_event(self, event):
        """
        Handles the pygame_gui.UI_TEXT_ENTRY_FINISHED event for the ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running:
            match self.stage:
                case ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN:
                    if event.ui_element == self.custom_theme_name_text_entry_line:
                        if event.text in self.color_manager.get_all_theme_names_from_themes_list():
                            self.custom_theme_name_text_entry_line.set_text('A custom theme already exists with this name.')
                        else:
                            self.custom_theme_name = event.text
                            self.changed_custom_theme_name = True
                            self.next_page_button.enable()

    def handle_theme_window_ui_drop_down_menu_changed_event(self, event):
        """
        Handles the pygame_gui.UI_DROP_DOWN_MENU_CHANGED event for ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running:
            match self.stage:
                case ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN:
                    if event.ui_element == self.custom_theme_inheriting_theme_menu:
                        self.changed_inheriting_theme = True
                        if event.text == 'None':
                            self.inheriting_theme = None
                        else:
                            self.inheriting_theme = event.text


    def handle_theme_window_ui_button_pressed_event(self, event):
        """
        Handles the pygame_gui.UI_BUTTON_PRESSED event for ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running:
            match self.stage:
                case ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN:
                    if event.ui_element == self.next_page_button:
                        self.clean_custom_theme_creation_welcome_screen()
                        self.build_custom_theme_creation_selection_screen()
                        print("[THEME WINDOW] Custom Theme name:", self.custom_theme_name + ", Inheriting Theme:", self.inheriting_theme)

                case ThemeWindowStages.CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN:
                    if event.ui_element == self.previous_page_button:
                        self.clean_custom_theme_creation_selection_screen()
                        self.build_custom_theme_creation_welcome_screen()
                        self.next_page_button.enable()
                        self.custom_theme_name_text_entry_line.set_text(self.custom_theme_name)
                        self.custom_theme_inheriting_theme_menu.kill()
                        custom_themes_names = self.color_manager.get_all_theme_names_from_themes_list()
                        custom_themes_names.append('None')
                        if self.inheriting_theme == None:
                            current_inheriting_theme_name = 'None'
                        else:
                            current_inheriting_theme_name = self.inheriting_theme

                        self.custom_theme_inheriting_theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 310), (200, 50)),
                                                                                                     options_list=custom_themes_names,
                                                                                                     starting_option=current_inheriting_theme_name,
                                                                                                     container=self,
                                                                                                     manager=self.manager)
                    elif event.ui_element == self.next_page_button:
                        self.clean_custom_theme_creation_selection_screen()
                        self.build_custom_theme_creation_finish_screen()

                    else:
                        for i, button in enumerate(self.ui_buttons):
                            if event.ui_element == button:
                                print(self.node_type_and_name_dict[i])
                                self.color_picker_index = i

                                color = self.custom_theme_dict[list(self.custom_theme_dict)[i]]
                                if color == None:
                                    color = self.color_manager.get_theme_color(list(self.node_type_and_name_dict)[i])
                                else:
                                    color = pygame.Color(color)

                                self.color_picker = pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect((100, 100), (400, 400)),
                                                                                            window_title=self.node_type_and_name_dict[i]+' Color',
                                                                                            initial_colour=color,
                                                                                            manager=self.manager)
                case ThemeWindowStages.CUSTOM_THEME_CREATION_FINISH_SCREEN:
                    if event.ui_element == self.previous_page_button:
                        self.clean_custom_theme_creation_finish_screen()
                        self.build_custom_theme_creation_selection_screen()

                    if event.ui_element == self.finish_button:
                        self.clean_custom_theme_creation_finish_screen()
                        self.previous_page_button.kill()
                        self.next_page_button.kill()
                        self.color_manager.set_and_animate_theme_colors_dict(self.custom_theme_dict)
                        self.color_manager.save_theme_to_themes_list(self.custom_theme_name, self.custom_theme_dict)
                        self.window_running = False
                        self.kill()

                case ThemeWindowStages.CUSTOM_THEME_EDITING_WELCOME_SCREEN:
                    if event.ui_element == self.custom_theme_editing_next_page_button:
                        self.clean_custom_theme_editing_welcome_screen()
                        self.build_custom_theme_editing_color_selection_screen()


                case ThemeWindowStages.CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN:
                    if event.ui_element == self.custom_theme_editing_previous_page_button:
                        self.clean_custom_theme_editing_color_selection_screen()
                        self.build_custom_theme_editing_welcome_screen()

                    elif event.ui_element == self.custom_theme_editing_next_page_button:
                        self.clean_custom_theme_editing_color_selection_screen()
                        self.build_custom_theme_editing_finish_screen()

                    else:
                        for i, button in enumerate(self.custom_theme_editing_ui_buttons):
                            if event.ui_element == button:
                                print(self.node_type_and_name_dict[i])
                                self.custom_theme_editing_color_picker_index = i

                                color = self.custom_theme_editing_dict[list(self.custom_theme_editing_dict)[i]]
                                if color == None:
                                    color = self.color_manager.get_theme_color(list(self.node_type_and_name_dict)[i])
                                else:
                                    color = pygame.Color(color)

                                self.custom_theme_editing_color_picker = pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect((100, 100), (400, 400)),
                                                                                                                 window_title=self.node_type_and_name_dict[i]+' Color',
                                                                                                                 initial_colour=color,
                                                                                                                 manager=self.manager)
                case ThemeWindowStages.CUSTOM_THEME_EDITING_FINISH_SCREEN:
                    if event.ui_element == self.custom_theme_editing_previous_page_button:
                        self.clean_custom_theme_editing_finish_screen()
                        self.build_custom_theme_editing_color_selection_screen()

                    if event.ui_element == self.custom_theme_editing_save_changes_button:
                        self.clean_custom_theme_editing_finish_screen()
                        self.custom_theme_editing_next_page_button.kill()
                        self.custom_theme_editing_previous_page_button.kill()
                        self.color_manager.set_and_animate_theme_colors_dict(self.custom_theme_editing_dict)
                        self.color_manager.save_theme_to_themes_list(self.custom_theme_to_edit_name, self.custom_theme_editing_dict)
                        self.changed_custom_theme_to_edit_name = False
                        self.edited_custom_theme = True
                        self.window_running = False
                        self.kill()


                case ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN:
                    if event.ui_element == self.custom_theme_delete_button:
                        if len(self.custom_themes_to_delete_names) > 0:
                            self.color_manager.set_and_animate_dark_theme(None)

                            self.deleted_themes = True
                            for custom_theme_name in self.custom_themes_to_delete_names:
                                self.color_manager.delete_custom_theme_from_themes_list(custom_theme_name)

                        self.clean_custom_theme_delete_screen()
                        self.window_running = False
                        self.kill()

    def handle_theme_window_ui_color_picker_color_picked_event(self, event):
        """
        Handles the pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED event for ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == ThemeWindowStages.CUSTOM_THEME_CREATION_COLOR_SELECTION_SCREEN:
                if event.ui_element == self.color_picker:
                    print("[THEME WINDOW] Colour:", event.colour)
                    self.color_surface_list[self.color_picker_index].fill(event.colour)
                    self.custom_theme_dict[list(self.custom_theme_dict)[self.color_picker_index]] = self.color_manager.extract_rgb_color_from_pygame_color(event.colour)
                    self.ui_images[self.color_picker_index].set_image(self.color_surface_list[self.color_picker_index])

            if self.stage == ThemeWindowStages.CUSTOM_THEME_EDITING_COLOR_SELECTION_SCREEN:
                if event.ui_element == self.custom_theme_editing_color_picker:
                    print("[THEME WINDOW] Custom theme editing colour:", event.colour)
                    self.custom_theme_editing_color_surface_list[self.custom_theme_editing_color_picker_index].fill(event.colour)
                    self.custom_theme_editing_dict[list(self.custom_theme_editing_dict)[self.custom_theme_editing_color_picker_index]] = self.color_manager.extract_rgb_color_from_pygame_color(event.colour)
                    self.custom_theme_editing_ui_images[self.custom_theme_editing_color_picker_index].set_image(self.custom_theme_editing_color_surface_list[self.custom_theme_editing_color_picker_index])


    def handle_theme_window_ui_selection_list_new_selection(self, event):
        """
        Handles the pygame_gui.UI_SELECTION_LIST_NEW_SELECTION event for ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN:
                if event.ui_element == self.custom_themes_selection_list:
                    self.custom_themes_to_delete_names.append(event.text)
                    print(self.custom_themes_to_delete_names)

            if self.stage == ThemeWindowStages.CUSTOM_THEME_EDITING_WELCOME_SCREEN:
                if event.ui_element == self.custom_theme_editing_selection_list:
                    self.custom_theme_to_edit_name = event.text
                    self.changed_custom_theme_to_edit_name = True
                    print(self.custom_theme_to_edit_name)

    def handle_theme_window_ui_selection_list_dropped_selection(self, event):
        """
        Handles the pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION event for ThemeWindow.

        @param event: pygame.event
        """
        if self.window_running and self.stage == ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN:
            if event.ui_element == self.custom_themes_selection_list:
                self.custom_themes_to_delete_names.remove(event.text)
                print(self.custom_themes_to_delete_names)

    def shutdown(self):
        """
        Sets the window_running attribute to False.
        """
        print("[THEME WINDOW] Shutdown Theme Window")
        self.window_running = False

class UINetworkingManager(pygame_gui.elements.UIWindow):
    def __init__(self, manager, client, server, font_manager):
        """
        Initializes the UINetworkingManager class.

        @param manager: pygame_gui.ui_manager.UIManager
        @param client: Client
        @param server: Server
        @param font_manager: FontManager
        """
        self.manager = manager
        self.client = client
        self.server = server
        self.font_manager = font_manager
        self.window_width = 650
        self.window_height = 600
        self.window_running = False
        self.created_server = False
        self.shutdown_server = False
        self.connected_to_server = False
        self.ip_address = socket.gethostbyname(socket.gethostname())

    def create_server(self):
        """
        Creates a message window telling the user that they have successfully created
        a server running on their local machine. This message window will also tell the
        user information about the server (i.e. the IP Address and Port Number the server
        is running on).
        """
        if self.created_server == False:
            self.created_server = True
            self.shutdown_server = False
            self.connected_to_server = False

            self.port = random.randint(2000, 10000)
            self.server.run_server(self.ip_address, self.port)
            self.client.connect_to_server(self.ip_address, self.port)

            message = (f'We have successfully created a server running on<br><br><b>IP Address: {self.ip_address}<br>Port: {self.port}</b><br>'
                       f'<br>You can now allow your friends to join your game by telling them to click on the <b>Connect to Server</b> option'
                       f' and typing in the IP address and port shown in this window in the relevant fields.')

            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                               window_title='Created Server Message Window',
                                               html_message=message,
                                               manager=self.manager)

    def show_server_info(self):
        """
        Creates a message window which will tell the user the following
        information about the game server running on their local machine.

        - IP Address of the server.
        - Port Number the server is listening on.
        - How many clients are connected to the server.
        """
        message = (f'Your server is running on<br><br><b>IP Address: {self.ip_address}<br>Port: {self.port}<br>' f'Number of currently connected clients: {self.server.get_number_of_currently_connected_clients()}</b>'
                   f'<br><br>You can allow your friends to join your game by telling them to click on the <b>Connect to Server</b>'
                   f' option and typing in the IP address and port shown in this window in the relevant fields.')

        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           window_title='Server Information Window',
                                           html_message=message,
                                           manager=self.manager)

    def destroy_server(self):
        """
        This function is used to shut down a server and will do the following:

        - The shutdown_server attribute is set to True
        - The created_server attribute is set to False
        - The connected_to_server attribute is set to False
        - The shutdown() method is called from self.server
        - A message window is created telling the user that the server
          has been shutdown successfully.
        """
        self.shutdown_server = True
        self.created_server = False
        self.connected_to_server = False
        self.server.shutdown()
        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           window_title='Server Shutdown Window',
                                           html_message="Successfully shutdown the server, all of the clients have been kicked out as well.",
                                           manager=self.manager)

    def check_is_valid_ip_address(self, ip_address):
        """
        This function will take in a string and check if
        it is the valid format to be considered an IP Address.

        @param ip_address: Str
        @return: bool
        """
        try:
            ip_address_obj = ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def check_is_valid_port(self, port_number):
        """
        This function will check if the port_number given
        is in the range 2000 to 9999.

        @param port_number: int
        @return: bool
        """
        if port_number in range(2000, 10000):
            return True
        else:
            return False

    def server_connection_has_broken(self):
        """
        This function will set both the created_server and connected_to_server
        attributes to False. It will then check if the shutdown_server attribute
        is set to True, if it is we will set to it to False, otherwise we will
        create a message window telling the user that the server they were connected
        to has been shut down by the owner.
        """
        self.created_server = False
        self.connected_to_server = False
        if self.shutdown_server:
            self.shutdown_server = False
        else:
            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                               html_message="The server has been shutdown by the owner and you have been kicked out of the server.",
                                               manager=self.manager)


    def build_networking_connect_to_server_screen(self):
        """
        It will first create a window and then create the widgets for the
        screen to connect to server.
        """
        self.window_running = True

        self.created_server = False
        self.connected_to_server = False

        super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                         window_display_title='Connect to Server',
                         manager=self.manager)

        self.set_blocking(True)
        self.networking_connect_to_server_welcome_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 5), (self.window_width - 50, 50)),
                                                                                                 html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Connect To Server Screen</var></font>",
                                                                                                 object_id="#text_box_title",
                                                                                                 container=self,
                                                                                                 manager=self.manager)

        self.networking_connect_to_server_welcome_info_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 55), (self.window_width - 50, 100)),
                                                                                                html_text= ("In order to connect to a server you must type in the"
                                                                                                            " server's IP Address and Port Number in the relevant fields"
                                                                                                            " below. You can then click the <b>Connect</b> button to see if"
                                                                                                            " we can connect to the server with the information you have provided."),
                                                                                                object_id="#text_box_info",
                                                                                                container=self,
                                                                                                manager=self.manager)

        self.networking_connect_to_server_ip_address_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((235, 170), (150, 35)),
                                                                                         text='IP Address',
                                                                                         container=self,
                                                                                         manager=self.manager)

        self.networking_connect_to_server_ip_address_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((205, 205), (200, 50)),
                                                                                                           container=self,
                                                                                                           manager=self.manager)

        self.networking_connect_to_server_port_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((235, 285), (150, 35)),
                                                                                   text='Port Number',
                                                                                   container=self,
                                                                                   manager=self.manager)

        self.networking_connect_to_server_port_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((205, 320), (200, 50)),
                                                                                                     container=self,
                                                                                                     manager=self.manager)

        self.networking_connect_to_server_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((205, 420), (200, 50)),
                                                                                text='Connect',
                                                                                container=self,
                                                                                manager=self.manager)

    def clean_networking_connect_server_screen(self):
        """
        Removes the widgets for the screen to connect to the server.
        """
        self.window_running = False
        self.networking_connect_to_server_welcome_title_text_box.kill()
        self.networking_connect_to_server_welcome_info_text_box.kill()
        self.networking_connect_to_server_ip_address_label.kill()
        self.networking_connect_to_server_ip_address_text_entry_line.kill()
        self.networking_connect_to_server_port_label.kill()
        self.networking_connect_to_server_port_text_entry_line.kill()
        self.networking_connect_to_server_button.kill()

    def disconnect_from_server(self):
        """
        This function will set the created_server and connected_to_server attributes to
        False. It will then create a network event using the create_network_event method
        in self.client with the event NetworkingEventTypes.DISCONNECT_FROM_SERVER. After
        this, the function will create a message window telling the user that they have
        successfully disconnected from the server.
        """
        self.created_server = False
        self.connected_to_server = False

        self.client.create_network_event(NetworkingEventTypes.DISCONNECT_FROM_SERVER)
        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           html_message="Successfully disconnected from server.",
                                           manager=self.manager)

    def handle_ui_networking_manager_ui_button_pressed_event(self, event):
        """
        Handles the pygame_gui.UI_BUTTON_PRESSED event for UINetworkingManager.

        @param event: pygame.event
        """
        if self.window_running:
            if event.ui_element == self.networking_connect_to_server_button:
                exit = False

                server_ip_address = self.networking_connect_to_server_ip_address_text_entry_line.get_text()
                if self.check_is_valid_ip_address(server_ip_address) == False:
                    self.networking_connect_to_server_ip_address_text_entry_line.set_text("Invalid IP Address")
                    exit = True

                try:
                    server_port = int(self.networking_connect_to_server_port_text_entry_line.get_text())
                    if self.check_is_valid_port(server_port) == False:
                        self.networking_connect_to_server_port_text_entry_line.set_text("Port number must be in range 2000-10000")
                        exit = True
                except ValueError:
                    self.networking_connect_to_server_port_text_entry_line.set_text("Port number must be an integer.")
                    exit = True

                if exit:
                    return False

                successfully_connected_to_server = self.client.connect_to_server(server_ip_address, server_port)
                print(self.client.connected_to_server)
                if successfully_connected_to_server == False:
                    message = f'Unable to connect to server with IP Address <b>{server_ip_address}</b> on port <b>{server_port}</b>'
                    self.connected_to_server = False
                    self.created_server = False
                else:
                    message = f'Successfully connected to server with IP Address <b>{server_ip_address}</b> on port <b>{server_port}</b>'
                    self.connected_to_server = True
                    self.created_server = False

                pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)), html_message=message, manager=self.manager)

                self.clean_networking_connect_server_screen()
                self.kill()

                if self.connected_to_server:
                    return True

    def shutdown_networking_window(self):
        """
        Sets the window_running attribute to False
        """
        print("[NETWORKING WINDOW] Shutdown Networking Window")
        self.window_running = False

class TutorialWindowStages(IntEnum):
    TUTORIAL_WELCOME_SCREEN = 0,
    TUTORIAL_PROJECT_DESCRIPTION = 1,
    TUTORIAL_PATHFINDING_ALGORITHM = 2,
    TUTORIAL_PATHFINDING_ALGORITHM_INFO = 3,
    TUTORIAL_MAZE_GENERATION_ALGORITHM = 4,
    TUTORIAL_MAZE_GENERATION_ALGORITHM_INFO = 5,
    TUTORIAL_SETTINGS = 6,
    TUTORIAL_FONTS = 7,
    TUTORIAL_MARKED_AND_WEIGHTED_NODES = 8,
    TUTORIAL_CLEARING_NODES = 9,
    TUTORIAL_THEMING = 10,
    TUTORIAL_NETWORKING = 11,
    TUTORIAL_END_SCREEN = 12

class TutorialWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, color_manager, font_manager, settings_window):
        """
        Initializes the TutorialWindow class.

        @param manager: pygame_gui.ui_manager.UIManager
        @param color_manager: ColorManager
        @param font_manager: FontManager
        @param settings_window: SettingsWindow
        """
        self.manager = manager
        self.color_manager = color_manager
        self.font_manager = font_manager
        self.settings_window = settings_window
        self.window_width = 650
        self.window_height = 600
        self.window_running = False
        self.stage = 0
        self.load_tutorial_assets()
        self.stages_build_and_clean_functions_dict = {
            TutorialWindowStages.TUTORIAL_WELCOME_SCREEN: {'build': self.build_tutorial_welcome_screen, 'clean': self.clean_tutorial_welcome_screen},
            TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION: {'build': self.build_project_description_screen, 'clean': self.clean_project_description_screen},
            TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM: {'build': self.build_pathfinding_algorithm_screen, 'clean': self.clean_pathfinding_algorithm_screen},
            TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM_INFO: {'build': self.build_pathfinding_algorithm_info_screen, 'clean': self.clean_pathfinding_algorithm_info_screen},
            TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM: {'build': self.build_maze_generation_algorithm_screen, 'clean': self.clean_maze_generation_algorithm_screen},
            TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM_INFO: {'build': self.build_maze_generation_algorithm_info_screen, 'clean': self.clean_maze_generation_algorithm_info_screen},
            TutorialWindowStages.TUTORIAL_SETTINGS: {'build': self.build_settings_screen, 'clean': self.clean_settings_screen},
            TutorialWindowStages.TUTORIAL_FONTS: {'build': self.build_fonts_screen, 'clean': self.clean_fonts_screen},
            TutorialWindowStages.TUTORIAL_MARKED_AND_WEIGHTED_NODES: {'build': self.build_marked_and_weighted_nodes_screen, 'clean': self.clean_marked_and_weighted_nodes_screen},
            TutorialWindowStages.TUTORIAL_CLEARING_NODES: {'build': self.build_clearing_nodes_screen, 'clean': self.clean_clearing_nodes_screen},
            TutorialWindowStages.TUTORIAL_THEMING: {'build': self.build_theming_screen, 'clean': self.clean_theming_screen},
            TutorialWindowStages.TUTORIAL_NETWORKING: {'build': self.build_networking_screen, 'clean': self.clean_networking_screen},
            TutorialWindowStages.TUTORIAL_END_SCREEN: {'build': self.build_end_screen, 'clean': self.clean_end_screen}
        }

    def load_tutorial_assets(self):
        """
        This function will go through each image in the data/tutorial_assets directory
        and remove the file extension from the image file's name. It will then add this
        image file name (without the file extension) as a key for the ui_tutorial_images_surfaces_dict
        dictionary with the value for the key being the loaded image file (this should be a pointer to
        or a way for us to access the image file in memory so that it is ready to draw onto the screen).
        """
        file_names = os.listdir('data/tutorial_assets')
        keys = [file_name[:-4] for file_name in file_names]
        self.ui_tutorial_image_surfaces_dict = {}

        for i in range(len(keys)):
            self.ui_tutorial_image_surfaces_dict[keys[i]] = pygame.image.load('data/tutorial_assets/' + file_names[i]).convert_alpha()

        print('[UI MANAGER] Tutorial asset keys:', keys)

    def fill_image_with_color_and_set_shadow_to_border_color(self, key, color, shadow_colour=(255, 0, 0)):
        """
        This function will go through each pixel in the image specified by the key (we will get the image
        data by accessing with the key given in ui_tutorial_image_surfaces_dict dictionary) and it will check
        the value of the alpha channel of the pixel. If the pixel is transparent then we will continue to the next
        iteration otherwise we will check if the rgb values of the pixel are the same as those specified in the
        shadow_colour given. If it is, we will make the rgb value of this pixel be the same as the UI_BORDER_COLOR
        (we can get this by accessing the UI_BORDER_COLOR method in self.color_manager). If the rgb values are not the
        same as the shadow_colour we will instead set the rgb values of the pixel to be the same as the color given.

        @param key: str
        @param color: tuple
        @param shadow_colour: tuple
        """
        width, height = self.ui_tutorial_image_surfaces_dict[key].get_size()

        for y in range(height):
            for x in range(width):
                current_colour = self.ui_tutorial_image_surfaces_dict[key].get_at((x, y))
                alpha_value = current_colour[3]
                if alpha_value != 0:
                    color[3] = alpha_value
                    if current_colour[0] == shadow_colour[0]:
                        new_color = self.color_manager.UI_BORDER_COLOR
                        new_color[3] = alpha_value
                        self.ui_tutorial_image_surfaces_dict[key].set_at((x, y), new_color)
                    else:
                        self.ui_tutorial_image_surfaces_dict[key].set_at((x, y), color)

    def build_tutorial_welcome_screen(self):
        """
        It will first create a window and then create the widgets for TutorialWindowStages.TUTORIAL_WELCOME_SCREEN.
        """
        self.stage = TutorialWindowStages.TUTORIAL_WELCOME_SCREEN

        if self.window_running == False:
            print("[TUTORIAL WINDOW] Set self.window_running to True")

            self.window_running = True
            super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                             window_display_title='Tutorial',
                             manager=self.manager)
            self.set_blocking(True)

            self.previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (50, 30)),
                                                                     text='<-',
                                                                     container=self,
                                                                     manager=self.manager)

            self.next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.window_width - 90, 5), (50, 30)),
                                                                 text='->',
                                                                 container=self,
                                                                 manager=self.manager)

        self.previous_page_button.disable()

        self.welcome_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                              html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Tutorial</var></font>",
                                                              object_id="#text_box_title",
                                                              container=self,
                                                              manager=self.manager)


        self.fill_image_with_color_and_set_shadow_to_border_color('game_tutorial_logo', self.color_manager.UI_TEXT_COLOR)
        self.game_tutorial_logo_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((130, 70), (350, 350)),
                                                                    image_surface=self.ui_tutorial_image_surfaces_dict['game_tutorial_logo'],
                                                                    container=self,
                                                                    manager=self.manager)


        self.disable_tutorial_on_startup = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((410, 470), (180, 50)),
                                                                        text='Disable On Startup',
                                                                        container=self,
                                                                        manager=self.manager)

        if self.settings_window.should_build_tutorial_window_on_startup() == False:
            self.disable_tutorial_on_startup.hide()

    def clean_tutorial_welcome_screen(self):
        """
        Removes the widgets TutorialWindowStages.TUTORIAL_WELCOME_SCREEN.
        """
        self.welcome_text_box.kill()
        self.game_tutorial_logo_image.kill()
        self.disable_tutorial_on_startup.kill()

    def build_project_description_screen(self):
        """
        Creates widgets for TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION.
        """
        self.stage = TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION
        self.project_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                          html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Project Description</var></font>",
                                                                          object_id="#text_box_title",
                                                                          container=self,
                                                                          manager=self.manager)

        description_text = (
            f"Pathfind is a tool designed to help you find different routes between nodes"
            f" through using various kinds of algorithms. From Dijkstra's to A*. You can always"
            f" FIND THE PATH.<br><br>To playing pathfinding puzzles with your friends, to creating"
            f" your own colour schemes, creativity is your limitation."
        )
        self.project_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 170)),
                                                                          html_text=description_text,
                                                                          container=self,
                                                                          manager=self.manager)

        self.fill_image_with_color_and_set_shadow_to_border_color('point_a_to_b', self.color_manager.UI_TEXT_COLOR)
        self.point_a_to_b_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((200, 270), (220, 220)),
                                                              image_surface=self.ui_tutorial_image_surfaces_dict['point_a_to_b'],
                                                              container=self,
                                                              manager=self.manager)
        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_project_description_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION.
        """
        self.project_description_text_box.kill()
        self.point_a_to_b_image.kill()

    def build_pathfinding_algorithm_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM.
        """
        self.stage = TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM
        self.pathfinding_algorithm_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                            html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Pathfinding Algorithms</var></font>",
                                                                            object_id="#text_box_title",
                                                                            container=self,
                                                                            manager=self.manager)

        description_text = (
            f"Pathfind supports the use of various kinds of algorithms some which are "
            f"<b>weighted</b> and others which are <b>unweighted</b>.<br><br>You can select"
            f" a pathfinding algorithm using the pathfinding algorithms menu (picture on bottom left)"
            f" and then press the <b>run</b> button (picture at the bottom) to run the algorithm.<br><br>"
            f"You should also note that some algorithms also support <b>heuristics</b> which you will be able"
            f" to select using the heuristics menu (picture on the bottom right). The heuristics menu will only"
            f" appear if the pathfinding algorithm supports heuristics).<br><br>When an algorithm is running you"
            f" can change the speed at which the nodes are being animated by changing the <b>Pathfinding Algorithm Speed</b> slider."
        )
        self.pathfinding_algorithm_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 220)),
                                                                                        html_text=description_text,
                                                                                        container=self,
                                                                                        manager=self.manager)

        self.pathfinding_algorithms_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((100, 320), (215, 185)),
                                                                             image_surface=self.ui_tutorial_image_surfaces_dict['pathfinding_algorithms_menu'],
                                                                             container=self,
                                                                             manager=self.manager)

        self.heuristics_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((350, 320), (213, 103)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['heuristics_menu'],
                                                                 container=self,
                                                                 manager=self.manager)

        self.run_button_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((360, 433), (190, 60)),
                                                            image_surface=self.ui_tutorial_image_surfaces_dict['run_button'],
                                                            container=self,
                                                            manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_pathfinding_algorithm_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM.
        """
        self.pathfinding_algorithm_text_box.kill()
        self.pathfinding_algorithm_description_text_box.kill()
        self.pathfinding_algorithms_menu_image.kill()
        self.heuristics_menu_image.kill()
        self.run_button_image.kill()

    def build_pathfinding_algorithm_info_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM_INFO.
        """
        self.stage = TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM_INFO
        self.pathfinding_algorithm_info_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                                 html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Pathfinding Algorithms Info</var></font>",
                                                                                 object_id="#text_box_title",
                                                                                 container=self,
                                                                                 manager=self.manager)

        description_text = (
            f"Brief description of each pathfinding algorithm supported in Pathfind.<br><br>"
            f"<b>Depth Fist Search</b> (unweighted): Very slow, very bad. Doesn't guarantee the shortest path.<br>"
            f"<b>Breadth First Search</b> (unweighted): Pretty solid algorithm and it guarantees the shortest path.<br>"
            f"<b>Dijkstra</b> (weighted): The father of pathfinding algorithms, supports weights and guarantees the shortest path.<br>"
            f"<b>A*</b> (weighted): Supports weights and is faster than Dijkstra through the use of heuristics (estimate "
            f"of how far a specific node is from a target node). Also guarantees the shortest path.<br>"
            f"<b>Greedy Best First Search</b> (unweighted): Only relies on heuristics and doesn't support weights, but it's pretty fast!"
            f" Doesn't guarantee the shortest path.<br>"
            f"<b>Bidirectional Best First Search</b> (unweighted): Launches breadth first search from both the starting node and the target"
            f" node, so it's twice as fast as BFS! It also guarantees the shortest path.<br>"
        )
        self.pathfinding_algorithm_info_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 430)),
                                                                                 html_text=description_text,
                                                                                 container=self,
                                                                                 manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_pathfinding_algorithm_info_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM_INFO.
        """
        self.pathfinding_algorithm_info_title_text_box.kill()
        self.pathfinding_algorithm_info_text_box.kill()


    def build_maze_generation_algorithm_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM.
        """
        self.stage = TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM
        self.maze_generation_algorithm_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                       html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Maze Generation</var></font>",
                                                                       object_id="#text_box_title",
                                                                       container=self,
                                                                       manager=self.manager)

        description_text = (
            f"Pathfind allows you to create your own mazes and also generate mazes using different algorithms, some of "
            f"these maze generation algorithms are <b>weighted</b> and others are <b>unweighted</b>.<br><br> You can select a maze generation "
            f"algorithm by using the maze generation algorithms menu (picture at the bottom).<br><br>Maze generation algorithms "
            f"which use Recursive Division will be animated sequentially (like a pathfinding algorithm) for this reason you are "
            f"able to manipulate the speed at which these algorithms are being animated using the <b>Recursive Division Speed</b>"
            f" slider. When a Recursive Division algorithm is running you can also press the <b>Cancel</b> button to stop the algorithm"
            f" from adding new nodes to the maze."
        )
        self.maze_generation_algorithm_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 240)),
                                                                                            html_text=description_text,
                                                                                            container=self,
                                                                                            manager=self.manager)


        self.mazes_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((200, 350), (210, 163)),
                                                            image_surface=self.ui_tutorial_image_surfaces_dict['mazes_menu'],
                                                            container=self,
                                                            manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_maze_generation_algorithm_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM.
        """
        self.maze_generation_algorithm_title_text_box.kill()
        self.maze_generation_algorithm_description_text_box.kill()
        self.mazes_menu_image.kill()


    def build_maze_generation_algorithm_info_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM_INFO.
        """
        self.stage = TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM_INFO
        self.maze_generation_algorithm_info_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                                           html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Maze Generation Algorithms</var></font>",
                                                                                           object_id="#text_box_title",
                                                                                           container=self,
                                                                                           manager=self.manager)

        description_text = (
            f"Brief description of each maze generation algorithm supported in Pathfind.<br><br>"
            f"<b>Random Maze</b> (unweighted): Pretty simple algorithm. Just go through each node and "
            f"randomly choose whether or not it should be marked, doesn't guarantee a perfect maze.<br>"
            f"<b>Random Weighted Maze</b> (weighted): Same steps as a random maze, but we give"
            f" each node in the maze a random weight, also doesn't guarantee a perfect maze.<br>"
            f"<b>RD(Recursive Division)</b> (unweighted): An interesting algorithm, it divides the grid horizontally"
            f" and vertically by adding a wall of marked nodes and adds an empty space inside of these walls"
            f" to ensure a perfect maze! (oversimplified explanation).<br>"
            f"<b>RD Horizontal Skew</b> (unweighted): Recursive Division but biased horizontally (it will make more"
            f" horizontal splits of the maze). Guarantees a perfect maze.<br>"
            f"<b>RD Vertical Skew</b> (unweighted): Recursive Division but biased vertically (it will make more"
            f" vertical splits of the maze), also guarantees a perfect maze.<br>"
        )

        self.maze_generation_algorithm_info_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 430)),
                                                                                                 html_text=description_text,
                                                                                                 container=self,
                                                                                                 manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_maze_generation_algorithm_info_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_MAZE_GENERATION_ALGORITHM_INFO.
        """
        self.maze_generation_algorithm_info_title_text_box.kill()
        self.maze_generation_algorithm_info_description_text_box.kill()


    def build_settings_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_SETTINGS.
        """
        self.stage = TutorialWindowStages.TUTORIAL_SETTINGS
        self.settings_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                                           html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Settings</var></font>",
                                                                                           object_id="#text_box_title",
                                                                                           container=self,
                                                                                           manager=self.manager)

        description_text = (
            f"Pathfind also allows you customize the look and feel of the UI to help suit your needs and preferences.<br>"
            f"You can access the Settings Window (picture at the bottom) by pressing the <b>settings</b> button.<br><br>"
            f"<b>UI Element Shape</b>: This will allow to choose whether you want the UI to use a <b>Rectangle</b> shape "
            f"(with hard edges) or a <b>Rounded Rectangle</b> shape (with rounded edges).<br>"
            f"<b>UI Corner Roundness</b>: If the <b>UI Element Shape</b> is set to be a <b>Rounded Rectangle</b> then"
            f" the <b>UI Corner Roundness</b> slider will allow to change how round the edges of the UI Elements are.<br>"
            f"<b>Grid Width</b>: This slider will allow you set the thickness of the lines drawn on the grid.<br>"
            f"<b>UI Border Width</b>: This slider will change the thickness of the UI Elements.<br>"
            f"<b>UI Normal Font Size</b>: This slider will change the font size of the text in every element in the UI except"
            f" for the titles in windows.<br>"
            f"<b>UI Title Font Size</b>: This slider will only change the font size of the titles in windows (e.g. the title"
            f" for the last page was <b>Maze Generation Algorithms</b> which you could see at the top of the screen before).<br>"
            f"<b>UI Font</b>: This Drop Down Menu will allow to change the fonts the UI is using as well as creating and deleting"
            f" custom fonts (more information about this on the next page).<br>"
            f"<b>Disable Tutorial on Startup</b>: This button will allow you toggle whether or not you want to stop the tutorial"
            f" from appearing whenever the game starts up, and this is false by default (if this option is set to false you can "
            f"also press the <b>Disable on Startup</b> button on the first page of the tutorial to stop the tutorial from appearing "
            f"whenever the game is launched).<br>"
            f"<b>Reset</b>: This button will change all of the settings back to their default values.<br>"
            f"<b>Save</b>: This button will save you current settings. So when you restart the game, the game will continue to use"
            f" the same settings you are using now.<br>"
        )

        self.settings_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 80), (520, 205)),
                                                                           html_text=description_text,
                                                                           container=self,
                                                                           manager=self.manager)



        self.settings_window_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((180, 300)), (249, 229)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['settings_window'],
                                                                 container=self,
                                                                 manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_settings_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_SETTINGS.
        """
        self.settings_title_text_box.kill()
        self.settings_description_text_box.kill()
        self.settings_window_image.kill()

    def build_fonts_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_FONTS.
        """
        self.stage = TutorialWindowStages.TUTORIAL_FONTS
        self.fonts_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                  html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Fonts</var></font>",
                                                                  object_id="#text_box_title",
                                                                  container=self,
                                                                  manager=self.manager)

        description_text = (
            f"Pathfind allows you to select custom fonts for the UI. If you want to create a new custom font you should select"
            f" the <b>Create Custom Font</b> Option from the <b>UI Font</b> Drop Down Menu located in the settings window and"
            f" this will open up the <b>Custom Font Creation</b> page (picture on the bottom left). You can use the <b>Find File</b>"
            f" buttons to browse your filesystem and find the location of the font you want to use.<br><br>"
            f"<b>Normal Font File Path (Regular Weight)</b>: This is the file path to the font file you want to use for regular"
            f" text anywhere in the UI except for the titles in windows.<br>"
            f"<b>Normal Font File Path (Bold Weight)</b>: This is the file path to the font file you want to use for bold text"
            f" anywhere in the UI except for the titles in windows.<br>"
            f"<b>Title Font File Path (Regular Weight)</b>: This is the the file path to the font file you want to use for the titles"
            f" in windows.<br>"
            f"<b>Custom Font Name</b>: Name of the custom font you are creating.<br>"
            f"<b>Create Custom Font</b>: This will create the new custom font if all of the information you provided is correct (i.e."
            f" you have filled in each data entry, you have selected valid font files and the custom font name you have specified is not"
            f" already being used by any other font).<br><br>"
            f"If you have already created a custom font and you want to delete it you can select the <b>Delete Custom Font</b> Option from the "
            f"<b>UI Font</b> Drop Down Menu (this option will only appear if you have already created a custom font). This will open the "
            f"<b>Custom Font Deletion</b> page where you can select the custom fonts you want to delete and then press the <b>Delete</b> to delete them."
        )

        self.fonts_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 80), (520, 205)),
                                                                        html_text=description_text,
                                                                        container=self,
                                                                        manager=self.manager)



        self.custom_font_creation_screen_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((40, 300)), (249, 229)),
                                                                             image_surface=self.ui_tutorial_image_surfaces_dict['custom_font_creation_screen'],
                                                                             container=self,
                                                                             manager=self.manager)

        self.custom_font_deletion_screen_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((320, 298)), (249, 235)),
                                                                             image_surface=self.ui_tutorial_image_surfaces_dict['custom_font_deletion_screen'],
                                                                             container=self,
                                                                             manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_fonts_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_FONTS.
        """
        self.fonts_title_text_box.kill()
        self.fonts_description_text_box.kill()
        self.custom_font_creation_screen_image.kill()
        self.custom_font_deletion_screen_image.kill()


    def build_marked_and_weighted_nodes_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_MARKED_AND_WEIGHTED_NODES.
        """
        self.stage = TutorialWindowStages.TUTORIAL_MARKED_AND_WEIGHTED_NODES
        self.marked_and_weighted_nodes_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                                     html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Marked and Weighted Nodes</var></font>",
                                                                                     object_id="#text_box_title",
                                                                                     container=self,
                                                                                     manager=self.manager)

        description_text = (
            f"Pathfind's pathfinding algorithms support 2 types of nodes. <b>Marked</b> nodes and <b>Weighted</b> nodes."
            f" Marked nodes simply act as a barrier which the pathfinding algorithms must traverse around to find a path."
            f" Weighted nodes on the other hand behave slightly differently. A weighted node is a node which has a distance value (also"
            f" known as a <b>weight</b>) which is used to signify the cost of traversing to the node. Certain pathfinding algorithms"
            f" (Dijkstra and A*) will take these weights into consideration in order to find an ideal path to the target node.<br><br>"
            f"You can select whether you want to place marked or weighted nodes using the <b>Marked or Weighted Node</b> Drop Down Menu"
            f" (picture at the bottom). If you select the <b>Marked</b> option you are able to place and remove marked nodes using the left"
            f" and right mouse button respectively. Alternatively, if you select the <b>Weighted</b> option you can type in the weight you"
            f" want the nodes to have using the text entry line on the right and any nodes you place using the left mouse button will have"
            f" the specified weight, you can also remove weighted nodes using the right mouse button."
        )
        self.marked_and_weighted_nodes_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 270)),
                                                                                            html_text=description_text,
                                                                                            container=self,
                                                                                            manager=self.manager)


        self.marked_and_weighted_nodes_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((130, 370), (368, 104)),
                                                                           image_surface=self.ui_tutorial_image_surfaces_dict['marked_or_weighted_nodes'],
                                                                           container=self,
                                                                           manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_marked_and_weighted_nodes_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_MARKED_AND_WEIGHTED_NODES.
        """
        self.marked_and_weighted_nodes_title_text_box.kill()
        self.marked_and_weighted_nodes_description_text_box.kill()
        self.marked_and_weighted_nodes_image.kill()

    def build_clearing_nodes_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_CLEARING_NODES.
        """
        self.stage = TutorialWindowStages.TUTORIAL_CLEARING_NODES
        self.clearing_nodes_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                           html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Clearing Nodes</var></font>",
                                                                           object_id="#text_box_title",
                                                                           container=self,
                                                                           manager=self.manager)

        description_text = (
            f"You can clear different kinds of nodes from the grid using the <b>Clear Nodes</b> drop down menu (picture at the bottom)."
            f" A shortcut to clear all the nodes from the screen is to press the <b>c</b> key.<br><br>"
            f"<b>Clear Grid</b>: Clears all the nodes off the grid.<br>"
            f"<b>Clear Path</b>: Only clears nodes which are in the path.<br>"
            f"<b>Clear Checked Nodes</b>: Only clears nodes which have been checked by a pathfinding algorithm.<br>"
            f"<b>Clear Marked Nodes</b>: Only clears marked nodes.<br>"
            f"<b>Clear Weighted Nodes</b>: Only clears weighted nodes.<br>"
        )
        self.clearing_nodes_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 255)),
                                                                                 html_text=description_text,
                                                                                 container=self,
                                                                                 manager=self.manager)

        self.clear_grid_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((200, 350), (215, 175)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['clear_grid_menu'],
                                                                 container=self,
                                                                 manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_clearing_nodes_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_CLEARING_NODES.
        """
        self.clearing_nodes_title_text_box.kill()
        self.clearing_nodes_description_text_box.kill()
        self.clear_grid_menu_image.kill()

    def build_theming_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_THEMING.
        """
        self.stage = TutorialWindowStages.TUTORIAL_THEMING
        self.theming_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                    html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Theming</var></font>",
                                                                    object_id="#text_box_title",
                                                                    container=self,
                                                                    manager=self.manager)

        description_text = (
            f"Pathfind also allows you to create and delete custom themes. These custom themes will allow you change the colour"
            f" of every element in the UI from the background colour to even the colour of the title text. You can access this by"
            f" using the <b>Themes Menu</b> (picture at the bottom). By default there are 3 default themes in the game <b>Dark Theme</b>"
            f" (this is the theme which is set whenever you start the game), <b>Light Theme</b> and <b>Gruvbox</b>.<br><br>"
            f"You can create custom themes using the <b>Create Custom Theme</b> option. This will open a new page which will allow you "
            f"to specify the name of your new theme and also whether you want to inherit colours from another themes, you can then modify the"
            f" individual colours in the theme and then create the theme. If you have already created custom themes you can edit the colours in the"
            f" theme using the <b>Edit Custom Theme</b> option or you can also delete the custom themes using the <b>Delete Custom Theme</b> option."
        )
        self.theming_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (510, 215)),
                                                                          html_text=description_text,
                                                                          container=self,
                                                                          manager=self.manager)

        self.themes_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((200, 300), (212, 225)),
                                                             image_surface=self.ui_tutorial_image_surfaces_dict['themes_menu'],
                                                             container=self,
                                                             manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_theming_screen(self):
        """
        Removes the widgets for TutorialWindowStages.TUTORIAL_THEMING.
        """
        self.theming_title_text_box.kill()
        self.theming_description_text_box.kill()
        self.themes_menu_image.kill()

    def build_networking_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_NETWORKING.
        """
        self.stage = TutorialWindowStages.TUTORIAL_NETWORKING
        self.networking_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                       html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Networking</var></font>",
                                                                       object_id="#text_box_title",
                                                                       container=self,
                                                                       manager=self.manager)

        description_text = (
            f"Pathfind has built-in network functionality so you can play with your friends! This networking feature"
            f" will allow you to share a grid with your friends where you can all interactively place nodes, run "
            f"pathfinding and maze generation algorithms and see the results.<br><br>To access these networking"
            f" features you must use the <b>Networking Menu</b> (picture on the bottom left) if you want to create"
            f" a server you should select the <b>Create Server</b> option which will create a server on running on"
            f" your local IP Address on a certain port (this information will be shown in a window on your screen), you"
            f" can then share this information with you friends who can then join the server. In order to join a server"
            f" you must select the <b>Connect to Server</b> option which will open up the <b>Connect to Server Window</b>"
            f" (picture on the bottom right) you can then type down the IP Address and port the server is running on "
            f" and try to connect to the server by pressing the <b>Connect</b> button. If the information is valid you "
            f" will receive a message that you have successfully joined the server otherwise you will receive a message"
            f" that we've been unable to establish a connection to the server."
        )

        self.networking_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 80), (520, 205)),
                                                                           html_text=description_text,
                                                                           container=self,
                                                                           manager=self.manager)



        self.networking_menu_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((90, 300)), (209, 102)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['networking_menu'],
                                                                 container=self,
                                                                 manager=self.manager)

        self.connect_to_server_window_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((320, 300)), (249, 229)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['connect_to_server_window'],
                                                                 container=self,
                                                                 manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_networking_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_NETWORKING.
        """
        self.networking_title_text_box.kill()
        self.networking_description_text_box.kill()
        self.networking_menu_image.kill()
        self.connect_to_server_window_image.kill()

    def build_end_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_END_SCREEN.
        """
        self.stage = TutorialWindowStages.TUTORIAL_END_SCREEN
        self.end_title_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>The End</var></font>",
                                                                object_id="#text_box_title",
                                                                container=self,
                                                                manager=self.manager)

        description_text = (
            f"This page marks the end of the Tutorial. Remember you can always return to the tutorial by pressing"
            f" the <b>Tutorial</b> button (picture at the bottom).<br><br>Continue to explore and enjoy the game!"
        )

        self.end_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((60, 80), (520, 205)),
                                                                      html_text=description_text,
                                                                      container=self,
                                                                      manager=self.manager)

        self.tutorial_button_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(((240, 300)), (143, 134)),
                                                                 image_surface=self.ui_tutorial_image_surfaces_dict['tutorial_button'],
                                                                 container=self,
                                                                 manager=self.manager)


        self.next_page_button.disable()
        self.previous_page_button.enable()

    def clean_end_screen(self):
        """
        Creates the widgets for TutorialWindowStages.TUTORIAL_END_SCREEN.
        """
        self.end_title_text_box.kill()
        self.end_description_text_box.kill()
        self.tutorial_button_image.kill()

    def handle_tutorial_window_ui_button_pressed(self, event):
        """
        Handles the pygame_gui.UI_NETWORKING_MANAGER_UI_BUTTON_PRESSED event for TutorialWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == TutorialWindowStages.TUTORIAL_WELCOME_SCREEN:
                if event.ui_element == self.disable_tutorial_on_startup:
                    print("[TUTORIAL WINDOW] Tutorial Window has been disabled from startup")
                    self.settings_window.set_disable_tutorial_window_on_startup(True)
                    self.disable_tutorial_on_startup.kill()

            if event.ui_element == self.next_page_button:
                if self.stage+1 < 13:
                    self.stages_build_and_clean_functions_dict[self.stage]['clean']()
                    self.stages_build_and_clean_functions_dict[self.stage+1]['build']()
            elif event.ui_element == self.previous_page_button:
                if self.stage-1 > 0:
                    self.stages_build_and_clean_functions_dict[self.stage]['clean']()
                    self.stages_build_and_clean_functions_dict[self.stage-1]['build']()

    def shutdown(self):
        """
        Sets the window_running attribute to False.
        """
        print("[TUTORIAL WINDOW] Shutdown Tutorial Window")
        self.window_running = False

class FontManager:
    def __init__(self, manager, theme_manager, theme_json_data):
        """
        Initializes the FontManager class.

        @param manager: pygame_gui.ui_manager.UIManager
        @param theme_manager: pygame_gui.core.interfaces.appearance_theme_interface.IUIAppearanceThemeInterface
        @param theme_json_data: Dict
        """
        self.manager = manager
        self.theme_manager = theme_manager
        self.theme_json_data = theme_json_data
        self.current_font_name = 'Roboto'
        self.ui_normal_font_size_value = 15
        self.ui_title_font_size_value = 20

        with open('data/fonts/font_info.json') as file:
            self.font_json_data = json.loads(file.read())

    def save_font_json_data(self):
        """
        Will turn the font_json_data dictionary into json and save
        it in the data/fonts/font_info.json file.
        """
        with open('data/fonts/font_info.json', 'w') as file:
            file.write(json.dumps(self.font_json_data))

    def load_ui_fonts(self):
        """
        This function will go through each font in the font_json_data dictionary and check
        if the file paths of the font files still exist in the filesystem. If any of the font
        files no longer exist in the filesystem we will add the font's name to the fonts_to_remove
        list. If all the font files for the font exist we will load the font files into the UI, so
        we can use the font whenever we want. After we finish going through all the fonts in the font_json_data
        dictionary we will iterate over all the fonts in the fonts_to_remove list and remove the
        key-value pair in the dictionary which is associated with the font. After we have finished
        iterating through the fonts_to_remove list we will run the save_font_json_data method.
        """
        self.fonts_to_remove = []

        for font_name in self.font_json_data:
            if (
                    os.path.isfile(self.font_json_data[font_name]['regular']) and
                    os.path.isfile(self.font_json_data[font_name]['bold']) and
                    os.path.isfile(self.font_json_data[font_name]['title'])
            ):
                self.manager.add_font_paths(font_name, self.font_json_data[font_name]['regular'], self.font_json_data[font_name]['bold'], self.font_json_data[font_name]['title'])
                fonts_to_preload_dict = []
                for font_size in range(5, 36):
                    fonts_to_preload_dict.append({"name": font_name, "point_size": font_size, "style": "regular"})
                    fonts_to_preload_dict.append({"name": font_name, "point_size": font_size, "style": "bold"})
                    fonts_to_preload_dict.append({"name": font_name, "point_size": font_size, "style": "italic"})

                self.manager.preload_fonts(fonts_to_preload_dict)
            else:
                self.fonts_to_remove.append(font_name)

        if len(self.fonts_to_remove) > 0:
            for font in self.fonts_to_remove:
                print(f"[FONT MANAGER] Deleted font with name '{font}'")
                del self.font_json_data[font]
            else:
                self.save_font_json_data()

    def add_ui_font(self, font_name, normal_font_regular_weight_file_path, normal_font_bold_weight_file_path, title_font_regular_weight_file_path):
        """
        If the font with the font_name specified does not exist as a key in the font_json_data dictionary
        (we can get a list of all the keys in the font_json_data dictionary using the get_ui_font_names method)
        we will add a new key-value pair into the dictionary where the key will be the font_name given and
        the value will be another dictionary containing the following key-value pairs:

        {
            "custom_font": True,
            "regular": normal_font_regular_weight_file_path,
            "bold": normal_font_bold_weight_file_path,
            "title": title_font_regular_weight_file_path
        }

        After this we will run the save_font_json_data method, and then we will load the font files into
        the UI, so we can the font whenever we want.

        @param font_name: Str
        @param normal_font_regular_weight_file_path: Str
        @param normal_font_bold_weight_file_path: Str
        @param title_font_regular_weight_file_path: Str
        """
        if font_name not in self.get_ui_font_names():
            self.font_json_data[font_name] = {
                "custom_font": True,
                "regular": normal_font_regular_weight_file_path,
                "bold": normal_font_bold_weight_file_path,
                "title": title_font_regular_weight_file_path
            }
            self.save_font_json_data()

            self.manager.add_font_paths(font_name, normal_font_regular_weight_file_path, normal_font_bold_weight_file_path, title_font_regular_weight_file_path)
            preload_font_dict = []
            for font_size in range(5, 36):
                preload_font_dict.append({"name": font_name, "point_size": font_size, "style": "regular"})
                preload_font_dict.append({"name": font_name, "point_size": font_size, "style": "bold"})
                preload_font_dict.append({"name": font_name, "point_size": font_size, "style": "italic"})

            self.manager.preload_fonts(preload_font_dict)
        else:
            print(f"[FONT MANAGER: ADD UI FONT] Error a font already exists with the name '{font_name}'")

    def delete_custom_ui_font(self, font_name):
        """
        If a font with the font_name given exists as a custom font in the font_json_data
        dictionary (we can get a list of all the custom fonts in the font_json_data dictionary
        using the get_custom_ui_font_names method), we will first check if the font_name given
        is the same as the current_font_name attribute. If it is we will set the current_font_name
        attribute equal to the default font we load at the start of the game (by default I use the
        'Roboto' font) and we will also run the set_current_font method and pass in the name of the
        default font we use as a string. After this, we will remove the key-value pair associated
        with the font_name given, from the font_json_data dictionary, and then we will run the
        save_font_json_data method.

        @param font_name: Str
        """
        if font_name in self.get_custom_ui_font_names():
            if font_name == self.current_font_name:
                self.current_font_name = "Roboto"
                self.set_current_font("Roboto")

            self.font_json_data.pop(font_name)
            self.save_font_json_data()
        else:
            print(f"[FONT MANAGER: DELETE_UI_FONT] Error no custom font exists with the name '{font_name}'")


    def set_current_font(self, font_name):
        """
        If a font with the font_name specified exists as a key in the font_json_data dictionary (we can
        get a list of all the keys in the font_json_data dictionary using the get_ui_font_names method)
        we will the set the current_font_name attribute to be equal to the font_name given, and we will
        perform the relevant operations to ensure that the UI is using this new font. In the case that
        the font with the font_name specified does not exist in the font_json_data dictionary we will
        return False.

        @param font_name: Str
        @return: None or False
        """
        if font_name in self.get_ui_font_names():
            self.current_font_name = font_name
            for ui_element in self.theme_json_data:
                if 'font' in self.theme_json_data[ui_element]:
                    if 'normal_font' in self.theme_json_data[ui_element]['font']:
                        self.theme_json_data[ui_element]['font']['name'] = font_name
            else:
                self.theme_manager.update_theming(json.dumps(self.theme_json_data))

        else:
            print(f"[FONT MANAGER: SET_CURRENT_FONT] Error no font exists with the name '{font_name}'")
            return False

    def set_normal_font_size(self, font_size):
        """
        This function will set the ui_normal_font_size_value attribute to be
        equal to the font_size given, we will then perform the relevant operations
        to ensure that the UI also uses this font size for every element on the screen
        except for the titles at the top of windows.

        @param font_size: int
        """
        for ui_element in self.theme_json_data:
            if 'font' in self.theme_json_data[ui_element]:
                if 'normal_font' in self.theme_json_data[ui_element]['font']:
                    self.theme_json_data[ui_element]['font']['size'] = font_size
        else:
            self.ui_normal_font_size_value = font_size
            self.theme_manager.update_theming(json.dumps(self.theme_json_data))

    def get_ui_font_names(self):
        """
        This function will return a list containing all the keys in the
        font_json_data dictionary.

        @return: List
        """
        return list(self.font_json_data.keys())

    def get_custom_ui_font_names(self):
        """
        This function will go through each font in the font_json_data dictionary. It will
        then retrieve the dictionary which is the value of the font and check if the custom_font
        key in this dictionary contains the value True. If it does we will add this font to the
        custom_font_names list. After we have iterated over all the fonts in the font_json_data
        dictionary we will return the custom_font_names list.

        @return: List
        """
        custom_font_names = []
        for font in self.font_json_data:
            if self.font_json_data[font]['custom_font']:
                custom_font_names.append(font)

        return custom_font_names

    def custom_ui_fonts_exist(self):
        """
        This function will go through each font in the font_json_data dictionary. It will
        then retrieve the dictionary which is the value of the font and check if the custom_font
        key in this dictionary contains the value True. If it does we will return True and exit
        the function otherwise we will continue to the next iteration. If we have completed all
        the iterations then this would mean that there aren't any custom fonts in the font_json_data
        dictionary, and so we will return False.
        @return:
        """
        for font_name in self.font_json_data:
            if self.font_json_data[font_name]['custom_font']:
                return True
        else:
            return False


class SettingsWindowStages(IntEnum):
    SETTINGS_WINDOW_SETTINGS_SCREEN = 0,
    SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN = 1,
    SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN = 2

class SettingsWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, theme_manager, theme_json_data, grid, font_manager):
        """
        Initializes the SettingsWindow class.

        @param manager: pygame_gui.ui_manager.UIManager
        @param theme_manager: pygame_gui.core.interfaces.appearance_theme_interface.IUIAppearanceThemeInterface
        @param theme_json_data: Dict
        @param grid: Grid
        @param font_manager: FontManager
        """
        self.manager = manager
        self.theme_manager = theme_manager
        self.theme_json_data = theme_json_data
        self.grid = grid
        self.font_manager: FontManager = font_manager
        self.window_width = 650
        self.window_height = 600
        self.window_running = False
        self.changed_ui_border_width = False
        self.custom_font_label_name_for_file_path_dialog = None
        self.custom_normal_font_regular_weight_file_path_string = None
        self.custom_normal_font_bold_weight_file_path_string = None
        self.custom_title_font_regular_weight_file_path_string = None
        self.custom_fonts_to_delete_names = []
        self.stage = None
        self.load_user_settings()

    def load_user_settings(self):
        """
        This function will first open the data/settings/user_settings.json file, and it
        will read all the json data in the file and convert it into a dictionary which will
        be stored in the user_settings_json_data attribute. We will then perform the
        relevant operations required to apply the settings in the user_settings_json_data
        dictionary to the UI and the grid (this consists of things such as the corner roundness
        of UI Elements, the shape of UI Elements, the border width of the UI Elements, the thickness
        of the lines on the grid, the font size of normal UI Elements, the font size of titles in
        the UI and the font we should be using in the UI.
        """

        with open('data/settings/user_settings.json') as file:
            self.user_settings_json_data = json.loads(file.read())

        self.ui_element_shape = self.user_settings_json_data['ui_element_shape']
        self.ui_corner_roundness_value = self.user_settings_json_data['ui_corner_roundness_value']
        if self.ui_element_shape == 'Rectangle':
            self.theme_json_data['#ui_element_shape']['misc']['shape'] = 'rectangle'
            self.theme_json_data['horizontal_slider.#right_button']['misc']['shape'] = 'rectangle'
            self.theme_json_data['horizontal_slider.#left_button']['misc']['shape'] = 'rectangle'
        else:
            self.theme_json_data['#ui_element_shape']['misc']['shape'] = 'rounded_rectangle'
            self.handle_settings_window_ui_corner_roundness_changed()

        self.theme_manager.update_theming(json.dumps(self.theme_json_data))
        self.ui_border_width_value = self.user_settings_json_data['ui_border_width_value']
        self.grid.line_width = self.user_settings_json_data['grid_width']
        self.font_manager.set_normal_font_size(self.user_settings_json_data['ui_normal_font_size_value'])
        self.font_manager.ui_title_font_size_value = self.user_settings_json_data['ui_title_font_size_value']
        successfully_changed_current_font = self.font_manager.set_current_font(self.user_settings_json_data['current_font_name'])
        if successfully_changed_current_font == False:
            self.user_settings_json_data['current_font_name'] = "Roboto"
            self.save_user_settings()

    def save_user_settings(self):
        """
        This function will turn the dictionary stored in the user_settings_json_data
        attribute into a json string, and we will overwrite the file at data/settings/user_settings.json
        with this json string.
        """
        with open('data/settings/user_settings.json', 'w') as file:
            file.write(json.dumps(self.user_settings_json_data))

    def handle_settings_window_border_width_changed(self):
        """
        This function will set the changed_ui_border_width attribute to True, and it will
        perform the relevant operations to ensure that the border width of the UI Elements
        is the same as the ui_border_width_value attribute.
        """
        print("ui_border_width_value:", self.ui_border_width_value)
        self.theme_json_data['#ui_element_shape']['misc']['border_width'] = str(self.ui_border_width_value)
        self.theme_json_data['drop_down_menu']['misc']['border_width'] = str(self.ui_border_width_value)
        self.theme_json_data['text_entry_line']['misc']['border_width'] = str(self.ui_border_width_value)
        if self.ui_border_width_value < 3:
            self.theme_json_data['horizontal_slider.#sliding_button']['misc']['border_width'] = str(self.ui_border_width_value)

        self.theme_manager.update_theming(json.dumps(self.theme_json_data))
        self.changed_ui_border_width = True

        self.ui_element_shape_drop_down_menu.kill()
        self.ui_element_shape_drop_down_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((70, 100), (160, 40)),
                                                                                  options_list=['Rounded Rectangle', 'Rectangle'],
                                                                                  starting_option=self.ui_element_shape,
                                                                                  container=self,
                                                                                  manager=self.manager)

        self.ui_font_drop_down_menu.kill()

        font_name_list = self.font_manager.get_ui_font_names()
        font_name_list.append('Create Custom Font')
        if self.font_manager.custom_ui_fonts_exist():
            font_name_list.append('Delete Custom Font')

        self.ui_font_drop_down_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((80, 380), (160, 40)),
                                                                         options_list=font_name_list,
                                                                         starting_option=self.font_manager.current_font_name,
                                                                         container=self,
                                                                         manager=self.manager)

    def handle_settings_window_ui_corner_roundness_changed(self):
        """
        This function will perform the relevant operations to ensure that the
        corner roundness of the UI Elements is the same as the ui_corner_roundness_value
        attribute.
        """
        self.theme_json_data['#ui_element_shape']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value)
        self.theme_json_data['horizontal_slider.#sliding_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_json_data['selection_list.@selection_list_item']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value)
        self.theme_json_data['#colour_picker_dialog.colour_channel_editor.horizontal_slider.#sliding_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_json_data['#colour_picker_dialog.colour_channel_editor.text_entry_line']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value)
        self.theme_json_data['vertical_scroll_bar.#top_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_json_data['vertical_scroll_bar.#bottom_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_json_data['horizontal_slider.#right_button']['misc']['shape'] = 'rounded_rectangle'
        self.theme_json_data['horizontal_slider.#left_button']['misc']['shape'] = 'rounded_rectangle'
        self.theme_json_data['horizontal_slider.#left_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_json_data['horizontal_slider.#right_button']['misc']['shape_corner_radius'] = str(self.ui_corner_roundness_value // 2)
        self.theme_manager.update_theming(json.dumps(self.theme_json_data))

    def should_build_tutorial_window_on_startup(self):
        """
        This function will return the result of performing the logical negation operation
        on the boolean stored as the value of the 'disabled_tutorial_on_startup' key in
        the user_settings_json_data dictionary.

        @return: bool
        """
        return not self.user_settings_json_data['disable_tutorial_on_startup']

    def set_disable_tutorial_window_on_startup(self, option):
        """
        This function will set the value of the 'disable_tutorial_on_startup' key
        in the user_settings_json_data dictionary to the boolean value option given.
        After this it will run the save_user_settings method.

        @param option: bool
        """
        self.user_settings_json_data['disable_tutorial_on_startup'] = option
        self.save_user_settings()

    def build_settings_window(self):
        """
        It will first create a window and then create the widgets for SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN.
        After this it will run the handle_settings_window_border_width_changed method.
        """
        self.stage = SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN

        if self.window_running == False:
            print("[SETTINGS WINDOW] Set self.window_running to True")

            self.window_running = True
            super().__init__(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                             window_display_title='Settings',
                             manager=self.manager)

            self.set_blocking(True)

        self.welcome_to_settings_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, -5), (self.window_width - 180, 80)),
                                                                          html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Settings</var></font>",
                                                                          object_id="#text_box_title",
                                                                          container=self,
                                                                          manager=self.manager)

        self.ui_element_shape_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((60, 60), (180, 40)),
                                                                  text="UI Element Shape",
                                                                  container=self,
                                                                  manager=self.manager)

        self.ui_element_shape_drop_down_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((70, 100), (160, 40)),
                                                                                  options_list=['Rounded Rectangle', 'Rectangle'],
                                                                                  starting_option=self.ui_element_shape,
                                                                                  container=self,
                                                                                  manager=self.manager)

        self.ui_corner_roundness_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((330, 60), (240, 40)),
                                                                     text="UI Corner Roundness",
                                                                     container=self,
                                                                     manager=self.manager)

        self.ui_corner_roundness_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((340, 100), (210, 27)),
                                                                                 start_value=self.ui_corner_roundness_value,
                                                                                 value_range=(3, 11),
                                                                                 container=self,
                                                                                 manager=self.manager)
        if self.ui_element_shape == 'Rectangle':
            self.ui_corner_roundness_slider.disable()

        self.grid_width_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 160), (160, 40)),
                                                            text="Grid Width",
                                                            container=self,
                                                            manager=self.manager)

        self.grid_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((50, 200), (210, 27)),
                                                                        start_value=self.grid.line_width,
                                                                        value_range=(1, 7),
                                                                        container=self,
                                                                        manager=self.manager)

        self.ui_border_width_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((365, 160), (160, 40)),
                                                                 text="UI Border Width",
                                                                 container=self,
                                                                 manager=self.manager)

        self.ui_border_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((340, 200), (210, 27)),
                                                                             start_value=self.ui_border_width_value,
                                                                             value_range=(1, 4),
                                                                             container=self,
                                                                             manager=self.manager)

        self.ui_normal_font_size_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((55, 260), (200, 40)),
                                                                     text="UI Normal Font Size",
                                                                     container=self,
                                                                     manager=self.manager)

        self.ui_normal_font_size_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((50, 300), (210, 27)),
                                                                                 start_value=self.font_manager.ui_normal_font_size_value,
                                                                                 value_range=(5, 21),
                                                                                 container=self,
                                                                                 manager=self.manager)

        self.ui_title_font_size_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((365, 260), (160, 40)),
                                                                     text="UI Title Font Size",
                                                                     container=self,
                                                                     manager=self.manager)

        self.ui_title_font_size_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((340, 300), (210, 27)),
                                                                                start_value=self.font_manager.ui_title_font_size_value,
                                                                                value_range=(5, 35),
                                                                                container=self,
                                                                                manager=self.manager)

        self.ui_font_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((80, 340), (160, 40)),
                                                         text="UI Font",
                                                         container=self,
                                                         manager=self.manager)

        font_name_list = self.font_manager.get_ui_font_names()
        font_name_list.append('Create Custom Font')
        if self.font_manager.custom_ui_fonts_exist():
            font_name_list.append('Delete Custom Font')

        self.ui_font_drop_down_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((80, 380), (160, 40)),
                                                                         options_list=font_name_list,
                                                                         starting_option=self.font_manager.current_font_name,
                                                                         container=self,
                                                                         manager=self.manager)

        self.ui_disable_tutorial_on_startup_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, 340), (200, 40)),
                                                                                text="Disable Tutorial On Startup",
                                                                                container=self,
                                                                                manager=self.manager)

        if self.user_settings_json_data['disable_tutorial_on_startup']:
            startup_button_icon = '╳'
        else:
            startup_button_icon = ''

        self.ui_disable_tutorial_on_startup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((420, 380), (45, 40)),
                                                                                  text=startup_button_icon,
                                                                                  container=self,
                                                                                  object_id="#tutorial_button",
                                                                                  manager=self.manager)

        self.ui_reset_settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((80, 450), (200, 50)),
                                                                     text='Reset',
                                                                     container=self,
                                                                     manager=self.manager)

        self.ui_save_settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 450), (200, 50)),
                                                                    text='Save',
                                                                    container=self,
                                                                    manager=self.manager)

        self.handle_settings_window_border_width_changed()

    def clean_settings_window(self):
        """
        Removes the widgets for SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN.
        """
        self.stage = None
        self.welcome_to_settings_text_box.kill()
        self.ui_element_shape_label.kill()
        self.ui_element_shape_drop_down_menu.kill()
        self.ui_corner_roundness_label.kill()
        self.ui_corner_roundness_slider.kill()
        self.grid_width_label.kill()
        self.grid_width_slider.kill()
        self.ui_border_width_label.kill()
        self.ui_border_width_slider.kill()
        self.ui_normal_font_size_label.kill()
        self.ui_normal_font_size_slider.kill()
        self.ui_title_font_size_label.kill()
        self.ui_title_font_size_slider.kill()
        self.ui_font_label.kill()
        self.ui_font_drop_down_menu.kill()
        self.ui_disable_tutorial_on_startup_label.kill()
        self.ui_disable_tutorial_on_startup_button.kill()
        self.ui_reset_settings_button.kill()
        self.ui_save_settings_button.kill()

    def build_custom_font_creation_window(self):
        """
        Creates the widgets for SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN.
        """
        self.stage = SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN

        self.welcome_to_font_creation_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, -5), (self.window_width - 180, 80)),
                                                                               html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Custom Font Creation</var></font>",
                                                                               object_id="#text_box_title",
                                                                               container=self,
                                                                               manager=self.manager)

        self.previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (50, 30)),
                                                                 text='<-',
                                                                 container=self,
                                                                 manager=self.manager)

        self.custom_font_name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((210, 360), (200, 40)),
                                                                  text='Custom Font Name',
                                                                  container=self,
                                                                  manager=self.manager)

        self.custom_font_name_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((210, 400), (200, 50)),
                                                                                    container=self,
                                                                                    manager=self.manager)

        self.custom_font_ui_elements_dict = {'Normal Font File Path (Regular Weight)': None,
                                             'Normal Font File Path (Bold Weight)': None,
                                             'Title Font File Path (Regular Weight)': None
                                            }

        distance_x = 120
        distance_y = 70
        for custom_font_label_name in self.custom_font_ui_elements_dict:
            self.custom_font_ui_elements_dict[custom_font_label_name] = [pygame_gui.elements.UILabel(relative_rect=pygame.Rect((distance_x, distance_y), (380, 40)),
                                                                                                     text=custom_font_label_name,
                                                                                                     container=self,
                                                                                                     object_id='#label_left_horiz_alignment',
                                                                                                     manager=self.manager),
                                                                         pygame_gui.elements.UIButton(relative_rect=pygame.Rect((distance_x, distance_y+40), (100, 40)),
                                                                                                      text='Find File',
                                                                                                      container=self,
                                                                                                      manager=self.manager),
                                                                         pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((distance_x+120, distance_y+40), (280, 40)),
                                                                                                             container=self,
                                                                                                             manager=self.manager)]
            distance_y += 100

        self.custom_font_create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((210, 470), (200, 50)),
                                                                      text='Create Custom Font',
                                                                      container=self,
                                                                      manager=self.manager)

    def clean_custom_font_creation_window(self):
        """
        Removes the widgets for SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN.
        """
        self.stage = None
        self.welcome_to_font_creation_text_box.kill()
        self.previous_page_button.kill()
        self.custom_font_name_label.kill()
        self.custom_font_name_text_entry_line.kill()
        for ui_element_list in self.custom_font_ui_elements_dict.values():
            for ui_element in ui_element_list:
                ui_element.kill()

        self.custom_font_ui_elements_dict = None
        self.custom_font_create_button.kill()

    def build_custom_font_deletion_window(self):
        """
        Creates the widgets for SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN.
        """
        self.stage = SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN

        self.welcome_to_font_deletion_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, -5), (self.window_width - 180, 80)),
                                                                               html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Custom Font Deletion</var></font>",
                                                                               object_id="#text_box_title",
                                                                               container=self,
                                                                               manager=self.manager)

        self.previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (50, 30)),
                                                                 text='<-',
                                                                 container=self,
                                                                 manager=self.manager)

        self.custom_fonts_to_delete_names = []
        self.custom_font_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((180, 120), ((250, 250))),
                                                                              item_list=self.font_manager.get_custom_ui_font_names(),
                                                                              allow_multi_select=True,
                                                                              container=self,
                                                                              manager=self.manager)

        self.custom_font_delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((205, 390), (200, 50)),
                                                                      text='Delete',
                                                                      container=self,
                                                                      manager=self.manager)

    def clean_custom_font_deletion_window(self):
        """
        Removes the widgets for SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN.
        """
        self.stage = None
        self.welcome_to_font_deletion_text_box.kill()
        self.previous_page_button.kill()
        self.custom_font_selection_list.kill()
        self.custom_font_delete_button.kill()

    def handle_settings_window_ui_button_pressed_event(self, event):
        """
        Handles the pygame_gui.UI_BUTTON_PRESSED event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN:
                if event.ui_element == self.ui_save_settings_button:
                    print("[SETTINGS WINDOW] Saved current settings")
                    self.user_settings_json_data['ui_element_shape'] = self.ui_element_shape
                    self.user_settings_json_data['ui_corner_roundness_value'] = self.ui_corner_roundness_value
                    self.user_settings_json_data['ui_border_width_value'] = self.ui_border_width_value
                    self.user_settings_json_data['grid_width'] = self.grid.line_width
                    self.user_settings_json_data['ui_normal_font_size_value'] = self.font_manager.ui_normal_font_size_value
                    self.user_settings_json_data['ui_title_font_size_value'] = self.font_manager.ui_title_font_size_value
                    self.user_settings_json_data['current_font_name'] = self.font_manager.current_font_name
                    self.save_user_settings()

                elif event.ui_element == self.ui_reset_settings_button:
                    print("[SETTINGS WINDOW] Reset user settings")

                    with open('data/settings/user_settings.json', 'w') as file:
                        with open('data/settings/default_user_settings.json') as default_user_settings_file:
                            file.write(default_user_settings_file.read())

                    self.load_user_settings()
                    self.clean_settings_window()
                    self.build_settings_window()

                elif event.ui_element == self.ui_disable_tutorial_on_startup_button:
                    if self.user_settings_json_data['disable_tutorial_on_startup']:
                        self.set_disable_tutorial_window_on_startup(False)
                        self.ui_disable_tutorial_on_startup_button.set_text('')
                        print("[SETTINGS WINDOW] User enabled the tutorial window to appear on startup.")
                    else:
                        self.set_disable_tutorial_window_on_startup(True)
                        self.ui_disable_tutorial_on_startup_button.set_text('╳')
                        print("[SETTINGS WINDOW] User disabled the tutorial window from appearing on startup.")



            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN:
                if event.ui_element == self.previous_page_button:
                    self.clean_custom_font_creation_window()
                    self.build_settings_window()

                elif event.ui_element == self.custom_font_create_button:
                    custom_font_name = self.custom_font_name_text_entry_line.get_text()
                    if custom_font_name == '' or custom_font_name == 'A custom font already exists with this name.':
                        self.custom_font_name_text_entry_line.set_text("Please pick a valid custom font name.")
                        return

                    exit = False
                    if self.custom_normal_font_regular_weight_file_path_string == None:
                        self.custom_font_ui_elements_dict[list(self.custom_font_ui_elements_dict)[0]][2].set_text("Please pick a valid font file")
                        exit = True

                    if self.custom_normal_font_bold_weight_file_path_string == None:
                        self.custom_font_ui_elements_dict[list(self.custom_font_ui_elements_dict)[1]][2].set_text("Please pick a valid font file")
                        exit = True

                    if self.custom_title_font_regular_weight_file_path_string == None:
                        self.custom_font_ui_elements_dict[list(self.custom_font_ui_elements_dict)[2]][2].set_text("Please pick a valid font file")
                        exit = True

                    if exit:
                        return

                    self.font_manager.add_ui_font(custom_font_name, self.custom_normal_font_regular_weight_file_path_string, self.custom_normal_font_bold_weight_file_path_string, self.custom_title_font_regular_weight_file_path_string)
                    self.font_manager.set_current_font(custom_font_name)

                    self.custom_normal_font_regular_weight_file_path_string = None
                    self.custom_normal_font_bold_weight_file_path_string = None
                    self.custom_title_font_regular_weight_file_path_string = None
                    self.clean_custom_font_creation_window()
                    self.build_settings_window()
                else:
                    for custom_font_label_name in self.custom_font_ui_elements_dict:
                        for ui_element in self.custom_font_ui_elements_dict[custom_font_label_name]:
                            if event.ui_element == ui_element:
                                self.custom_font_label_name_for_file_path_dialog = custom_font_label_name
                                self.custom_font_file_path_dialog = pygame_gui.windows.UIFileDialog(rect=pygame.Rect((200, 100), (600, 500)),
                                                                                                    window_title="Find File",
                                                                                                    initial_file_path=os.path.expanduser('~'),
                                                                                                    object_id='#custom_file_display_list',
                                                                                                    manager=self.manager)
                                return

            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN:
                if event.ui_element == self.previous_page_button:
                    self.clean_custom_font_deletion_window()
                    self.build_settings_window()

                elif event.ui_element == self.custom_font_delete_button:
                    if self.font_manager.current_font_name in self.custom_fonts_to_delete_names:
                        self.font_manager.set_current_font("Roboto")

                    for font in self.custom_fonts_to_delete_names:
                        self.font_manager.delete_custom_ui_font(font)

                    self.custom_fonts_to_delete_names = []
                    self.clean_custom_font_deletion_window()
                    self.build_settings_window()

    def handle_settings_window_ui_drop_down_menu_changed_event(self, event):
        """
        Handles the pygame_gui.UI_DROP_DOWN_MENU_CHANGED event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN:
                if event.ui_element == self.ui_element_shape_drop_down_menu:
                    match event.text:
                        case 'Rectangle':
                            self.ui_element_shape = 'Rectangle'
                            self.ui_corner_roundness_slider.disable()
                            self.theme_json_data['#ui_element_shape']['misc']['shape'] = 'rectangle'
                            self.theme_json_data['horizontal_slider.#right_button']['misc']['shape'] = 'rectangle'
                            self.theme_json_data['horizontal_slider.#left_button']['misc']['shape'] = 'rectangle'
                            self.theme_manager.update_theming(json.dumps(self.theme_json_data))
                        case 'Rounded Rectangle':
                            self.ui_element_shape = 'Rounded Rectangle'
                            self.ui_corner_roundness_slider.enable()
                            self.theme_json_data['#ui_element_shape']['misc']['shape'] = 'rounded_rectangle'
                            self.theme_manager.update_theming(json.dumps(self.theme_json_data))

                if event.ui_element == self.ui_font_drop_down_menu:
                    match event.text:
                        case 'Create Custom Font':
                            self.clean_settings_window()
                            self.build_custom_font_creation_window()
                        case 'Delete Custom Font':
                            self.clean_settings_window()
                            self.build_custom_font_deletion_window()
                        case _:
                            self.font_manager.set_current_font(event.text)
                            self.welcome_to_settings_text_box.kill()
                            self.welcome_to_settings_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, -5), (self.window_width - 180, 70)),
                                                                                              html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Settings</var></font>",
                                                                                              object_id="#text_box_title",
                                                                                              container=self,
                                                                                              manager=self.manager)

    def handle_settings_window_ui_horizontal_slider_moved_event(self, event):
        """
        Handles the pygame_gui.UI_HORIZONTAL_SLIDER_MOVED event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_SETTINGS_SCREEN:
                if event.ui_element == self.ui_corner_roundness_slider:
                    self.ui_corner_roundness_value = event.value
                    self.handle_settings_window_ui_corner_roundness_changed()

                elif event.ui_element == self.grid_width_slider:
                    self.grid.line_width = event.value

                elif event.ui_element == self.ui_border_width_slider:
                    if self.ui_border_width_value != event.value:
                        self.ui_border_width_value = event.value
                        self.handle_settings_window_border_width_changed()

                elif event.ui_element == self.ui_normal_font_size_slider:
                    self.font_manager.set_normal_font_size(event.value)

                elif event.ui_element == self.ui_title_font_size_slider:
                    self.font_manager.ui_title_font_size_value = event.value
                    self.welcome_to_settings_text_box.kill()
                    self.welcome_to_settings_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, -5), (self.window_width - 180, 70)),
                                                                                      html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Settings</var></font>",
                                                                                      object_id="#text_box_title",
                                                                                      container=self,
                                                                                      manager=self.manager)

    def handle_settings_window_ui_file_dialog_path_picked_event(self, event):
        """
        Handles the pygame_gui.UI_FILE_DIALOG_PATH_PICKED event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN:
                if event.ui_element == self.custom_font_file_path_dialog:
                    if len(event.text) > 3 and event.text[-3:] in ['ttf', 'otf']:
                        match self.custom_font_label_name_for_file_path_dialog:
                            case 'Normal Font File Path (Regular Weight)':
                                self.custom_normal_font_regular_weight_file_path_string = event.text
                            case 'Normal Font File Path (Bold Weight)':
                                self.custom_normal_font_bold_weight_file_path_string = event.text
                            case 'Title Font File Path (Regular Weight)':
                                self.custom_title_font_regular_weight_file_path_string = event.text

                        self.custom_font_ui_elements_dict[self.custom_font_label_name_for_file_path_dialog][2].set_text(event.text)
                    else:
                        match self.custom_font_label_name_for_file_path_dialog:
                            case 'Normal Font File Path (Regular Weight)':
                                self.custom_normal_font_regular_weight_file_path_string = None
                            case 'Normal Font File Path (Bold Weight)':
                                self.custom_normal_font_bold_weight_file_path_string = None
                            case 'Title Font File Path (Regular Weight)':
                                self.custom_title_font_regular_weight_file_path_string = None

                        self.custom_font_ui_elements_dict[self.custom_font_label_name_for_file_path_dialog][2].set_text("Invalid font file type (must be .ttf or .otf)")

                    self.custom_font_label_name_for_file_path_dialog = None
                    print("[CURRENT FILE PATHS]:", self.custom_normal_font_regular_weight_file_path_string, self.custom_normal_font_bold_weight_file_path_string, self.custom_title_font_regular_weight_file_path_string)

    def handle_settings_window_ui_text_entry_finished_event(self, event):
        """
        Handles the pygame_gui.UI_TEXT_ENTRY_FINISHED event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN:
                if event.ui_element == self.custom_font_name_text_entry_line:
                    if event.text in self.font_manager.get_ui_font_names():
                        self.custom_font_name_text_entry_line.set_text("A custom font already exists with this name.")

    def handle_settings_window_ui_selection_list_new_selection(self, event):
        """
        Handles the pygame_gui.UI_SELECTION_LIST_NEW_SELECTION event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN:
                if event.ui_element == self.custom_font_selection_list:
                    self.custom_fonts_to_delete_names.append(event.text)
                    print(self.custom_fonts_to_delete_names)

    def handle_settings_window_ui_selection_list_dropped_selection(self, event):
        """
        Handles the pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION event for SettingsWindow.

        @param event: pygame.event
        """
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN:
                if event.ui_element == self.custom_font_selection_list:
                    self.custom_fonts_to_delete_names.remove(event.text)
                    print(self.custom_fonts_to_delete_names)

    def shutdown(self):
        """
        Sets the window_running attribute to False.
        """
        print("[SETTINGS WINDOW] Shutdown Settings Window")
        self.window_running = False

class GameUIStates(IntEnum):
    UI_NORMAL_STATE = 0,
    UI_RUNNING_PATHFINDING_ALGORITHM_STATE = 1,
    UI_RUNNING_RECURSIVE_DIVISION_STATE = 2

class GameUIManager:
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager, grid, client, server, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict):
        """
        Initializes the GameUIManager class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        @param grid: Grid
        @param client: Client
        @param server: Server
        @param pathfinding_algorithms_dict: Dict
        @param maze_generation_algorithms_dict: Dict
        @param events_dict: Dict
        """
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.color_manager: ColorManager = color_manager
        self.animation_manager: AnimationManager = animation_manager
        self.grid = grid
        self.client = client
        self.server = server
        self.pathfinding_algorithms_dict = pathfinding_algorithms_dict
        self.maze_generation_algorithms_dict = maze_generation_algorithms_dict
        self.events_dict = events_dict
        self.state = GameUIStates.UI_NORMAL_STATE

        self.manager = pygame_gui.UIManager((screen_manager.screen_width, screen_manager.screen_height))
        self.theme_manager = self.manager.get_theme()

        with open("data/ui_themes/ui_theme.json", "r") as file:
            file_data = file.read()
            self.theme_json_data = json.loads(file_data)

        self.font_manager = FontManager(self.manager, self.theme_manager, self.theme_json_data)
        self.font_manager.load_ui_fonts()
        self.theme_manager.load_theme('data/ui_themes/ui_theme.json')

        self.ui_node_type_and_theme_property_path_dict = {
            ColorUITypes.UI_BACKGROUND_COLOR: 'defaults/colours/normal_bg',
            ColorUITypes.UI_HOVERED_BACKGROUND_COLOR: 'defaults/colours/hovered_bg',
            ColorUITypes.UI_DISABLED_BACKGROUND_COLOR: 'defaults/colours/disabled_bg',
            ColorUITypes.UI_PRESSED_BACKGROUND_COLOR: 'defaults/colours/active_bg',
            ColorUITypes.UI_BORDER_COLOR: 'defaults/colours/normal_border',
            ColorUITypes.UI_HOVERED_BORDER_COLOR: 'defaults/colours/hovered_border',
            ColorUITypes.UI_DISABLED_BORDER_COLOR: 'defaults/colours/disabled_border',
            ColorUITypes.UI_PRESSED_BORDER_COLOR: 'defaults/colours/active_border',
            ColorUITypes.UI_SELECTED_COLOR: 'defaults/colours/selected_bg',
            ColorUITypes.UI_WINDOW_BACKGROUND_COLOR: 'window/colours/dark_bg',
            ColorUITypes.UI_TEXT_ENTRY_LINE_BORDER_COLOR: 'text_entry_line/colours/normal_border',
            ColorUITypes.UI_TEXT_COLOR: 'defaults/colours/normal_text',
            ColorUITypes.UI_TEXT_HOVERED_COLOR: 'defaults/colours/hovered_text',
            ColorUITypes.UI_TEXT_PRESSED_COLOR: 'defaults/colours/active_text',
            ColorUITypes.UI_TEXT_SELECTED_FOREGROUND_COLOR: 'defaults/colours/selected_text',
            ColorUITypes.UI_TEXT_SELECTED_BACKGROUND_COLOR: 'text_entry_line/colours/selected_bg',
            ColorUITypes.UI_TEXT_DISABLED_COLOR: 'defaults/colours/disabled_text',
            ColorUITypes.UI_TITLE_TEXT_COLOR: '#text_box_title/colours/normal_text'
        }

        self.set_ui_colours_from_current_theme()

        self.run_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((810, 130), (180, 50)), text="Run", manager=self.manager)

        self.pathfinding_algorithms_options = ['Depth First Search', 'Breadth First Search', 'Dijkstra', 'A*', 'Greedy Best First Search', 'Bidirectional Best First Search']
        self.pathfinding_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 10), (200, 50)),
                                                                              options_list=self.pathfinding_algorithms_options,
                                                                              starting_option="A*",
                                                                              manager=self.manager)

        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 10), (200, 50)),
                                                                  options_list=['Manhattan Distance', 'Euclidean Distance'],
                                                                  starting_option='Manhattan Distance',
                                                                  manager=self.manager)

        self.maze_generation_algorithms_options = ['Random Maze', 'Random Weighted Maze', 'RD(Recursive Division)', 'RD Horizontal Skew', 'RD Vertical Skew']
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((440, 10), (200, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option='Random Maze',
                                                                                  manager=self.manager)

        self.resolution_divider_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 65), (250, 30)),
                                                                    text='Grid Size',
                                                                    manager=self.manager)

        self.resolution_divider_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 92), (320, 27)),
                                                                                start_value=4,
                                                                                value_range=(1, 8),
                                                                                manager=self.manager)

        self.pathfinding_algorithm_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((400, 65), (280, 30)),
                                                                             text='Pathfinding Algorithm Speed',
                                                                             manager=self.manager)

        self.pathfinding_algorithm_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((380, 92), (320, 27)),
                                                                                         start_value=25,
                                                                                         value_range=(12, 100),
                                                                                         manager=self.manager)

        self.recursive_division_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((775, 65), (250, 30)),
                                                                          text='Recursive Division Speed',
                                                                          manager=self.manager)

        self.recursive_division_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((740, 92), (320, 27)),
                                                                                      start_value=15,
                                                                                      value_range=(10, 50),
                                                                                      manager=self.manager)

        self.marked_or_weighted_node_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 130), (200, 50)),
                                                                              options_list=['Marked', 'Weighted'],
                                                                              starting_option='Marked',
                                                                              manager=self.manager)

        self.weighted_node_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((230, 130), (150, 50)),
                                                                                 manager=self.manager)

        self.clear_node_types = ['Clear Grid', 'Clear Path', 'Clear Checked Nodes', 'Clear Marked Nodes', 'Clear Weighted Nodes']
        self.clear_nodes_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((390, 130), (200, 50)),
                                                                   options_list=self.clear_node_types,
                                                                   starting_option='Clear Grid',
                                                                   manager=self.manager)

        self.tutorial_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 130), (60, 50)),
                                                            text='?',
                                                            manager=self.manager)

        self.settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((860, 10), (200, 50)),
                                                            text='Settings',
                                                            manager=self.manager)

        self.settings_window = SettingsWindow(self.manager, self.theme_manager, self.theme_json_data, self.grid, self.font_manager)
        self.tutorial_window = TutorialWindow(self.manager, self.color_manager, self.font_manager, self.settings_window)

        self.theme_menu = None
        self.generate_theme_menu('Dark Theme')
        self.theme_window = ThemeWindow(self.manager, self.color_manager, self.font_manager)
        self.ui_networking_manager = UINetworkingManager(self.manager, self.client, self.server, self.font_manager)
        self.generate_networking_menu(kill_networking_menu=False)

        self.weighted_node_text_entry_line.set_text_length_limit(10)
        self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
        self.weighted_node_text_entry_line.disable()
        self.weighted_node_text_entry_line.set_text('      None')

        self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.ASTAR
        self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].heuristic = self.heuristic
        self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE
        self.recursive_division_skew = None
        self.pathfinding_algorithm_speed = 25
        self.recursive_division_speed = 15
        self.cursor_node_type = CursorNodeTypes.MARKED_NODE
        self.weight = 1

        if self.settings_window.should_build_tutorial_window_on_startup():
            print("[UI MANAGER] Building tutorial window.")
            self.tutorial_window.build_tutorial_welcome_screen()

    def generate_theme_menu(self, theme=None, kill_theme_menu=False):
        """
        If the theme variable given is set to None we will set the theme
        variable to be equal the current_theme_name attribute in self.color_manager.
        After this we will check if the kill_theme_menu variable given is set to True
        if it is we will destroy the current theme menu. After this we will create a
        new theme menu.

        @param theme: Str or None
        @param kill_theme_menu: Bool
        """
        if theme == None:
            theme = self.color_manager.current_theme_name

        if kill_theme_menu:
            if self.theme_menu != None:
                self.theme_menu.kill()

        theme_menu_options = self.color_manager.get_all_theme_names_from_themes_list()
        theme_menu_options.append('Create Custom Theme')

        if self.color_manager.do_custom_themes_exists():
            theme_menu_options.append('Edit Custom Theme')
            theme_menu_options.append('Delete Custom Theme')

        if self.client.connected_to_server:
            theme_menu_options.append('Send Theme To Clients')

        self.theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((600, 130), (200, 50)),
                                                             options_list=theme_menu_options,
                                                             starting_option=theme,
                                                             manager=self.manager)

    def generate_networking_menu(self, kill_networking_menu=True):
        """
        This function will first check if the kill_networking_menu variable given is set to True
        if it is we will destroy the current networking menu. After this we will create a new
        networking menu.

        @param kill_networking_menu: bool
        """
        if kill_networking_menu:
            self.networking_menu.kill()

        if self.ui_networking_manager.created_server == False and self.ui_networking_manager.connected_to_server == False:
            options = ['Create Server', 'Connect to Server']
        elif self.ui_networking_manager.created_server and self.ui_networking_manager.connected_to_server == False:
            options = ['Show Server Info', 'Destroy Server']
        elif self.ui_networking_manager.created_server == False and self.ui_networking_manager.connected_to_server:
            options = ['Disconnect from Server']

        self.networking_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((650, 10), (200, 50)),
                                                                  options_list=options,
                                                                  starting_option=options[0],
                                                                  manager=self.manager)



    def run_pathfinding_algorithm(self, pathfinding_algorithm, heuristic=None):
        """
        This function will be used to run a pathfinding algorithm, and it will
        do the following things in the order given:

        1) Run the reset_rect_array_adjacent_nodes method in self.rect_array_obj.
        2) Run the gen_rect_array_with_adjacent_nodes method in self.rect_array_obj.
        3) Run the reset_non_user_weights method in self.rect_array_obj.
        4) Run the reset_path_pointer method in pathfinding_algorithm.
        5) Run the reset_checked_nodes_pointer method in pathfinding_algorithm.
        6) Run the reset_animated_checked_coords_stack method in pathfinding_algorithm.
        7) Run the reset_animated_path_coords_stack method in pathfinding_algorithm.
        8) Set the heuristic attribute in pathfinding_algorithm to be the same as the heuristic given.
        9) Run the run method in pathfinding_algorithm.

        @param pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        @param heuristic: PathfindingHeuristics
        """
        self.rect_array_obj.reset_rect_array_adjacent_nodes()
        self.rect_array_obj.gen_rect_array_with_adjacent_nodes()
        self.rect_array_obj.reset_non_user_weights()

        pathfinding_algorithm.reset_path_pointer()
        pathfinding_algorithm.reset_checked_nodes_pointer()

        pathfinding_algorithm.reset_animated_checked_coords_stack()
        pathfinding_algorithm.reset_animated_path_coords_stack()

        print("Current pathfinding heuristic:", heuristic)
        pathfinding_algorithm.heuristic = heuristic
        pathfinding_algorithm.run()


    def create_empty_heuristics_menu(self):
        """
        This function will first destroy the current heuristics menu, and it will
        set the heuristic attribute to None. After this it will create a new heuristics
        menu.
        """
        self.heuristics_menu.kill()
        self.heuristic = None
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 10), (200, 50)),
                                                                  options_list=['None'],
                                                                  starting_option='None',
                                                                  manager=self.manager)
        self.heuristics_menu.disable()

    def create_heuristics_menu_with_distances(self, starting_value='Manhattan Distance'):
        """
        This function will first destroy the current heuristics menu. After this it will check
        if the starting_value given is equal to the string 'Manhattan Distance' or 'Euclidean Distance'
        and it will set the heuristic attribute to be PathfindingHeuristics.MANHATTAN_DISTANCE or
        PathfindingHeuristics.EUCLIDEAN_DISTANCE accordingly. After this we will create a new heuristics menu
        with the new value of the heuristics attribute.

        @param starting_value: Str
        """
        self.heuristics_menu.kill()
        if starting_value == 'Manhattan Distance':
            self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        else:
            self.heuristic = PathfindingHeuristics.EUCLIDEAN_DISTANCE

        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 10), (200, 50)),
                                                                  options_list=['Manhattan Distance', 'Euclidean Distance'],
                                                                  starting_option=starting_value,
                                                                  manager=self.manager)

    def run_current_maze_generation_algorithm(self):
        """
        This function will first run the reset_path_pointer and reset_checked_nodes_pointer
        methods on the current pathfinding algorithm (we can access the current pathfinding algorithm
        by accessing the object stored as the value of the key which is self.current_pathfinding_algorithm in
        the pathfinding_algorithms_dict dictionary). We will also run the reset_maze_pointer method on the
        current maze generation algorithm (we can also access the current maze generation algorithm by accessing
        the object stored as the value of the key which is self.current_maze_generation_algorithm in the
        maze_generation_algorithms_dict dictionary). After this we will run the maze generation algorithm specified
        by self.current_maze_generation_algorithm.
        """
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()

        self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()

        match self.current_maze_generation_algorithm:
            case MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE:
                self.grid.reset_marked_nodes(False)
                self.grid.reset_all_weights(False)
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].create_random_marked_maze()
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

            case MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE:
                self.grid.reset_marked_nodes(False)
                self.grid.reset_all_weights(False)
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].create_random_weighted_maze()
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

            case MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION:
                self.grid.reset_marked_nodes()
                self.grid.reset_all_weights()

                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_animated_coords_stack()
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].skew = self.recursive_division_skew
                self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].run_recursive_division()

                pygame.time.set_timer(self.events_dict['DRAW_MAZE'], self.recursive_division_speed)
                self.build_ui_running_recursive_division_state()
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.recursive_division_skew, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

    def get_current_pathfinding_algorithm(self):
        """
        This function will return the pathfinding algorithm object which is stored as the value of
        the key self.current_pathfinding_algorithm in the pathfinding_algorithms_dict dictionary.

        @return: An instance of a child class of the PathfindingAlgorithm class.
        """
        return self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm]

    def update_current_pathfinding_algorithm(self, pathfinding_algorithm, heuristic, is_server_event=False):
        """
        This function will set the current_pathfinding_algorithm attribute to be equal to the pathfinding_algorithm
        given. This function will then destroy the current pathfinding algorithms menu and the heuristics menu
        and create a new pathfinding algorithms menu and heuristics menu depending upon the pathfinding_algorithm and
        heuristic given. After this we will check if the is_server_event variable given is set to True. If it
        is we will run the build_ui_running_pathfinding_algorithm_state method.

        @param pathfinding_algorithm: An instance of a child class of the PathfindingAlgorithm class.
        @param heuristic: PathfindingHeuristics
        @param is_server_event: bool
        """
        self.current_pathfinding_algorithm = pathfinding_algorithm
        match self.current_pathfinding_algorithm:
            case PathfindingAlgorithmTypes.DFS:
                starting_option = 'Depth First Search'
            case PathfindingAlgorithmTypes.BFS:
                starting_option = 'Breadth First Search'
            case PathfindingAlgorithmTypes.DIJKASTRA:
                starting_option = 'Dijkstra'
            case PathfindingAlgorithmTypes.ASTAR:
                starting_option = 'A*'
            case PathfindingAlgorithmTypes.GREEDY_BFS:
                starting_option = 'Greedy Best First Search'
            case PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS:
                starting_option = 'Bidirectional Best First Search'

        self.pathfinding_algorithms_menu.kill()
        self.pathfinding_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 10), (200, 50)),
                                                                              options_list=self.pathfinding_algorithms_options,
                                                                              starting_option=starting_option,
                                                                              manager=self.manager)

        if heuristic == None:
            self.create_empty_heuristics_menu()
        else:
            self.heuristic = heuristic
            match self.heuristic:
                case PathfindingHeuristics.EUCLIDEAN_DISTANCE:
                    self.create_heuristics_menu_with_distances('Euclidean Distance')
                case PathfindingHeuristics.MANHATTAN_DISTANCE:
                    self.create_heuristics_menu_with_distances()

        if is_server_event:
            self.build_ui_running_pathfinding_algorithm_state()

    def get_current_maze_generation_algorithm(self):
        """
        This function will return the maze geneartion algorithm object which is stored as the value of
        the key self.current_maze_generation_algorithm in the maze_generation_algorithms_dict dictionary.

        @return: An instance of a child class of the MazeGenerationAlgorithm class.
        """
        return self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm]

    def update_current_maze_generation_algorithm(self, maze_generation_algorithm, is_server_event=False):
        """
        This function will set the current_maze_generation_algorithm attribute to the maze_generation_algorithm
        given. After this we will destroy the maze generation algorithm menu and create a new one. We will also
        run the build_ui_running_recursive_division_state method if the is_server_event variable given is set to
        True and the maze_generation_algorithm given is set to be MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION.

        @param maze_generation_algorithm: An instance of a child class of the MazeGenerationAlgorithm class.
        @param is_server_event: bool
        """
        self.current_maze_generation_algorithm = maze_generation_algorithm
        match self.current_maze_generation_algorithm:
            case MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE:
                starting_value = 'Random Maze'
            case MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE:
                starting_value = 'Random Weighted Maze'
            case MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION:
                skew = self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].skew

                if skew == None:
                    starting_value = 'RD(Recursive Division)'
                elif skew == RecursiveDivisionSkew.HORIZONTAL:
                    starting_value = 'RD Horizontal Skew'
                elif skew == RecursiveDivisionSkew.VERTICAL:
                    starting_value = 'RD Vertical Skew'

                if is_server_event:
                    self.build_ui_running_recursive_division_state()

        self.maze_generation_algorithms_menu.kill()
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((440, 10), (200, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option=starting_value,
                                                                                  manager=self.manager)
    def update_resolution_divider(self):
        """
        This function will set the value of the resolution divider slider to be the same as the
        resolution_divider attribute in self.screen_manager.
        """
        self.resolution_divider_slider.set_current_value(self.screen_manager.resolution_divider)

    def get_pathfinding_algorithm_speed(self):
        """
        Getter for the pathfinding_algorithm_speed attribute.

        @return: int
        """
        return self.pathfinding_algorithm_speed

    def get_recursive_division_speed(self):
        """
        Getter for the recursive_division_speed attribute.

        @return: int
        """
        return self.recursive_division_speed

    def get_cursor_node_type(self):
        """
        Getter for the cursor_node_type attribute.

        @return: CursorNodeTypes
        """
        return self.cursor_node_type

    def get_weight(self):
        """
        Getter for the weight attribute.

        @return: int
        """
        return self.weight

    def update_pathfinding_algorithm_speed(self, pathfinding_algorithm_speed):
        """
        This function will set the value of self.pathfinding_algorithm_speed to
        the pathfinding_algorithm_speed given and also set the value of the
        pathfinding algorithm speed slider to be the same as the pathfinding_algorithm_speed
        given.

        @param pathfinding_algorithm_speed: int
        """
        self.pathfinding_algorithm_speed = pathfinding_algorithm_speed
        self.pathfinding_algorithm_speed_slider.set_current_value(self.pathfinding_algorithm_speed)

    def update_recursive_division_speed(self, recursive_division_speed):
        """
        This function will set the value of self.recursive_division_speed to
        the recursive_division_speed given and also set the value of the
        recursive division speed slider to be the same as the recursive_division_speed
        given.
        
        @param recursive_division_speed: int
        """
        self.recursive_division_speed = recursive_division_speed
        self.recursive_division_speed_slider.set_current_value(self.recursive_division_speed)

    def handle_ui_drop_down_menu_changed_event(self, event):
        """
        This function handles the pygame_gui.UI_DROP_DOWN_MENU_CHANGED event
        for the GameUIManager, ThemeWindow and SettingsWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_drop_down_menu_changed_event(event)
        self.settings_window.handle_settings_window_ui_drop_down_menu_changed_event(event)
        if event.ui_element == self.pathfinding_algorithms_menu:
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()

            match event.text:
                case 'Depth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DFS
                    self.create_empty_heuristics_menu()
                case 'Breadth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.BFS
                    self.create_empty_heuristics_menu()
                case 'Dijkstra':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DIJKASTRA
                    self.create_empty_heuristics_menu()
                case 'A*':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.ASTAR
                    self.create_heuristics_menu_with_distances()
                case 'Greedy Best First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.GREEDY_BFS
                    self.create_heuristics_menu_with_distances()
                case 'Bidirectional Best First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.BIDIRECTIONAL_BFS
                    self.create_empty_heuristics_menu()

        if event.ui_element == self.heuristics_menu:
            match event.text:
                case 'Manhattan Distance':
                    self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
                case 'Euclidean Distance':
                    self.heuristic = PathfindingHeuristics.EUCLIDEAN_DISTANCE

        if event.ui_element == self.maze_generation_algorithms_menu:
            match event.text:
                case 'Random Maze':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE
                    self.run_current_maze_generation_algorithm()
                case 'Random Weighted Maze':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE
                    self.run_current_maze_generation_algorithm()
                case 'RD(Recursive Division)':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = None
                    self.run_current_maze_generation_algorithm()
                case 'RD Horizontal Skew':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = RecursiveDivisionSkew.HORIZONTAL
                    self.run_current_maze_generation_algorithm()
                case 'RD Vertical Skew':
                    self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION
                    self.recursive_division_skew = RecursiveDivisionSkew.VERTICAL
                    self.run_current_maze_generation_algorithm()

        if event.ui_element == self.marked_or_weighted_node_menu:
            match event.text:
                case 'Marked':
                    self.cursor_node_type = CursorNodeTypes.MARKED_NODE
                    self.weighted_node_text_entry_line.disable()
                    self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
                    self.weighted_node_text_entry_line.set_text('   None')
                case 'Weighted':
                    self.cursor_node_type = CursorNodeTypes.WEIGHTED_NODE
                    self.weighted_node_text_entry_line.enable()
                    self.weighted_node_text_entry_line.set_allowed_characters('numbers')
                    self.weighted_node_text_entry_line.set_text('1')
                    self.weight = 1

        if event.ui_element == self.clear_nodes_menu:
            match event.text:
                case 'Clear Grid':
                    self.grid.reset_marked_nodes()
                    self.grid.reset_all_weights()

                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()

                    self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()

                    self.client.create_network_event(NetworkingEventTypes.CLEAR_GRID)
                case 'Clear Path':
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer(True)
                    self.client.create_network_event(NetworkingEventTypes.CLEAR_PATH)
                case 'Clear Checked Nodes':
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer(True)
                    self.client.create_network_event(NetworkingEventTypes.CLEAR_CHECKED_NODES)
                case 'Clear Marked Nodes':
                    self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()
                    self.grid.reset_marked_nodes()
                    self.client.create_network_event(NetworkingEventTypes.CLEAR_MARKED_NODES)
                case 'Clear Weighted Nodes':
                    self.grid.reset_all_weights()
                    self.client.create_network_event(NetworkingEventTypes.CLEAR_WEIGHTED_NODES)

        if event.ui_element == self.theme_menu:
            match event.text:
                case 'Create Custom Theme':
                    self.theme_window.build_custom_theme_creation_welcome_screen()
                case 'Edit Custom Theme':
                    self.theme_window.build_custom_theme_editing_welcome_screen()
                case 'Delete Custom Theme':
                    self.theme_window.build_custom_theme_delete_screen()
                case 'Send Theme To Clients':
                    self.client.create_network_event(NetworkingEventTypes.SEND_THEME)
                    pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (650, 600)),
                                                       html_message=(f"Successfully sent the current theme {self.color_manager.current_theme_name}"
                                                                     f" to all the other clients in the server."),
                                                       manager=self.manager)
                case _:
                    theme = self.color_manager.get_theme_from_themes_list(event.text)
                    if theme != None:
                        self.color_manager.current_theme_name = event.text
                        if self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].checked_nodes.gen_copy_without_empty_values() != []:
                            pathfinding_algorithm = self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm]
                        else:
                            pathfinding_algorithm = None

                        self.color_manager.set_and_animate_theme_colors_dict(theme, pathfinding_algorithm)

        if event.ui_element == self.networking_menu:
            match event.text:
                case 'Create Server':
                    self.ui_networking_manager.create_server()
                    self.generate_networking_menu()
                    self.generate_theme_menu(kill_theme_menu=True)
                case 'Connect to Server':
                    self.ui_networking_manager.build_networking_connect_to_server_screen()
                case 'Show Server Info':
                    self.ui_networking_manager.show_server_info()
                    self.generate_networking_menu()
                case 'Destroy Server':
                    self.ui_networking_manager.destroy_server()
                    self.generate_networking_menu()
                    self.generate_theme_menu(kill_theme_menu=True)
                case 'Disconnect from Server':
                    self.ui_networking_manager.disconnect_from_server()
                    self.generate_networking_menu()
                    self.generate_theme_menu(kill_theme_menu=True)


    def cancel_pathfinding_algorithm(self):
        """
        This function will reset the path pointer and checked nodes pointer for the current
        pathfinding algorithm, as well as setting the timer for the DRAW_CHECKED_NODES and DRAW_PATH
        events to 0. The function will then run the build_ui_normal_state method.
        """
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
        pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], 0)
        pygame.time.set_timer(self.events_dict['DRAW_PATH'], 0)
        self.build_ui_normal_state()

    def cancel_recursive_division(self, cut_off_point=None):
        """
        This function will run the cut_maze method on the current maze generation algorithm and pass
        in the cut_off_point variable given. It will then set the timer for the DRAW_MAZE event to 0
        and then call the build_ui_normal_state method.

        @param cut_off_point: int or None
        """
        self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].cut_maze(cut_off_point)
        pygame.time.set_timer(self.events_dict['DRAW_MAZE'], 0)
        self.build_ui_normal_state()

    def handle_ui_button_pressed_event(self, event):
        """
        This function will handle the pygame_gui.UI_BUTTON_PRESSED_EVENT event for the
        GameUIManager, ThemeWindow, SettingsWindow and the TutorialWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_button_pressed_event(event)
        self.settings_window.handle_settings_window_ui_button_pressed_event(event)
        self.tutorial_window.handle_tutorial_window_ui_button_pressed(event)

        update_theme_menu = self.ui_networking_manager.handle_ui_networking_manager_ui_button_pressed_event(event)
        if update_theme_menu:
            self.generate_theme_menu(kill_theme_menu=True)

        if self.state == GameUIStates.UI_NORMAL_STATE:
            if event.ui_element == self.run_button:
                self.run_pathfinding_algorithm(self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm], self.heuristic)
                self.client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, self.current_pathfinding_algorithm, self.heuristic)

                pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], self.pathfinding_algorithm_speed)
                self.build_ui_running_pathfinding_algorithm_state()

        elif self.state == GameUIStates.UI_RUNNING_PATHFINDING_ALGORITHM_STATE:
            if event.ui_element == self.run_button:
                self.cancel_pathfinding_algorithm()
                self.client.create_network_event(NetworkingEventTypes.CANCEL_PATHFINDING_ALGORITHM)

        elif self.state == GameUIStates.UI_RUNNING_RECURSIVE_DIVISION_STATE:
            if event.ui_element == self.run_button:
                self.cancel_recursive_division()
                self.client.create_network_event(NetworkingEventTypes.CANCEL_RECURSIVE_DIVISION, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze_pointer)

        if event.ui_element == self.tutorial_button:
            self.tutorial_window.build_tutorial_welcome_screen()

        if event.ui_element == self.settings_button:
            self.settings_window.build_settings_window()

    def handle_ui_horizontal_slider_moved_event(self, event):
        """
        This function will handle the pygame_gui.UI_HORIZONTAL_SLIDER_MOVED event for the
        GameUIManager and the SettingsWindow.

        @param event: pygame.event
        """
        self.settings_window.handle_settings_window_ui_horizontal_slider_moved_event(event)
        if event.ui_element == self.resolution_divider_slider:
            self.screen_manager.set_resolution_divider(event.value)
            self.rect_array_obj.reset_rect_array()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
            self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()
            self.client.create_network_event(NetworkingEventTypes.SET_RESOLUTION_DIVIDER, event.value)

        if event.ui_element == self.pathfinding_algorithm_speed_slider:
            if event.value != self.pathfinding_algorithm_speed:
                self.pathfinding_algorithm_speed = event.value
                self.client.create_network_event(NetworkingEventTypes.SET_PATHFINDING_ALGORITHM_SPEED, self.pathfinding_algorithm_speed)

        if event.ui_element == self.recursive_division_speed_slider:
            if event.value != self.recursive_division_speed:
                self.recursive_division_speed = event.value
                self.client.create_network_event(NetworkingEventTypes.SET_RECURSIVE_DIVISION_SPEED, self.recursive_division_speed)

    def handle_ui_text_entry_finished_event(self, event):
        """
        This function will handle the pygame_gui.UI_TEXT_ENTRY_FINISHED event for the
        GameUIManager, ThemeWindow and the SettingsWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_text_entry_finished_event(event)
        self.settings_window.handle_settings_window_ui_text_entry_finished_event(event)
        if event.ui_element == self.weighted_node_text_entry_line:
            self.weight = int(event.text)

    def handle_ui_window_closed_event(self, event):
        """
        This function will handle the pygame_gui.UI_WINDOW_CLOSE event for the GameUIManager,
        ThemeWindow, UINetworkingManager, SettingsWindow and the TutorialWindow.

        @param event: pygame.event
        """
        if event.ui_element == self.theme_window:
            self.theme_window.shutdown()

            if self.theme_window.custom_theme_name != None and self.color_manager.check_custom_theme_exists(self.theme_window.custom_theme_name):
                self.generate_theme_menu(self.theme_window.custom_theme_name, True)
                self.color_manager.current_theme_name = self.theme_window.custom_theme_name
                self.theme_window.custom_theme_name = None

            elif self.theme_window.edited_custom_theme:
                self.generate_theme_menu(self.theme_window.custom_theme_to_edit_name, True)
                self.color_manager.current_theme_name = self.theme_window.custom_theme_to_edit_name
                self.theme_window.custom_theme_to_edit_name = None

            elif self.theme_window.deleted_themes:
                self.generate_theme_menu('Dark Theme', True)
                self.color_manager.current_theme_name = 'Dark Theme'
                self.theme_window.deleted_themes = False

        if event.ui_element == self.ui_networking_manager:
            if self.ui_networking_manager.connected_to_server:
                self.generate_networking_menu()

        if event.ui_element == self.tutorial_window:
            self.tutorial_window.shutdown()

        if event.ui_element == self.settings_window:
            self.settings_window.shutdown()

    def handle_ui_color_picker_color_picked_event(self, event):
        """
        This function will handle the pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED for the
        GameUIManager and the ThemeWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_color_picker_color_picked_event(event)

    def handle_ui_selection_list_new_selection(self, event):
        """
        This function will handle the pygame_gui.UI_SELECTION_LIST_NEW_SELECTION for the
        GameUIManager, ThemeWindow, and the SettingsWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_selection_list_new_selection(event)
        self.settings_window.handle_settings_window_ui_selection_list_new_selection(event)

    def handle_ui_selection_list_dropped_selection(self, event):
        """
        This function will handle the pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION for the
        GameUIManager, ThemeWindow and the SettingsWindow.

        @param event: pygame.event
        """
        self.theme_window.handle_theme_window_ui_selection_list_dropped_selection(event)
        self.settings_window.handle_settings_window_ui_selection_list_dropped_selection(event)

    def handle_ui_file_dialog_path_picked_event(self, event):
        """
        This function will handle the pygame_gui.UI_FILE_DIALOG_PATH_PICKED for the
        GameUIManager and the SettingsWindow.

        @param event: pygame.event
        """
        self.settings_window.handle_settings_window_ui_file_dialog_path_picked_event(event)

    def update_client_received_new_theme(self):
        """
        This function will first check if the received_new_theme attribute in self.client is equal
        to True, if it is we will set it to False then we will call the generate_theme_menu method
        and set the kill_theme_menu argument to True. We will then create a message window telling
        the user that another client in the server has sent them a new theme.
        """
        if self.client.received_new_theme:
            self.client.received_new_theme = False
            self.generate_theme_menu(kill_theme_menu=True)
            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (650, 600)),
                                               html_message=(f"A client has sent the theme {self.color_manager.current_theme_name} to you,"
                                                             f" and it has been set as the current theme."),
                                               manager=self.manager)

    def update_networking_server_connection_broken(self):
        """
        This function will first check if the server_connection_broken attribute in self.client is equal
        to True, if it is we will set it to False then we will call the server_connection_has_broken method
        in self.ui_networking_manager. We will then create the networking menu again using the generate_networking_menu
        method, and we will also create the theme menu again using the generate_theme_menu method with the kill_theme_menu
        argument being set to True.
        """
        if self.client.server_connection_broken:
            self.client.server_connection_broken = False
            self.ui_networking_manager.server_connection_has_broken()
            self.generate_networking_menu()
            self.generate_theme_menu(kill_theme_menu=True)

    def set_colour_to_ui_element(self, ui_node_type, colour, update_theme=True):
        """
        This function will set the colour of the ui_node_type specified to the colour
        specified. If the update_theme variable given is set to True we will also update
        these changes so that they can be seen in the UI.

        @param ui_node_type: ColorUITypes
        @param colour: Tuple
        @param update_theme: bool
        """
        if type(colour) == pygame.Color:
            color_string = 'rgb' + str(self.color_manager.extract_rgb_color_from_pygame_color(colour))
        else:
            color_string = 'rgb'+str(colour)

        color_key_path = self.ui_node_type_and_theme_property_path_dict[ui_node_type].split('/')
        theme_json_data_command = 'self.theme_json_data'
        for key in color_key_path:
            theme_json_data_command += f"['{key}']"

        theme_json_data_command += "="
        theme_json_data_command += f'"{color_string}"'
        exec(theme_json_data_command)

        if ui_node_type == ColorUITypes.UI_TEXT_COLOR:
            self.theme_json_data['defaults']['colours']['text_cursor'] = color_string
        elif ui_node_type == ColorUITypes.UI_BORDER_COLOR:
            self.theme_json_data['text_entry_line']['colours']['normal_border'] = color_string
        elif ui_node_type == ColorUITypes.UI_BACKGROUND_COLOR:
            self.theme_json_data['horizontal_slider']['colours']['dark_bg'] = color_string
            self.theme_json_data['selection_list']['colours']['dark_bg'] = color_string
            self.theme_json_data['text_entry_line']['colours']['dark_bg'] = color_string
            self.theme_json_data['vertical_scroll_bar']['colours']['dark_bg'] = color_string
            self.theme_json_data['text_box']['colours']['dark_bg'] = color_string
        elif ui_node_type == ColorUITypes.UI_DISABLED_BACKGROUND_COLOR:
            self.theme_json_data['defaults']['colours']['disabled_dark_bg'] = color_string
            self.theme_json_data['text_entry_line']['colours']['disabled_dark_bg'] = color_string

        if update_theme:
            self.theme_manager.update_theming(json.dumps(self.theme_json_data))

    def set_ui_colours_from_current_theme(self):
        """
        This function will go through each ui node type in ColorUITypes and call
        the set_colour_to_ui_element method on it, we will set the colour argument
        to be the colour in the theme for that ui node type (we can get this colour
        by using the get_theme_color method in self.color_manager and pass in
        the ui node type we are currently iterating over as the argument) and we will
        also set the update_theme argument to False.
        """
        theme_colors_dict = self.color_manager.get_theme_colors_dict()
        for ui_node_type in ColorUITypes:
            self.set_colour_to_ui_element(ui_node_type, self.color_manager.get_theme_color(ui_node_type), False)

        self.theme_manager.update_theming(json.dumps(self.theme_json_data))
        print(f"[SET_UI_COLOURS_FROM_CURRENT_THEME] Set UI Colours from theme: '{self.color_manager.current_theme_name}'")

    def handle_ui_colour_animations(self):
        """
        This function will first call the update_ui_element_interpolation_dict method in self.animation_manager
        and then iterate over each key-value pair in this dictionary (this key value pair will contain the ui node type
        and the colour of the ui node type). We will then call the set_colour_to_ui_element method and pass in the ui node type
        and colour. After this we will call the set_node_color method in self.color_manager and pass in the ui node type
        and the colour.
        """
        update_text_entry_line = False
        for ui_colour_to_update_dict in self.animation_manager.update_ui_element_interpolation_dict():
            for ui_node_type, colour in ui_colour_to_update_dict.items():
                update_text_entry_line = True
                self.set_colour_to_ui_element(ui_node_type, colour, False)
                self.color_manager.set_node_color(ui_node_type, colour)

        if update_text_entry_line == False:
            if self.state == GameUIStates.UI_NORMAL_STATE and self.marked_or_weighted_node_menu.selected_option == 'Marked':
                self.weighted_node_text_entry_line.set_text_length_limit(10)
                self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
                self.weighted_node_text_entry_line.enable()
                self.weighted_node_text_entry_line.disable()
                self.weighted_node_text_entry_line.set_text('      None')

        self.theme_manager.update_theming(json.dumps(self.theme_json_data))

    def handle_ui_border_width_changed(self):
        """
        If the changed_ui_border_width attribute in self.settings_window is set to True, we will set
        it to False and then perform the required operations to ensure that the all the UI Elements
        are using the correct border width.
        """
        if self.settings_window.changed_ui_border_width:
            print("[GAME UI MANAGER] Redraw UIDropDownMenus with new border width.")
            self.settings_window.changed_ui_border_width = False
            self.update_current_pathfinding_algorithm(self.current_pathfinding_algorithm, self.heuristic)
            self.update_current_maze_generation_algorithm(self.current_maze_generation_algorithm)

            self.marked_or_weighted_node_menu.kill()
            if self.cursor_node_type == CursorNodeTypes.MARKED_NODE:
                marked_or_weighted_value = 'Marked'
            else:
                marked_or_weighted_value = 'Weighted'

            self.marked_or_weighted_node_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 130), (200, 50)),
                                                                                   options_list=['Marked', 'Weighted'],
                                                                                   starting_option=marked_or_weighted_value,
                                                                                   manager=self.manager)

            current_clear_nodes_option = self.clear_nodes_menu.selected_option
            self.clear_nodes_menu.kill()

            self.clear_nodes_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((390, 130), (200, 50)),
                                                                       options_list=self.clear_node_types,
                                                                       starting_option=current_clear_nodes_option,
                                                                       manager=self.manager)

            self.generate_theme_menu(kill_theme_menu=True)
            self.generate_networking_menu()

    def handle_bottom_ui_drop_down_menus_open(self):
        """
        If the marked or weighted node menu, clear nodes menu or theme menu are open we will return True
        otherwise we will return False.

        @return: bool
        """
        for drop_down_menu in [self.marked_or_weighted_node_menu, self.clear_nodes_menu, self.theme_menu]:
            if drop_down_menu.current_state == drop_down_menu.menu_states['expanded']:
                return True

        return False

    def handle_ui_window_open(self):
        """
        This function will return True if there are any windows open in the game
        otherwise it will return False.

        @return: bool
        """
        if len(self.manager.get_window_stack().get_stack()) > 0:
            return True
        else:
            return False

    def build_ui_normal_state(self):
        """
        This method will set the state attribute to GameUIStates.UI_NORMAL_STATE and
        perform the required operations to ensure that the UI is in GameUIStates.UI_NORMAL_STATE.
        """
        self.state = GameUIStates.UI_NORMAL_STATE
        self.run_button.set_text("Run")
        self.pathfinding_algorithms_menu.enable()
        self.update_current_pathfinding_algorithm(self.current_pathfinding_algorithm, self.heuristic)
        self.maze_generation_algorithms_menu.enable()
        self.resolution_divider_label.enable()
        self.resolution_divider_slider.enable()
        self.pathfinding_algorithm_speed_label.enable()
        self.pathfinding_algorithm_speed_slider.enable()
        self.recursive_division_speed_label.enable()
        self.recursive_division_speed_slider.enable()
        self.marked_or_weighted_node_menu.enable()
        if self.marked_or_weighted_node_menu.selected_option == 'Weighted':
            self.weighted_node_text_entry_line.enable()
        else:
            self.weighted_node_text_entry_line.disable()
        self.clear_nodes_menu.enable()
        self.tutorial_button.enable()
        self.settings_button.enable()
        self.theme_menu.enable()
        self.generate_theme_menu(kill_theme_menu=True)
        self.networking_menu.enable()
        self.generate_networking_menu()

    def build_ui_running_pathfinding_algorithm_state(self):
        """
        This method will set the state attribute to GameUIStates.UI_RUNNING_PATHFINDING_ALGORITHM_STATE and
        perform the required operations to ensure that the UI is in GameUIStates.UI_NORMAL_STATE.
        """
        self.state = GameUIStates.UI_RUNNING_PATHFINDING_ALGORITHM_STATE
        self.run_button.set_text("Cancel")
        self.pathfinding_algorithms_menu.disable()
        self.heuristics_menu.disable()
        self.maze_generation_algorithms_menu.disable()
        self.resolution_divider_label.disable()
        self.resolution_divider_slider.disable()
        self.pathfinding_algorithm_speed_label.enable()
        self.pathfinding_algorithm_speed_slider.enable()
        self.recursive_division_speed_label.disable()
        self.recursive_division_speed_slider.disable()
        if self.marked_or_weighted_node_menu.selected_option == 'Marked':
            self.weighted_node_text_entry_line.disable()
            self.weighted_node_text_entry_line.set_text('      None')
        else:
            weight = self.weighted_node_text_entry_line.get_text()
            self.weighted_node_text_entry_line.disable()
            self.weighted_node_text_entry_line.set_text(weight)
        self.marked_or_weighted_node_menu.disable()
        self.clear_nodes_menu.disable()
        self.tutorial_button.disable()
        self.settings_button.disable()
        self.theme_menu.disable()
        self.networking_menu.disable()

    def build_ui_running_recursive_division_state(self):
        """
        This method will set the state attribute to GameUIStates.UI_RUNNING_RECURSIVE_DIVISION_STATE and
        perform the required operations to ensure that the UI is in GameUIStates.UI_RUNNING_PATHFINDING_ALGORITHM_STATE.
        """
        self.state = GameUIStates.UI_RUNNING_RECURSIVE_DIVISION_STATE
        self.run_button.set_text("Cancel")
        self.pathfinding_algorithms_menu.disable()
        self.heuristics_menu.disable()
        self.maze_generation_algorithms_menu.disable()
        self.resolution_divider_label.disable()
        self.resolution_divider_slider.disable()
        self.pathfinding_algorithm_speed_label.disable()
        self.pathfinding_algorithm_speed_slider.disable()
        self.recursive_division_speed_label.enable()
        self.recursive_division_speed_slider.enable()
        if self.marked_or_weighted_node_menu.selected_option == 'Marked':
            self.weighted_node_text_entry_line.disable()
            self.weighted_node_text_entry_line.set_text('      None')
        else:
            weight = self.weighted_node_text_entry_line.get_text()
            self.weighted_node_text_entry_line.disable()
            self.weighted_node_text_entry_line.set_text(weight)
        self.marked_or_weighted_node_menu.disable()
        self.clear_nodes_menu.disable()
        self.tutorial_button.disable()
        self.settings_button.disable()
        self.theme_menu.disable()
        self.networking_menu.disable()

    def not_normal_state(self):
        """
        This function will check if the state attribute is equal to the GameUIStates.UI_NORMAL_STATE,
        if it is we will return False otherwise we will return True.

        @return: bool
        """
        if self.state != GameUIStates.UI_NORMAL_STATE:
            return True
        else:
            return False

    def draw(self):
        """
        This function will draw of the elements in the UI onto the screen.
        """
        self.manager.draw_ui(self.screen_manager.screen)
