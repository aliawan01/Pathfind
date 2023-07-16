import pygame
from pygame.locals import *

import pygame_gui
import sys
import os
from enum import IntEnum

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
    def __init__(self, manager, color_manager):
        self.manager = manager
        self.color_manager = color_manager
        self.window_width = 650
        self.window_height = 600
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
            ColorNodeTypes.END_NODE_COLOR: 'End Node'
        }

        self.custom_theme_dict = {
            ColorNodeTypes.BORDER_COLOR: None,
            ColorNodeTypes.BOARD_COLOR: None,
            ColorNodeTypes.MARKED_NODE_COLOR: None,
            ColorNodeTypes.PATH_NODE_FOREGROUND_COLOR: None,
            ColorNodeTypes.PATH_NODE_BACKGROUND_COLOR: None,
            ColorNodeTypes.CHECKED_NODE_FOREGROUND_COLOR: None,
            ColorNodeTypes.CHECKED_NODE_BACKGROUND_COLOR: None,
            ColorNodeTypes.WEIGHTED_NODE_COLOR: None,
            ColorNodeTypes.START_NODE_COLOR: None,
            ColorNodeTypes.END_NODE_COLOR: None
        }

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
                                                              html_text="Welcome to Custom Theme Creation Menu!",
                                                              container=self,
                                                              manager=self.manager)

        self.custom_theme_name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, 80), (200, 80)),
                                                                   text='Custom Theme Name:',
                                                                   container=self,
                                                                   manager=self.manager)

        self.custom_theme_name_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((175, 140), (150, 50)),
                                                                                     container=self,
                                                                                     manager=self.manager)

        self.custom_theme_inheriting_theme_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, 250), (200, 80)),
                                                                               text='Inherit from Theme:',
                                                                               container=self,
                                                                               manager=self.manager)

        custom_themes_names = self.color_manager.get_all_theme_names_from_themes_list()
        custom_themes_names.append('None')
        self.custom_theme_inheriting_theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((175, 310), (150, 50)),
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
                                                                      html_text="Color Selection",
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
        height = 80

        self.ui_images = []
        self.ui_text_boxes = []
        self.ui_buttons = []

        for i in range(len(self.color_surface_list)):
            surface = self.color_surface_list[i]

            self.ui_images.append(pygame_gui.elements.UIImage(relative_rect=pygame.Rect((width, height), (50, 50)),
                                                              image_surface=surface,
                                                              container=self,
                                                              manager=self.manager))

            self.ui_text_boxes.append(pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((width + 60, height), (180, 30)),
                                                                    html_text=self.node_type_and_name_dict[list(self.node_type_and_name_dict)[i]],
                                                                    container=self,
                                                                    manager=self.manager))

            self.ui_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width + 60, height + 30), (130, 30)),
                                                                text='Edit Color',
                                                                container=self,
                                                                manager=self.manager))
            if width == 40:
                width = 340
                switch = True
            else:
                width = 40
                if switch:
                    height += 90
                    switch = False


    def clean_custom_theme_creation_selection_screen(self):
        self.stage = None
        self.color_selection_text_box.kill()
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
                                                                    html_text="Create Theme",
                                                                    container=self,
                                                                    manager=self.manager)

        # TODO(ali): Make the self.custom_theme_name bold in the html_text (do this once you have set the fonts)
        self.finish_button_info = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((100, 100), (400, 200)),
                                                                html_text=(f"Pressing the finish button will create "
                                                                f"the new custom theme {self.custom_theme_name} and it will "
                                                                f"be set as the current theme."),
                                                                container=self,
                                                                manager=self.manager)

        self.finish_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 330), (200, 100)),
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
                                                                                   html_text="Welcome to the custom theme editing menu!",
                                                                                   container=self,
                                                                                   manager=self.manager)

        self.custom_theme_editing_selection_list_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((160, 70), (300, 100)),
                                                                                          html_text=('Press the theme you want to edit and then'
                                                                                                     ' click on the next page button'),
                                                                                          container=self,
                                                                                          manager=self.manager)

        custom_theme_names = self.color_manager.get_all_theme_names_from_themes_list()
        custom_theme_names.remove('Dark Theme')
        custom_theme_names.remove('Light Theme')
        print("[THEME WINDOW] Custom theme names:", custom_theme_names)
        if self.custom_theme_to_edit_name == None:
            self.custom_theme_to_edit_name = custom_theme_names[0]
            self.changed_custom_theme_to_edit_name = True

        print(self.custom_theme_to_edit_name)
        self.custom_theme_editing_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((180, 180), ((250, 250))),
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
        self.custom_theme_editing_color_selection_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((70, 5), (self.window_width - 180, 50)),
                                                                                           html_text="Edit Color Selection",
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
        height = 80

        self.custom_theme_editing_ui_images = []
        self.custom_theme_editing_ui_text_boxes = []
        self.custom_theme_editing_ui_buttons = []

        for i in range(len(self.custom_theme_editing_color_surface_list)):
            surface = self.custom_theme_editing_color_surface_list[i]

            self.custom_theme_editing_ui_images.append(pygame_gui.elements.UIImage(relative_rect=pygame.Rect((width, height), (50, 50)),
                                                                                   image_surface=surface,
                                                                                   container=self,
                                                                                   manager=self.manager))

            self.custom_theme_editing_ui_text_boxes.append(pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((width + 60, height), (180, 30)),
                                                                                         html_text=self.node_type_and_name_dict[list(self.node_type_and_name_dict)[i]],
                                                                                         container=self,
                                                                                         manager=self.manager))

            self.custom_theme_editing_ui_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width + 60, height + 30), (130, 30)),
                                                                                     text='Edit Color',
                                                                                     container=self,
                                                                                     manager=self.manager))
            if width == 40:
                width = 340
                switch = True
            else:
                width = 40
                if switch:
                    height += 90
                    switch = False



    def clean_custom_theme_editing_color_selection_screen(self):
        self.stage = None
        self.custom_theme_editing_color_selection_text_box.kill()

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
                                                                    html_text="Finish Editing Custom Theme",
                                                                    container=self,
                                                                    manager=self.manager)

        # TODO(ali): Make the self.custom_theme_to_edit_name bold in the html_text (do this once you have set the fonts)
        self.custom_theme_editing_save_changes_button_info = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((100, 100), (400, 200)),
                                                                                     html_text=(f"Pressing the save changes button will save the changes"
                                                                                                f" you made to the custom theme {self.custom_theme_to_edit_name}"
                                                                                                f" and it will be set as the current theme."),
                                                                                     container=self,
                                                                                     manager=self.manager)

        self.custom_theme_editing_save_changes_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 330), (200, 100)),
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

        self.custom_theme_deletion_text_box = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((10, 5), (self.window_width-50, 100)),
                                                                            html_text=("Welcome to the custom theme deletion page!<br>"
                                                                                       "Select the custom theme you want to delete from the menu "
                                                                                       "below and press the 'Delete Themes' button to delete the theme."),
                                                                            container=self,
                                                                            manager=self.manager)

        custom_theme_names = self.color_manager.get_all_theme_names_from_themes_list()
        custom_theme_names.remove('Dark Theme')
        custom_theme_names.remove('Light Theme')
        print("[THEME WINDOW] Custom theme names:", custom_theme_names)

        self.custom_themes_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((180, 120), ((250, 250))),
                                                                                item_list=custom_theme_names,
                                                                                allow_multi_select=True,
                                                                                container=self,
                                                                                manager=self.manager)

        self.custom_theme_delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((205, 390), (200, 100)),
                                                                       text='Delete Themes',
                                                                       container=self,
                                                                       manager=self.manager)


    def clean_custom_theme_delete_screen(self):
        self.stage = None
        self.window_running = False
        self.custom_theme_deletion_text_box.kill()
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

                        self.custom_theme_inheriting_theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((175, 310), (150, 50)),
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
                                self.color_picker = pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect((100, 100), (400, 400)),
                                                                                            window_title=self.node_type_and_name_dict[i]+' Color',
                                                                                            initial_colour=self.color_manager.get_theme_color(list(self.node_type_and_name_dict)[i]),
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
                                self.custom_theme_editing_color_picker = pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect((100, 100), (400, 400)),
                                                                                                                 window_title=self.node_type_and_name_dict[i]+' Color',
                                                                                                                 initial_colour=self.color_manager.get_theme_color(list(self.node_type_and_name_dict)[i]),
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

class GameUIManager:
    def __init__(self, screen_manager, rect_array_obj, color_manager, grid, client, pathfinding_algorithms_dict, maze_generation_algorithms_dict, events_dict):
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.color_manager: ColorManager = color_manager
        self.grid = grid
        self.client = client
        self.pathfinding_algorithms_dict = pathfinding_algorithms_dict
        self.maze_generation_algorithms_dict = maze_generation_algorithms_dict
        self.events_dict = events_dict
        self.screen_lock = False

        self.manager = pygame_gui.UIManager((screen_manager.screen_width, screen_manager.screen_height))
        self.run_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((800, 10), (130, 50)), text="Run", manager=self.manager)

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
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((480, 10), (220, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option='Random Maze',
                                                                                  manager=self.manager)

        # TODO(ali): Could remove this label if it isn't needed later
        self.resolution_divider_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 65), (200, 30)),
                                                                    text='Resolution Divider Slider',
                                                                    manager=self.manager)

        self.resolution_divider_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 95), (280, 25)),
                                                                                start_value=4,
                                                                                value_range=(1, 8),
                                                                                manager=self.manager)

        # TODO(ali): Could remove this label it isn't needed later
        self.pathfinding_algorithm_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((370, 65), (220, 30)),
                                                                             text='Pathfinding Algorithm Speed',
                                                                             manager=self.manager)

        self.pathfinding_algorithm_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((340, 95), (280, 25)),
                                                                                         start_value=25,
                                                                                         value_range=(12, 100),
                                                                                         manager=self.manager)

        # TODO(ali): Could remove this label if it isn't needed later
        self.recursive_division_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((660, 65), (220, 30)),
                                                                          text='Recursive Division speed',
                                                                          manager=self.manager)

        self.recursive_division_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((640, 95), (280, 25)),
                                                                                      start_value=15,
                                                                                      value_range=(10, 50),
                                                                                      manager=self.manager)

        self.marked_or_weighted_node_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((20, 130), (150, 35)),
                                                                              options_list=['Marked', 'Weighted'],
                                                                              starting_option='Marked',
                                                                              manager=self.manager)

        self.weighted_node_text_entry_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((185, 130), (100, 35)),
                                                                                 manager=self.manager)

        clear_node_types = ['Clear Grid', 'Clear Path', 'Clear Checked Nodes', 'Clear Marked Nodes', 'Clear Weighted Nodes']
        self.clear_nodes_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((310, 130), (200, 40)),
                                                                   options_list=clear_node_types,
                                                                   starting_option='Clear Grid',
                                                                   manager=self.manager)

        self.generate_theme_menu()
        self.theme_window = ThemeWindow(self.manager, self.color_manager)

        self.weighted_node_text_entry_line.set_text_length_limit(10)
        self.weighted_node_text_entry_line.set_allowed_characters([' ', 'N', 'o', 'n', 'e'])
        self.weighted_node_text_entry_line.disable()
        self.weighted_node_text_entry_line.set_text('   None')

        self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.ASTAR
        self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        self.current_maze_generation_algorithm = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE
        self.recursive_division_skew = None
        self.pathfinding_algorithm_speed = 25
        self.recursive_division_speed = 15
        self.cursor_node_type = CursorNodeTypes.MARKED_NODE
        self.weight = 1

    def generate_theme_menu(self, default_theme='Dark Theme'):
        theme_menu_options = self.color_manager.get_all_theme_names_from_themes_list()
        theme_menu_options.append('Create Custom Theme')
        if self.color_manager.do_custom_themes_exists():
            theme_menu_options.append('Edit Custom Theme')
            theme_menu_options.append('Delete Custom Theme')

        self.theme_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((530, 130), (200, 40)),
                                                             options_list=theme_menu_options,
                                                             starting_option=default_theme,
                                                             manager=self.manager)


    def run_pathfinding_algorithm(self, pathfinding_algorithm, heuristic=None):
        self.rect_array_obj.reset_rect_array_adjacent_nodes()
        self.rect_array_obj.gen_rect_array_with_adjacent_nodes()
        self.rect_array_obj.reset_non_user_weights()

        pathfinding_algorithm.reset_checked_nodes_pointer()
        pathfinding_algorithm.reset_path_pointer()

        pathfinding_algorithm.reset_animated_checked_coords_stack()
        pathfinding_algorithm.reset_animated_path_coords_stack()

        pathfinding_algorithm.heuristic = heuristic
        pathfinding_algorithm.run()


    def create_empty_heuristics_menu(self):
        self.heuristics_menu.kill()
        self.heuristic = None
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((240, 10), (200, 50)),
                                                                  options_list=['None'],
                                                                  starting_option='None',
                                                                  manager=self.manager)
        self.heuristics_menu.disable()

    def create_heuristics_menu_with_distances(self, starting_value='Manhattan Distance'):
        self.heuristics_menu.kill()
        self.heuristic = PathfindingHeuristics.MANHATTAN_DISTANCE
        self.heuristics_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((240, 10), (200, 50)),
                                                                  options_list=['Manhattan Distance', 'Euclidean Distance'],
                                                                  starting_option=starting_value,
                                                                  manager=self.manager)

    def run_current_maze_generation_algorithm(self):
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
        self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()

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
                self.client.create_network_event(NetworkingEventTypes.RUN_MAZE_GENERATION_ALGORITHM, self.current_maze_generation_algorithm, self.recursive_division_skew, self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].maze.to_list())

    def get_current_pathfinding_algorithm(self):
        return self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm]

    def update_current_pathfinding_algorithm(self, pathfinding_algorithm):
        self.current_pathfinding_algorithm = pathfinding_algorithm
        match self.current_maze_generation_algorithm:
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

        if self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].heuristic == None:
            self.create_empty_heuristics_menu()
        else:
            self.heuristic = self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].heuristic
            match self.heuristic:
                case PathfindingHeuristics.EUCLIDEAN_DISTANCE:
                    self.create_heuristics_menu_with_distances('Euclidean Distance')
                case PathfindingHeuristics.MANHATTAN_DISTANCE:
                    self.create_heuristics_menu_with_distances()

    def get_current_maze_generation_algorithm(self):
        return self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm]

    def update_current_maze_generation_algorithm(self, maze_generation_algorithm):
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

        self.maze_generation_algorithms_menu.kill()
        self.maze_generation_algorithms_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((480, 10), (220, 50)),
                                                                                  options_list=self.maze_generation_algorithms_options,
                                                                                  starting_option=starting_value,
                                                                                  manager=self.manager)
    def update_resolution_divider(self):
        self.resolution_divider_slider.set_current_value(self.screen_manager.resolution_divider)

    def update_screen_lock(self, screen_lock):
        self.screen_lock = screen_lock

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
        if event.ui_element == self.pathfinding_algorithms_menu:
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()

            match event.text:
                case 'Depth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DFS
                    self.create_empty_heuristics_menu()
                case 'Breadth First Search':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.BFS
                    self.create_empty_heuristics_menu()
                case 'Dijkstra':
                    self.current_pathfinding_algorithm = PathfindingAlgorithmTypes.DIJKASTRA
                    self.create_heuristics_menu_with_distances()
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

                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()

                    self.maze_generation_algorithms_dict[self.current_maze_generation_algorithm].reset_maze_pointer()

                    self.client.create_network_event(NetworkingEventTypes.CLEAR_GRID)
                case 'Clear Path':
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer(self.color_manager.CHECKED_NODE_FOREGROUND_COLOR)
                    self.client.create_network_event(NetworkingEventTypes.CLEAR_PATH)
                case 'Clear Checked Nodes':
                    self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
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
                case _:
                    theme = self.color_manager.get_theme_from_themes_list(event.text)
                    if theme != None:
                        self.color_manager.set_and_animate_theme_colors_dict(theme)

    def handle_ui_button_pressed_event(self, event):
        self.theme_window.handle_theme_window_ui_button_pressed_event(event)
        if event.ui_element == self.run_button:
            self.run_pathfinding_algorithm(self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm], self.heuristic)
            self.client.create_network_event(NetworkingEventTypes.RUN_PATHFINDING_ALGORITHM, self.current_pathfinding_algorithm, self.heuristic)

            pygame.time.set_timer(self.events_dict['DRAW_CHECKED_NODES'], self.pathfinding_algorithm_speed)

    def handle_ui_horizontal_slider_moved_event(self, event):
        if event.ui_element == self.resolution_divider_slider:
            self.screen_manager.set_resolution_divider(event.value)
            self.rect_array_obj.reset_rect_array()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_checked_nodes_pointer()
            self.pathfinding_algorithms_dict[self.current_pathfinding_algorithm].reset_path_pointer()
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
        if event.ui_element == self.weighted_node_text_entry_line:
            self.weight = int(event.text)

    def handle_ui_window_closed_event(self, event):
        if event.ui_element == self.theme_window:
            self.theme_window.shutdown()

            if self.theme_window.custom_theme_name != None and self.color_manager.check_custom_theme_exists(self.theme_window.custom_theme_name):
                self.theme_menu.kill()
                self.generate_theme_menu(self.theme_window.custom_theme_name)
                self.theme_window.custom_theme_name = None

            elif self.theme_window.edited_custom_theme:
                self.theme_menu.kill()
                self.generate_theme_menu(self.theme_window.custom_theme_to_edit_name)
                self.theme_window.custom_theme_to_edit_name = None

            elif self.theme_window.deleted_themes:
                self.theme_menu.kill()
                self.generate_theme_menu('Dark Theme')
                self.theme_window.deleted_themes = False


    def handle_ui_color_picker_color_picked_event(self, event):
        self.theme_window.handle_theme_window_ui_color_picker_color_picked_event(event)

    def handle_ui_selection_list_new_selection(self, event):
        self.theme_window.handle_theme_window_ui_selection_list_new_selection(event)

    def handle_ui_selection_list_dropped_selection(self, event):
        self.theme_window.handle_theme_window_ui_selection_list_dropped_selection(event)

    def draw(self):
        self.manager.draw_ui(self.screen_manager.screen)