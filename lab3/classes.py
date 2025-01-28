class StringManipulator:
    def __init__(self):
        self.input_string = ""

    def getString(self):
        self.input_string = input("Enter a string: ")

    def printString(self):
        print(self.input_string.upper())



class Shape:
    def area(self):
        return 0


class Square(Shape):
    def __init__(self, length):
        self.length = length

    def area(self):
        return self.length ** 2



class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width


import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def show(self):
        print(f"Coordinates: ({self.x}, {self.y})")

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def dist(self, other_point):
        return math.sqrt((self.x - other_point.x) ** 2 + (self.y - other_point.y) ** 2)



class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount}. New balance: {self.balance}")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds!")
        else:
            self.balance -= amount
            print(f"Withdrew {amount}. New balance: {self.balance}")


def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True



if __name__ == "__main__":

    print("Task 1: String Manipulator")
    sm = StringManipulator()
    sm.getString()
    sm.printString()
    print()


    print("Task 2: Shape and Square")
    square = Square(5)
    print("Area of Square:", square.area())
    print()


    print("Task 3: Rectangle")
    rectangle = Rectangle(4, 6)
    print("Area of Rectangle:", rectangle.area())
    print()


    print("Task 4: Point")
    p1 = Point(1, 2)
    p2 = Point(4, 6)
    p1.show()
    p1.move(3, 5)
    p1.show()
    print("Distance between p1 and p2:", p1.dist(p2))
    print()


    print("Task 5: Bank Account")
    acc = Account("John Doe", 1000)
    acc.deposit(500)
    acc.withdraw(200)
    acc.withdraw(2000)
    print()


    print("Task 6: Filter Prime Numbers")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    prime_numbers = list(filter(lambda x: is_prime(x), numbers))
    print("Prime numbers:", prime_numbers)