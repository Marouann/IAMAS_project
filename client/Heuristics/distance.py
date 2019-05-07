from math import sqrt

def manhattan(start: ('int', 'int'), end: ('int', 'int')) -> 'float':
    distance = [abs(a - b) for a, b in zip(start, end)]
    return sum(distance)


def euclidean(start: ('int', 'int'), end: ('int', 'int')) -> 'float':
    distance = [(a - b) ** 2 for a, b in zip(start, end)]
    return sqrt(sum(distance))





