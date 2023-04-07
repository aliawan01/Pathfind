# TODO(ali): Need to make them work as actual queues.
class Queue:
    def __init__(self):
        self.heap = []

    def __iter__(self):
        return iter(self.heap)

    def __str__(self):
        return str(self.heap)

    def remove_empty_values(self):
        indexes_to_remove = []
        for i in range(len(self.heap)):
            if self.heap[i] == None:
                indexes_to_remove.append(i)

        for i in indexes_to_remove:
            self.heap.pop(i)

    def enqueue(self, item):
        self.heap.append(item)

    def dequeue(self):
        if len(self.heap) > 0:
            return self.heap.pop(0)
        else:
            return None

    def peek(self):
        return self.heap[0]

    def exists(self, item):
        if item in self.heap: 
            return True
        else:
            return False

    def is_empty(self):
        if len(self.heap) == 0:
            return True
        else:
            return False

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def __iter__(self):
        return iter(self.heap)

    def __str__(self):
        return str(self.heap)

    def enqueue(self, item, priority):
        self.heap.append((item, priority))

    def dequeue(self):
        current_item_index = 0
        for i in range(len(self.heap)):
            if self.heap[i][1] < self.heap[current_item_index][1]:
                current_item_index = i

        coord = self.heap[current_item_index][0]
        self.heap.pop(current_item_index)
        return coord

    def peek(self):
        current_item_index = 0
        for i in range(len(self.heap)):
            if self.heap[i][1] < self.heap[current_item_index][1]:
                current_item_index = i

        coord = self.heap[current_item_index][0]
        return coord

    def exists(self, item):
        for heap_item, heap_priority in self.heap:
            if heap_item == item: 
                return True

        return False

    def replace(self, coord, new_f_value):
        for i in range(len(self.heap)):
            if self.heap[i][0] == coord:
                self.heap[i][1] == new_f_value
                break

    def is_empty(self):
        if len(self.heap) == 0:
            return True
        else:
            return False
