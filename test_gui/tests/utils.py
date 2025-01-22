import random
import string


def generateWord(n: int):
    return "".join(random.choice(string.ascii_letters) for _ in range(n))


def generateOutputPath():
    return tuple(generateWord(random.randint(4, 10)) for _ in range(random.randint(3, 4)))


def generateRandomCode(n: int) -> list[tuple[str, ...]]:
    codes = {generateOutputPath() for _ in range(n)}

    while len(codes) < n:
        codes.add(generateOutputPath())

    return list(codes)
