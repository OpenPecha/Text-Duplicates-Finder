
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
            self.head.next = new_node 
        self.head = new_node


    def getLen(self, head):
        temp = head
        len = 0
        while (temp != None):
            len += 1
            temp = temp.next

        return len

    def getMiddle(self,start_node):
        head = start_node
        if head != None:
            len = self.getLen(head)
            temp = head
            midIdx = len // 2
            while midIdx != 0:
                temp = temp.next
                midIdx -= 1
 
            return temp


    def getLast(self):
        if self.head != None:
            temp = self.head
            while temp.next != None:
                temp = temp.next
            return temp

    def getFirst(self):
        if self.head != None:
            temp = self.head
            while temp.prev!= None:
                temp = temp.prev
            return temp
