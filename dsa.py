
import heapq


# 1. STACK - Last In, First Out (LIFO)
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        return self.items[-1] if self.items else None

    def is_empty(self):
        return len(self.items) == 0


# 2. QUEUE - First In, First Out (FIFO)
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)

    def is_empty(self):
        return len(self.items) == 0


# 3. LINKED LIST - Nodes connected through links
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            return

        current = self.head

        while current.next:
            current = current.next

        current.next = new_node

    def display(self):
        current = self.head
        records = []

        while current:
            records.append(current.data)
            current = current.next

        return records


# 4. HEAP - Find employees with highest final salaries
def highest_paid_employees(employees, count=5):
    # Negative salary makes Python's min-heap act as a max-heap.
    heap = [
        (-emp.calculate_final_salary(), emp.emp_id, emp)
        for emp in employees
    ]

    heapq.heapify(heap)
    result = []

    for _ in range(min(count, len(heap))):
        result.append(heapq.heappop(heap)[2])

    return result


# 5. TREE - Binary Search Tree ordered by final salary
class TreeNode:
    def __init__(self, employee):
        self.employee = employee
        self.left = None
        self.right = None


class SalaryTree:
    def __init__(self):
        self.root = None

    def insert(self, employee):
        self.root = self._insert(self.root, employee)

    def _insert(self, node, employee):
        if node is None:
            return TreeNode(employee)

        salary = employee.calculate_final_salary()
        current_salary = node.employee.calculate_final_salary()

        if salary < current_salary:
            node.left = self._insert(node.left, employee)
        else:
            node.right = self._insert(node.right, employee)

        return node

    def get_sorted_employees(self):
        result = []

        def inorder(node):
            if node is not None:
                inorder(node.left)
                result.append(node.employee)
                inorder(node.right)

        inorder(self.root)
        return result


# 6. SEARCHING - Linear search by employee ID
def search_by_id(employees, emp_id):
    for employee in employees:
        if employee.emp_id.lower() == emp_id.lower():
            return employee

    return None


# 7. SORTING - Bubble sort by final salary
def sort_by_salary(employees):
    result = employees.copy()

    for i in range(len(result)):
        for j in range(len(result) - i - 1):
            if (
                result[j].calculate_final_salary()
                > result[j + 1].calculate_final_salary()
            ):
                result[j], result[j + 1] = (
                    result[j + 1], result[j]
                )

    return result
