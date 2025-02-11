import math

# 1
def degree_to_radian(degree):
    return degree * math.pi / 180


degree = 15
radian = degree_to_radian(degree)

print(f"Degree: {degree}")
print(f"Radian: {radian:.6f}")


# 2
def trapezoid_area(base1, base2, height):
    return (base1 + base2) * height / 2


area = trapezoid_area(5, 5, 6)

print(f"Area trapezoid: {area}")


# 3
def polygon_area(sides, length):
    return (sides * length ** 2) / (4 * math.tan(math.pi / sides))



area = polygon_area(2, 34)

print(f"area of polygon is: {area}")


# 4
def parallelogram_area(base, height):
    return base * height




area = parallelogram_area(5, 15)

print(f"Area  parallelogram: {area}")
