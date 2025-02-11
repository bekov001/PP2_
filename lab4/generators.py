# 1.
def squares_up_to_n(n):
    for i in range(n + 1):
        yield i * i


for square in squares_up_to_n(5):
    print(square)


# 2
def even_numbers_up_to_n(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input("Enter a number n: "))
even_nums = list(even_numbers_up_to_n(n))
print(",".join(map(str, even_nums)))


# 3
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i


for num in divisible_by_3_and_4(100):
    print(num)


# 4
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i


a = int(input("Enter the starting number a: "))
b = int(input("Enter the ending number b: "))

for square in squares(a, b):
    print(square)


# 5
def countdown(n):
    while n >= 0:
        yield n
        n -= 1


n = int(input("Enter a number to start the countdown: "))
for num in countdown(n):
    print(num)