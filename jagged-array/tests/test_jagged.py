from jagged import Jagged


def test_create_jagged():
    jagged_array = [[[0], [1, 2], [3, 4, 5, 6, 7], [8], [9, 10, 11]], [[12]], [[13, 14, 15], []]]

    ar = Jagged(jagged_array)

    shape_array = [
        [0, 3],
        [0, 5, 6, 8],
        [0, 1, 3, 8, 9, 12, 13, 16, 16]
    ]

    data_array = list(range(16))

    assert _jagged_list_equal(ar.shape_array, shape_array)
    assert _jagged_list_equal(ar.data_array, data_array)


def test_index():
    jagged_array = [
        [
            [0],
            [1, 2],
            [3, 4, 5, 6, 7],
            [8],
            [9, 10, 11]
        ],
        [
            [12]
        ],
        [
            [13, 14, 15],
            []
        ]
    ]

    ar = Jagged(jagged_array)

    assert ar[0, 2, 1] == jagged_array[0][2][1]


def _jagged_list_equal(ar1, ar2):
    if isinstance(ar1, list) != isinstance(ar2, list):
        return False

    if isinstance(ar1, list):
        return all(_jagged_list_equal(a1, a2) for a1, a2 in zip(ar1, ar2))
    else:
        return ar1 == ar2
