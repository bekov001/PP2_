import os
import shutil


# Task 6
path = "."
print("Directories:", [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
print("Files:", [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
print("All contents:", os.listdir(path))


# Task 7
path = "test.txt"
print("Exists:", os.path.exists(path))
print("Readable:", os.access(path, os.R_OK))
print("Writable:", os.access(path, os.W_OK))
print("Executable:", os.access(path, os.X_OK))

# Task 8
if os.path.exists(path):
    print("Filename:", os.path.basename(path))
    print("Directory:", os.path.dirname(path))

# Task 9 Count lines in a text file
file_path = "test.txt"
if os.path.exists(file_path):
    with open(file_path, "r") as file:
        print("Number of lines:", sum(1 for _ in file))

# Task 10
lines = ["Hello", "World", "Python"]
with open("output.txt", "w") as file:
    file.writelines("\n".join(lines))

# Task 11: Generate 26 text files from A.txt to Z.txt
for char in range(65, 91):
    with open(f"{chr(char)}.txt", "w") as file:
        file.write(f"This is {chr(char)}.txt\n")

# Task 12: Copy contents
source = "output.txt"
destination = "copy.txt"
if os.path.exists(source):
    shutil.copy(source, destination)

# Task 13: Delete a file
file_to_delete = "copy.txt"
if os.path.exists(file_to_delete) and os.access(file_to_delete, os.W_OK):
    os.remove(file_to_delete)
    print(f"Deleted: {file_to_delete}")
