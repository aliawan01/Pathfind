# NOTE(ali): Temporarily going to be something that resembles a priority queue.
class PriorityQueue:
    def __init__(self):
        self.heap = []

    def enqueue(self, item, priority):
        self.heap.append((item, priority))
        # heapq.heappush(self.heap, (item, priority))

    def dequeue(self):
        current_item_index = 0
        for i in range(len(self.heap)):
            if self.heap[i][1] < self.heap[current_item_index][1]:
                current_item_index = i

        coord = self.heap[current_item_index][0]
        self.heap.pop(current_item_index)
        return coord
        # return heapq.heappop(self.heap)[0]

    def replace(self, coord, new_f_value):
        for i in range(len(self.heap)):
            if self.heap[i][0] == coord:
                self.heap[i][1] == new_f_value
                break

    # def check_exists(self, item):
        # for heap_item, priority in self.heap:
            # if list(heap_item) == list(item):
                # return True

        # return False

    def is_empty(self):
        if len(self.heap) == 0:
            return True
        else:
            return False


