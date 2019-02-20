class Node:
    def __init__(self, value):
        self.value = value
        self.next_node = None
        self.prev_node = None

head = None
tail = None

def display():
    global head
    global tail
    curr_node = head
    nodes = []
    while curr_node:
        nodes.append(str(curr_node.value))
        curr_node = curr_node.next_node
    print('the list: ' + ' '.join(nodes))

def insert(value):
    global head
    global tail
    new_node = Node(value)
    if tail == None and head == None:
        head = new_node
        tail = new_node
    elif value >= tail.value:
        tail.next_node = new_node
        new_node.prev_node = tail
        tail = new_node
    elif value <= head.value:
        head.prev_node = new_node
        new_node.next_node = head
        head = new_node
    else:
        iterator = head
        while iterator.value < value:
            iterator = iterator.next_node
        behind = iterator.prev_node
        next_node = iterator
        behind.next_node = new_node
        new_node.next_node = next_node
        next_node.prev_node = new_node
        new_node.prev_node = behind

def _delete(value, start):
    global head
    global tail
    if start != None and start.value == value:
        if start == head:
            if start == tail:
                head = None
                tail = None
            else:
                new_head = head.next_node
                head = new_head
                head.prev_node = None
                _delete(value, head)
        elif start == tail:
            new_tail = tail.prev_node
            new_tail.next_node = None
            tail = new_tail
        else:
            new_start = start.next_node
            start.prev_node.next_node = start.next_node
            start.next_node.prev_node = start.prev_node
            _delete(value, new_start)
def delete(value):
    global head
    if head != None:
        iterator = head
        while iterator != None and iterator.value < value:
            iterator = iterator.next_node
        _delete(value, iterator)

        
insert(1)
display()
insert(2)
display()
insert(5)
display()
insert(3)
display()
insert(0)
display()
insert(3)
display()
delete(3)
display()
delete(5)
display()
delete(1)
display()
delete(2)
display()
