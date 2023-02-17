from tolerant.toposort import toposort
from pprint import pprint


def main():
    expected = [{4}, {3}, {2}, {1}]
    actual = list(toposort({1: {2},
                            2: {3},
                            3: {4},
                            }))
    pprint(expected)
    pprint(actual)


main()
