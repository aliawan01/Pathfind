class Stack:
    def __init__(self, size): 
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
        if None in self.stack:
            self.pointer += 1
            self.stack[self.pointer] = value
        else:
            if show_errors:
                print("STACK PUSH ERROR: The stack is full.")
            return -1

    def pop(self, show_errors=True):
        if self.pointer != -1:
            self.stack[self.pointer] = None
            self.pointer -= 1
        else:
            if show_errors:
                print("STACK POP ERROR: The stack is empty.")
            return -1

    def peek(self, show_errors=True):
        if self.pointer != -1:
            return self.stack[self.pointer]
        else:
            if show_errors:
                print("STACK PEEK ERROR: The stack is empty.")
            return -1

    def get_size(self):
        counter = 0
        for item in self.stack:
            if item != None:
                counter += 1

        return counter

    def remove_empty_values(self):
        items_to_remove_indexes = []
        for i in range(len(self.stack)):
            if self.stack[i] == None:
                self.stack = self.stack[:i]
                break

    def reverse(self):
        self.remove_empty_values()
        self.stack = self.stack[::-1]
