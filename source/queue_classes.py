class Queue:
    def __init__(self):
        """
        Initializes the Queue class.
        """
        self.heap = []

    def __iter__(self):
        return iter(self.heap)

    def __str__(self):
        return str(self.heap)

    def remove_empty_values(self):
        """
        This function will go through the self.heap list and find
        any elements which are the None value, and it will remove them
        from the list.
        """
        indexes_to_remove = []
        for i in range(len(self.heap)):
            if self.heap[i] == None:
                indexes_to_remove.append(i)

        for i in indexes_to_remove:
            self.heap.pop(i)

    def enqueue(self, item):
        """
        This function will enqueue an item into the queue.

        @param item: Any
        """
        self.heap.append(item)

    def dequeue(self):
        """
        This function will remove the first element in the
        queue as long as the queue is not empty.

        @return: Any or None
        """
        if len(self.heap) > 0:
            return self.heap.pop(0)
        else:
            return None

    def peek(self):
        """
        This function will return the first item in the
        self.heap list.

        @return: ANy
        """
        return self.heap[0]

    def exists(self, item):
        """
        This function will check if the item given exists in the self.heap list.

        @param item: Any
        @return: bool
        """
        if item in self.heap:
            return True
        else:
            return False

    def is_empty(self):
        """
        This function will check if the queue is empty.

        @return: bool
        """
        if len(self.heap) == 0:
            return True
        else:
            return False

class PriorityQueue:
    def __init__(self):
        """
        Initializes the PriorityQueue class.
        """
        self.heap = []

    def __iter__(self):
        return iter(self.heap)

    def __str__(self):
        return str(self.heap)

    def enqueue(self, item, priority):
        """
        Will add an item to the queue with the given priority.

        @param item: Any
        @param priority: int
        """
        self.heap.append((item, priority))

    def dequeue(self):
        """
        This function will remove the item which has the highest
        priority from the priority queue as long as the queue is not
        empty.

        @return: Any
        """
        current_item_index = 0
        for i in range(len(self.heap)):
            if self.heap[i][1] < self.heap[current_item_index][1]:
                current_item_index = i

        coord = self.heap[current_item_index][0]
        self.heap.pop(current_item_index)
        return coord

    def peek(self):
        """
        This function will return the item with the highest priority
        in the priority queue.

        @return: Any
        """
        current_item_index = 0
        for i in range(len(self.heap)):
            if self.heap[i][1] < self.heap[current_item_index][1]:
                current_item_index = i

        coord = self.heap[current_item_index][0]
        return coord

    def exists(self, item):
        """
        This will check if the item given exists in the self.heap list.

        @param item: Any
        @return: bool
        """
        for heap_item, heap_priority in self.heap:
            if heap_item == item: 
                return True

        return False

    def replace(self, item, new_priority_value):
        """
        If the item given exists in the priority queue, this
        function will change the priority of that item to
        the new priority value we have been given.

        @param item: Any
        @param new_priority_value: int
        """
        for i in range(len(self.heap)):
            if self.heap[i][0] == item:
                element = list(self.heap[i])
                element[1] = new_priority_value
                self.heap[i] = element
                break

    def is_empty(self):
        """
        This function will check if the priority queue is empty.

        @return: bool
        """
        if len(self.heap) == 0:
            return True
        else:
            return False
