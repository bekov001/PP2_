# Task 1
def grams_to_ounces(grams):
    return 28.3495231 * grams


# Task 2
def fahrenheit_to_celsius(fahrenheit):
    return (5 / 9) * (fahrenheit - 32)


# Task 3
def solve(numheads, numlegs):
    for chickens in range(numheads + 1):
        rabbits = numheads - chickens
        if 2 * chickens + 4 * rabbits == numlegs:
            return chickens, rabbits
    return None


# Task 4
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def filter_prime(numbers):
    return [num for num in numbers if is_prime(num)]


# Task 5
from itertools import permutations


def print_permutations(s):
    perms = [''.join(p) for p in permutations(s)]
    for perm in perms:
        print(perm)


# Task 6
def reverse_sentence(sentence):
    words = sentence.split()
    return ' '.join(reversed(words))


# Task 7
def has_33(nums):
    for i in range(len(nums) - 1):
        if nums[i] == 3 and nums[i + 1] == 3:
            return True
    return False


# Task 8
def spy_game(nums):
    code = [0, 0, 7]
    index = 0
    for num in nums:
        if num == code[index]:
            index += 1
            if index == len(code):
                return True
    return False


# Task 9
import math


def sphere_volume(radius):
    return (4 / 3) * math.pi * (radius**3)


# Task 10
def unique_elements(lst):
    unique = []
    for item in lst:
        if item not in unique:
            unique.append(item)
    return unique


# Task 11
def is_palindrome(s):
    s = s.replace(" ", "").lower()
    return s == s[::-1]


# Task 12
def histogram(lst):
    for num in lst:
        print('*' * num)


# Task 13
import random


def guess_the_number():
    name = input("Hello! What is your name?\n")
    print(f"Well, {name}, I am thinking of a number between 1 and 20.")
    number = random.randint(1, 20)
    guesses = 0

    while True:
        guess = int(input("Take a guess.\n"))
        guesses += 1
        if guess < number:
            print("Your guess is too low.")
        elif guess > number:
            print("Your guess is too high.")
        else:
            print(f"Good job, {name}! You guessed my number in {guesses} guesses!")
            break


