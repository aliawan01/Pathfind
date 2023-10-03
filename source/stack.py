import traceback

class Stack:
    def __init__(self, size):
        """
        Initializes the Stack class.

        @param size: int
        """
        self.size = size
        self.stack = []
        for x in range(self.size):
            self.stack.append(None)
        self.pointer = -1

    def __iter__(self):
        return iter(self.stack)

    def __str__(self):
        return str(self.stack)

    def push(self, value, show_errors=True):
        """
        If the stack is not full, this function will add an element
        to the stack and also increment the pointer attribute. If
        the stack is full and the show_errors variable given is equal
        to True we will print out an error message.

        @param value: Any
        @param show_errors: bool
        @return: None or -1
        """
        if None in self.stack:
            self.pointer += 1
            self.stack[self.pointer] = value
        else:
            if show_errors:
                print("STACK PUSH ERROR: The stack is full.")
                traceback.print_stack()
            return -1

    def pop(self, show_errors=True):
        """
        If the stack is not empty, this function will remove the element
        in the stack at the index of the pointer attribute, it will then
        decrement the pointer attribute. If the stack is empty and the
        show_errors variable given is equal to True we will print out
        an error message.

        @param show_errors: bool
        @return: None or -1
        """
        if self.pointer != -1:
            self.stack[self.pointer] = None
            self.pointer -= 1
        else:
            if show_errors:
                print("STACK POP ERROR: The stack is empty.")
                traceback.print_stack()
            return -1

    def peek(self, show_errors=True):
        """
        If the stack is not empty, we will print out the element
        in the stack at the index of the pointer attribute. If the
        stack is empty and the show_errors variable is set to True
        we will print out an error message.

        @param show_errors: bool
        @return: Any or -1
        """
        if self.pointer != -1:
            return self.stack[self.pointer]
        else:
            if show_errors:
                print("STACK PEEK ERROR: The stack is empty.")
                traceback.print_stack()
            return -1

    def get_size(self):
        """
        This function will return the number of elements in the
        stack.

        @return: int
        """
        counter = 0
        for item in self.stack:
            if item != None:
                counter += 1

        return counter

    def remove_empty_values(self):
        """
        This function will go through the self.stack list and find
        any elements which are the None value, and it will remove them
        from the list.
        """
        for i in range(len(self.stack)):
            if self.stack[i] == None:
                self.stack = self.stack[:i]
                break

    def gen_copy_without_empty_values(self):
        """
        This function will create a copy of the self.stack list, and
        remove any None values in the list. It will then return this
        list.

        @return: List
        """
        stack_copy = self.stack.copy()
        items_to_remove_indexes = []
        for i in range(len(stack_copy)):
            if stack_copy[i] == None:
                items_to_remove_indexes.append(i)

        for index in items_to_remove_indexes[::-1]:
            stack_copy.pop(index)

        return stack_copy


    def reverse(self):
        """
        This function will run the remove_empty_values method
        and then reverse the self.stack list.
        """
        self.remove_empty_values()
        self.stack = self.stack[::-1]

    def exists(self, item):
        """
        This function will check if the item given exists in the self.stack list.

        @param item: Any
        @return: bool
        """
        if item in self.stack:
            return True
        else:
            return False

    def merge(self, stack1, stack2):
        """
        This function will run the remove_empty_values method on the stack1 and stack2
        stacks we have been given. It will then combine these two stacks and make this
        combined stack the value of the self.stack attribute.

        @param stack1: Stack
        @param stack2: Stack
        """
        stack1.remove_empty_values()
        stack2.remove_empty_values()
        self.stack = stack1.stack + stack2.stack

    def to_list(self):
        """
        This function will run the remove_empty_values method and
        then return the self.stack list.

        @return: List
        """
        self.remove_empty_values()
        return self.stack
