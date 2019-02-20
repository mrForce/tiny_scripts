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
