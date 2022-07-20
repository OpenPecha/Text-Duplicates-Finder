from tempfile import TemporaryDirectory


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class search_Seg:
    def __init__(self):
        self.head = None
        self.firstNode = self.head

    def push(self, data):
        new_node = Node(data)
        if self.head is not None:
            new_node.prev = self.head 
        self.head = new_node


    def getLen(self, head):
        temp = head
        len = 0
        while (temp != None):
            len += 1
            temp = temp.next

        return len

    def getMiddle(self):
        head = self.firstNode
        if head != None:
            len = self.getLen(head)
            temp = head
            midIdx = len // 2
            while midIdx != 0:
                temp = temp.next
                midIdx -= 1
 
            return temp.data


    def getLast(self):
        if self.head != None:
            temp = self.head
            while temp.next != None:
                temp = temp.next
            return temp.data

    def getFirst(self):
        if self.head != None:
            temp = self.head
            while temp.prev!= None:
                temp = temp.prev
            return temp.data
