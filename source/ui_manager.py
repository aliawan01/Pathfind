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
        self.stage = None
        self.welcome_text_box.kill()
        self.custom_theme_name_label.kill()
        self.custom_theme_name_text_entry_line.kill()
        self.custom_theme_inheriting_theme_label.kill()
        self.custom_theme_inheriting_theme_menu.kill()


    def build_custom_theme_creation_selection_screen(self):
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
        self.stage = ThemeWindowStages.CUSTOM_THEME_CREATION_FINISH_SCREEN
        self.next_page_button.disable()
        self.finish_screen_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                    html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Create Theme</var></font>",
                                                                    object_id="#text_box_title",
                                                                    container=self,
                                                                    manager=self.manager)

        # TODO(ali): Make the self.custom_theme_name bold in the html_text (do this once you have set the fonts)
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
        self.stage = None
        self.finish_screen_text_box.kill()
        self.finish_button_info.kill()
        self.finish_button.kill()

    def build_custom_theme_editing_welcome_screen(self):
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

        print(self.custom_theme_to_edit_name)
        self.custom_theme_editing_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((210, 180), ((250, 250))),
                                                                                       item_list=custom_theme_names,
                                                                                       default_selection=self.custom_theme_to_edit_name,
                                                                                       container=self,
                                                                                       manager=self.manager)

    def clean_custom_theme_editing_welcome_screen(self):
        self.stage = None
        self.custom_theme_editing_welcome_text_box.kill()
        self.custom_theme_editing_selection_list_text_box.kill()
        self.custom_theme_editing_selection_list.kill()

    def build_custom_theme_editing_color_selection_screen(self):
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
        self.stage = ThemeWindowStages.CUSTOM_THEME_EDITING_FINISH_SCREEN
        print("Reached the theme editing finish screen")

        self.custom_theme_editing_next_page_button.disable()
        self.custom_theme_editing_finish_screen_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                                         html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Finish Editing Custom Theme</var></font>",
                                                                                         object_id="#text_box_title",
                                                                                         container=self,
                                                                                         manager=self.manager)

        # TODO(ali): Make the self.custom_theme_to_edit_name bold in the html_text (do this once you have set the fonts)
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
        self.stage = None
        self.custom_theme_editing_finish_screen_text_box.kill()
        self.custom_theme_editing_save_changes_button_info.kill()
        self.custom_theme_editing_save_changes_button.kill()

    def build_custom_theme_delete_screen(self):
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
        self.stage = None
        self.window_running = False
        self.custom_theme_deletion_title_text_box.kill()
        self.custom_theme_deletion_info_text_box.kill()
        self.custom_themes_selection_list.kill()
        self.custom_theme_delete_button.kill()


    def handle_theme_window_ui_text_entry_finished_event(self, event):
        if self.window_running:
            match self.stage:
                case ThemeWindowStages.CUSTOM_THEME_CREATION_WELCOME_SCREEN:
                    if event.ui_element == self.custom_theme_name_text_entry_line:
                        if event.text in self.color_manager.get_all_theme_names_from_themes_list():
                            # TODO(ali): Flash a red color on the text entry line and empty it instead.
                            self.custom_theme_name_text_entry_line.set_text('A custom theme already exists with this name.')
                        else:
                            self.custom_theme_name = event.text
                            self.changed_custom_theme_name = True
                            self.next_page_button.enable()

    def handle_theme_window_ui_drop_down_menu_changed_event(self, event):
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
        if self.window_running and self.stage == ThemeWindowStages.CUSTOM_THEME_DELETE_SCREEN:
            if event.ui_element == self.custom_themes_selection_list:
                self.custom_themes_to_delete_names.remove(event.text)
                print(self.custom_themes_to_delete_names)

    def shutdown(self):
        print("[THEME WINDOW] Shutdown Theme Window")
        self.window_running = False

class UINetworkingManager(pygame_gui.elements.UIWindow):
    def __init__(self, manager, client, server, font_manager):
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
        self.ip_address = "127.0.0.1"

    def create_server(self):
        if self.created_server == False:
            self.created_server = True
            self.shutdown_server = False
            self.connected_to_server = False

            self.port = random.randint(2000, 10000)
            self.server.run_server(self.ip_address, self.port)
            self.client.connect_to_server(self.ip_address, self.port)
            # TODO(ali): Make the port and ip address bold

            message = (f'We have successfully created a server running on<br><br><b>IP Address: {self.ip_address}<br>Port: {self.port}</b><br>'
                       f'<br>You can now allow your friends to join your game by telling them to click on the <b>Connect to Server</b> option'
                       f' and typing in the IP address and port shown in this window in the relevant fields.')

            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                               window_title='Created Server Message Window',
                                               html_message=message,
                                               manager=self.manager)

    def show_server_info(self):
        message = (f'Your server is running on<br><br><b>IP Address: {self.ip_address}<br>Port: {self.port}<br>'
                   f'Number of currently connected clients: {self.server.get_number_of_currently_connected_clients()}</b>'
                   f'<br><br>You can allow your friends to join your game by telling them to click on the <b>Connect to Server</b>'
                   f' option and typing in the IP address and port shown in this window in the relevant fields.')

        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           window_title='Server Information Window',
                                           html_message=message,
                                           manager=self.manager)

    def destroy_server(self):
        self.shutdown_server = True
        self.created_server = False
        self.connected_to_server = False
        self.server.shutdown()
        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           window_title='Server Shutdown Window',
                                           html_message="Successfully shutdown the server, all of the clients have been kicked out as well.",
                                           manager=self.manager)

    def check_is_valid_ip_address(self, ip_address):
        try:
            ip_address_obj = ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def check_is_valid_port(self, port_number):
        if port_number in range(2000, 10000):
            return True
        else:
            return False

    def server_connection_has_broken(self):
        self.created_server = False
        self.connected_to_server = False
        if self.shutdown_server:
            self.shutdown_server = False
        else:
            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                               html_message="The server has been shutdown by the owner and you have been kicked out of the server.",
                                               manager=self.manager)


    def build_networking_connect_to_server_screen(self):
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
        self.networking_connect_to_server_ip_address_text_entry_line.set_text("127.0.0.1")

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
        self.window_running = False
        self.networking_connect_to_server_welcome_title_text_box.kill()
        self.networking_connect_to_server_welcome_info_text_box.kill()
        self.networking_connect_to_server_ip_address_label.kill()
        self.networking_connect_to_server_ip_address_text_entry_line.kill()
        self.networking_connect_to_server_port_label.kill()
        self.networking_connect_to_server_port_text_entry_line.kill()
        self.networking_connect_to_server_button.kill()

    def disconnect_from_server(self):
        self.created_server = False
        self.connected_to_server = False

        self.client.create_network_event(NetworkingEventTypes.DISCONNECT_FROM_SERVER)
        pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (self.window_width, self.window_height)),
                                           html_message="Successfully disconnected from server.",
                                           manager=self.manager)

    def handle_ui_networking_manager_ui_button_pressed_event(self, event):
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


                # TODO(ali): Set self.connected_to_server = True and self.created_server = False, here if we can successfully connect to the server.
                self.clean_networking_connect_server_screen()
                self.kill()

                if self.connected_to_server:
                    return True

    def shutdown_networking_window(self):
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
    # TODO(ali): Tell the user to explore the rest of the UI and game as well in the end screen.
    TUTORIAL_END_SCREEN = 12

class TutorialWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, color_manager, font_manager, settings_window):
        self.manager = manager
        self.color_manager = color_manager
        self.font_manager = font_manager
        self.settings_window = settings_window
        self.window_width = 650
        self.window_height = 600
        self.window_running = False
        self.stage = 0
        self.stages_build_and_clean_functions_dict = {
            TutorialWindowStages.TUTORIAL_WELCOME_SCREEN: {'build': self.build_tutorial_welcome_screen, 'clean': self.clean_tutorial_welcome_screen},
            TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION: {'build': self.build_project_description_screen, 'clean': self.clean_project_description_screen},
            TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM: {'build': self.build_pathfinding_algorithm_screen, 'clean': self.clean_pathfinding_algorithm_screen}
        }

    def build_tutorial_welcome_screen(self):
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

        self.disable_tutorial_on_startup = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((410, 470), (180, 50)),
                                                                        text='Disable On Startup',
                                                                        container=self,
                                                                        manager=self.manager)

        if self.settings_window.should_build_tutorial_window_on_startup() == False:
            self.disable_tutorial_on_startup.hide()

    def clean_tutorial_welcome_screen(self):
        self.welcome_text_box.kill()
        self.disable_tutorial_on_startup.kill()

    def build_project_description_screen(self):
        self.stage = TutorialWindowStages.TUTORIAL_PROJECT_DESCRIPTION
        self.project_description_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                          html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Project Description</var></font>",
                                                                          object_id="#text_box_title",
                                                                          container=self,
                                                                          manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_project_description_screen(self):
        self.project_description_text_box.kill()

    def build_pathfinding_algorithm_screen(self):
        self.stage = TutorialWindowStages.TUTORIAL_PATHFINDING_ALGORITHM
        self.pathfinding_algorithm_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 80)),
                                                                            html_text=f"<font name={self.font_manager.current_font_name} pixel_size={self.font_manager.ui_title_font_size_value}><var>Pathfinding Algorithms</var></font>",
                                                                            object_id="#text_box_title",
                                                                            container=self,
                                                                            manager=self.manager)

        self.next_page_button.enable()
        self.previous_page_button.enable()

    def clean_pathfinding_algorithm_screen(self):
        self.pathfinding_algorithm_text_box.kill()

    def handle_tutorial_window_ui_button_pressed(self, event):
        if self.window_running:
            if self.stage == TutorialWindowStages.TUTORIAL_WELCOME_SCREEN:
                if event.ui_element == self.disable_tutorial_on_startup:
                    print("[TUTORIAL WINDOW] Tutorial Window has been disabled from startup")
                    self.settings_window.set_disable_tutorial_window_on_startup(True)
                    self.disable_tutorial_on_startup.kill()

            if event.ui_element == self.next_page_button:
                self.stages_build_and_clean_functions_dict[self.stage]['clean']()
                self.stages_build_and_clean_functions_dict[self.stage+1]['build']()
            elif event.ui_element == self.previous_page_button:
                self.stages_build_and_clean_functions_dict[self.stage]['clean']()
                self.stages_build_and_clean_functions_dict[self.stage-1]['build']()

    def shutdown(self):
        print("[TUTORIAL WINDOW] Shutdown Tutorial Window")
        self.window_running = False

class FontManager:
    def __init__(self, manager, theme_manager, theme_json_data):
        self.manager = manager
        self.theme_manager = theme_manager
        self.theme_json_data = theme_json_data
        self.current_font_name = 'Roboto'
        self.ui_normal_font_size_value = 15
        self.ui_title_font_size_value = 20

        with open('data/fonts/font_info.json') as file:
            self.font_json_data = json.loads(file.read())

    def save_font_json_data(self):
        with open('data/fonts/font_info.json', 'w') as file:
            file.write(json.dumps(self.font_json_data))

    def load_ui_fonts(self):
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
        if font_name in self.get_custom_ui_font_names():
            if font_name == self.current_font_name:
                self.current_font_name = "Roboto"
                self.set_current_font("Roboto")

            self.font_json_data.pop(font_name)
            self.save_font_json_data()
        else:
            print(f"[FONT MANAGER: DELETE_UI_FONT] Error no custom font exists with the name '{font_name}'")


    def set_current_font(self, font_name):
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
        for ui_element in self.theme_json_data:
            if 'font' in self.theme_json_data[ui_element]:
                if 'normal_font' in self.theme_json_data[ui_element]['font']:
                    self.theme_json_data[ui_element]['font']['size'] = font_size
        else:
            self.ui_normal_font_size_value = font_size
            self.theme_manager.update_theming(json.dumps(self.theme_json_data))

    def get_ui_font_names(self):
        return list(self.font_json_data.keys())

    def get_custom_ui_font_names(self):
        custom_font_names = []
        for font in self.font_json_data:
            if self.font_json_data[font]['custom_font']:
                custom_font_names.append(font)

        return custom_font_names

    def custom_ui_fonts_exist(self):
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
        with open('data/settings/user_settings.json', 'w') as file:
            file.write(json.dumps(self.user_settings_json_data))

    def handle_settings_window_border_width_changed(self):
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
        return not self.user_settings_json_data['disable_tutorial_on_startup']

    def set_disable_tutorial_window_on_startup(self, option):
        self.user_settings_json_data['disable_tutorial_on_startup'] = option
        self.save_user_settings()

    def build_settings_window(self):
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
        self.stage = None
        self.welcome_to_font_deletion_text_box.kill()
        self.previous_page_button.kill()
        self.custom_font_selection_list.kill()
        self.custom_font_delete_button.kill()

    def handle_settings_window_ui_button_pressed_event(self, event):
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
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_CREATION_SCREEN:
                if event.ui_element == self.custom_font_name_text_entry_line:
                    if event.text in self.font_manager.get_ui_font_names():
                        self.custom_font_name_text_entry_line.set_text("A custom font already exists with this name.")

    def handle_settings_window_ui_selection_list_new_selection(self, event):
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN:
                if event.ui_element == self.custom_font_selection_list:
                    self.custom_fonts_to_delete_names.append(event.text)
                    print(self.custom_fonts_to_delete_names)

    def handle_settings_window_ui_selection_list_dropped_selection(self, event):
        if self.window_running:
            if self.stage == SettingsWindowStages.SETTINGS_WINDOW_CUSTOM_FONT_DELETION_SCREEN:
                if event.ui_element == self.custom_font_selection_list:
                    self.custom_fonts_to_delete_names.remove(event.text)
                    print(self.custom_fonts_to_delete_names)

    def shutdown(self):
        print("[SETTINGS WINDOW] Shutdown Settings Window")
        self.window_running = False

class GameUIStates(IntEnum):
    UI_NORMAL_STATE = 0,
    UI_RUNNING_PATHFINDING_ALGORITHM_STATE = 1,
    UI_RUNNING_RECURSIVE_DIVISION_STATE = 2

class GameUIManager:
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager, grid, client, server, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict):
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

        # TODO(ali): Could remove this label if it isn't needed later
        self.resolution_divider_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 65), (250, 30)),
                                                                    text='Grid Size',
                                                                    manager=self.manager)

        self.resolution_divider_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 92), (320, 27)),
                                                                                start_value=4,
                                                                                value_range=(1, 8),
                                                                                manager=self.manager)

        # TODO(ali): Could remove this label it isn't needed later
        self.pathfinding_algorithm_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((400, 65), (280, 30)),
                                                                             text='Pathfinding Algorithm Speed',
                                                                             manager=self.manager)

        self.pathfinding_algorithm_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((380, 92), (320, 27)),
                                                                                         start_value=25,
                                                                                         value_range=(12, 100),
                                                                                         manager=self.manager)

        # TODO(ali): Could remove this label if it isn't needed later
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
        if kill_networking_menu:
            self.networking_menu.kill()

        if self.ui_networking_manager.created_server == False and self.ui_networking_manager.connected_to_server == False:
            options = ['Create Server', 'Connect to Server']
        elif self.ui_networking_manager.created_server and self.ui_networking_manager.connected_to_server == False:
            options = ['Show Server Info', 'Destroy Server']
        elif self.ui_networking_manager.created_server == False and self.ui_networking_manager.connected_to_server:
            options = ['Disconnect from Server']
        else:
            # TODO(ali): Remove this else statements once you've finished making the networking menu.
            print("----------\nERROR!!! generate_networking_menu(), doesn't have any valid options, you haven't reset or assigned either self.created_server or self.connected_to_server properly.\n---------------")
            print("created_server:", self.ui_networking_manager.create_server)
            print("connected_to_server:", self.ui_networking_manager.connected_to_server)


        self.networking_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((650, 10), (200, 50)),
                                                                  options_list=options,
                                                                  starting_option=options[0],
                                                                  manager=self.manager)



    def run_pathfinding_algorithm(self, pathfinding_algorithm, heuristic=None):
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
        self.heuristics_menu.kill()
        self.heuristic = None
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((230, 10), (200, 50)),
                                                                  options_list=['None'],
                                                                  starting_option='None',
                                                                  manager=self.manager)
        self.heuristics_menu.disable()

    def create_heuristics_menu_with_distances(self, starting_value='Manhattan Distance'):
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
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()

        self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()
        # screen_lock = True

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
        return self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm]

    def update_current_pathfinding_algorithm(self, pathfinding_algorithm, heuristic, is_server_event=False):
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
        return self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm]

    def update_current_maze_generation_algorithm(self, maze_generation_algorithm, is_server_event=False):
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
        self.resolution_divider_slider.set_current_value(self.screen_manager.resolution_divider)

    def get_pathfinding_algorithm_speed(self):
        return self.pathfinding_algorithm_speed

    def get_recursive_division_speed(self):
        return self.recursive_division_speed

    def get_cursor_node_type(self):
        return self.cursor_node_type

    def get_weight(self):
        return self.weight

    def update_pathfinding_algorithm_speed(self, pathfinding_algorithm_speed):
        self.pathfinding_algorithm_speed = pathfinding_algorithm_speed
        self.pathfinding_algorithm_speed_slider.set_current_value(self.pathfinding_algorithm_speed)

    def update_recursive_division_speed(self, recursive_division_speed):
        self.recursive_division_speed = recursive_division_speed
        self.recursive_division_speed_slider.set_current_value(self.recursive_division_speed)

    def handle_ui_drop_down_menu_changed_event(self, event):
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
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
        pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], 0)
        pygame.time.set_timer(self.events_dict['DRAW_PATH'], 0)
        self.build_ui_normal_state()

    def cancel_recursive_division(self, cut_off_point=None):
        self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].cut_maze(cut_off_point)
        pygame.time.set_timer(self.events_dict['DRAW_MAZE'], 0)
        self.build_ui_normal_state()

    def handle_ui_button_pressed_event(self, event):
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
        self.theme_window.handle_theme_window_ui_text_entry_finished_event(event)
        self.settings_window.handle_settings_window_ui_text_entry_finished_event(event)
        if event.ui_element == self.weighted_node_text_entry_line:
            self.weight = int(event.text)

    def handle_ui_window_closed_event(self, event):
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
        self.theme_window.handle_theme_window_ui_color_picker_color_picked_event(event)

    def handle_ui_selection_list_new_selection(self, event):
        self.theme_window.handle_theme_window_ui_selection_list_new_selection(event)
        self.settings_window.handle_settings_window_ui_selection_list_new_selection(event)

    def handle_ui_selection_list_dropped_selection(self, event):
        self.theme_window.handle_theme_window_ui_selection_list_dropped_selection(event)
        self.settings_window.handle_settings_window_ui_selection_list_dropped_selection(event)

    def handle_ui_file_dialog_path_picked_event(self, event):
        self.settings_window.handle_settings_window_ui_file_dialog_path_picked_event(event)

    def update_client_received_new_theme(self):
        if self.client.received_new_theme:
            self.client.received_new_theme = False
            self.generate_theme_menu(kill_theme_menu=True)
            pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((60, 100), (650, 600)),
                                               html_message=(f"A client has sent the theme {self.color_manager.current_theme_name} to you,"
                                                             f" and it has been set as the current theme."),
                                               manager=self.manager)

    def update_networking_server_connection_broken(self):
        if self.client.server_connection_broken:
            self.client.server_connection_broken = False
            self.ui_networking_manager.server_connection_has_broken()
            self.generate_networking_menu()
            self.generate_theme_menu(kill_theme_menu=True)

    def set_colour_to_ui_element(self, ui_node_type, colour, update_theme=True):
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
        theme_colors_dict = self.color_manager.get_theme_colors_dict()
        for ui_node_type in ColorUITypes:
            self.set_colour_to_ui_element(ui_node_type, self.color_manager.get_theme_color(ui_node_type), False)

        self.theme_manager.update_theming(json.dumps(self.theme_json_data))
        print(f"[SET_UI_COLOURS_FROM_CURRENT_THEME] Set UI Colours from theme: '{self.color_manager.current_theme_name}'")

    def handle_ui_colour_animations(self):
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
        for drop_down_menu in [self.marked_or_weighted_node_menu, self.clear_nodes_menu, self.theme_menu]:
            if drop_down_menu.current_state == drop_down_menu.menu_states['expanded']:
                return True

        return False

    def handle_ui_window_open(self):
        if len(self.manager.get_window_stack().get_stack()) > 0:
            return True
        else:
            return False

    def build_ui_normal_state(self):
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
        if self.state != GameUIStates.UI_NORMAL_STATE:
            return True
        else:
            return False

    def draw(self):
        self.manager.draw_ui(self.screen_manager.screen)
