def anoymous(x):
    return x ** 2 + 1


def integrate(fun, start, end):
    step = 0.1
    intercept = start
    area = 0
    while intercept < end:
        intercept += step
        area += fun(intercept)
    return area


if __name__ == "__main__":
    print(integrate(anoymous, 0, 10))
