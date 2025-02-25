from functools import reduce
import time
import math

# Task 1
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)
print("Product of numbers:", product)

# Task 2: Count uppercase and lowercase
string = "HelloWorld"
upper_case = sum(1 for c in string if c.isupper())
lower_case = sum(1 for c in string if c.islower())
print(f"Upper case letters: {upper_case}, Lower case letters: {lower_case}")

# Task 3 if a string is a palindrome
palindrome_test = "madam"
is_palindrome = palindrome_test == palindrome_test[::-1]
print(f"Is '{palindrome_test}' a palindrome?", is_palindrome)

# Task 4 square root function after specific milliseconds
num, delay = 25100, 2123
time.sleep(delay / 1000)
sqrt_result = math.sqrt(num)
print(f"Square root of {num} after {delay} milliseconds is", sqrt_result)

# Task 5 if all elements of a tuple are true
tuple_test = (True, True, False)
all_true = all(tuple_test)
print("All elements true:", all_true)
