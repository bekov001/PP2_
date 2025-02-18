import re

# 1
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"ab*"
print(bool(re.fullmatch(pattern, string)))

# 2
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"ab{2,3}"
print(bool(re.fullmatch(pattern, string)))

# 3
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"[a-z]+_[a-z]+"
print(re.findall(pattern, string))

# 4
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"[A-Z][a-z]+"
print(re.findall(pattern, string))

# 5
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"a.*b"
print(bool(re.fullmatch(pattern, string)))

# 6
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
pattern = r"[ ,.]"
print(re.sub(pattern, ":", string))

# 7
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
parts = string.split("_")
print(parts[0] + "".join(word.capitalize() for word in parts[1:]))

# 8
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
print(re.split(r"(?=[A-Z])", string))

# 9
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
print(re.sub(r"(?=[A-Z])", " ", string).strip())

# 10
with open("row.txt", "r", encoding="utf-8") as file:
    string = file.read().strip()
print(re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower())