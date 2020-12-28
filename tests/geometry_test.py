# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import itertools as it

import pytest

from webtraversallibrary.geometry import Point, Rectangle

# pylint: disable=redefined-outer-name


@pytest.fixture
def points():
    ps = [(0, 0), (0, 1), (10, 2), (4, 1), (6, 2), (-1, 43)]
    qs = [(4, 1), (0, 1), (5, 2), (4, 1), (10, 2), (-1, 43)]
    return ps, qs


def test_point_equality(points):
    for p, q in zip(*points):
        pp, pq = Point(*p), Point(*q)

        assert (pp == pq) == (p == q)
        assert (pp != pq) == (p != q)


def test_point_ordering(points):
    for p, q in zip(*points):
        pp, pq = Point(*p), Point(*q)

        assert (pp < pq) == (p < q)
        assert (pp <= pq) == (p <= q)
        assert (pp > pq) == (p > q)
        assert (pp >= pq) == (p >= q)


def test_point_zero():
    a = Point.zero()
    b = Point.zero()
    assert a + b == Point(0, 0)


def test_point_unpacking():
    x, y = Point(3, 4)
    assert x == 3
    assert y == 4


def test_rectangle_from_many_representations():
    x1, y1 = 0, 1
    x2, y2 = 2, 3

    r1 = Rectangle.from_list((x1, y1, x2, y2))
    r2 = Rectangle(Point(x1, y1), Point(x2, y2))
    r3 = Rectangle.from_list([x1, y1, x2, y2])
    r4 = Rectangle.from_list([x1, y2, x2, y1])
    r5 = Rectangle.from_list([x2, y2, x1, y1])

    rects = [r1, r2, r3, r4, r5]
    for ri, rj in it.product(rects, repeat=2):
        assert ri == rj

    r_different = Rectangle.from_list([y1, x1, x2, y2])
    for r in rects:
        assert r != r_different

    with pytest.raises(ValueError):
        Rectangle.from_list(1, 2, 3)


def test_rectangle_properties():
    x1, y1 = 0, 1
    x2, y2 = 2, 3

    w = x2 - x1
    h = y2 - y1

    r = Rectangle.from_list((x1, y1, x2, y2))

    assert r.x == x1
    assert r.y == y1
    assert r.center == Point((x1 + x2) / 2, (y1 + y2) / 2)
    assert r.width == w
    assert r.height == h
    assert r.area == w * h
    assert r.bounds == (0, 1, 2, 3)


def test_rectangle_contains():
    r_large = Rectangle.from_list([0, 0, 5, 5])
    r_small = Rectangle.from_list([1, 1, 2, 2])
    r_mid = Rectangle.from_list([-1, -1, 3, 3])
    r_touching = Rectangle.from_list([0, 0, 4, 5])

    assert r_small in r_small  # pylint: disable=comparison-with-itself

    assert r_small in r_large
    assert r_mid not in r_large
    assert r_touching in r_large
    assert r_small in r_mid
    assert r_mid not in r_touching
    assert r_small in r_touching

    assert Point(0, 0) in r_large
    assert Point(0, 0) not in r_small
    assert Point(1, 1) in r_large
    assert Point(1, 1) in r_small

    with pytest.raises(TypeError):
        assert "not a rectangle" in r_large


def test_rectangle_add():
    r_large = Rectangle.from_list([0, 0, 5, 5])
    r_moved = r_large + Point(1, 2)
    assert r_moved.bounds == (1, 2, 6, 7)


def test_rectangle_sub():
    r_large = Rectangle.from_list([0, 0, 5, 5])
    r_moved = r_large - Point(1, 2)
    assert r_moved.bounds == (-1, -2, 4, 3)


def test_rectangle_bounding_box():
    r1 = Rectangle(Point(0, 1), Point(2, 3))
    r2 = Rectangle(Point(0, 0), Point(4, 2))

    assert Rectangle.bounding_box([r1, r2]) == Rectangle(Point(0, 0), Point(4, 3))


def test_rectangle_centered_at():
    x, y = 1, 2
    radius = 2

    rect_centered_at_xy = Rectangle.centered_at(Point(x, y), radius)

    assert rect_centered_at_xy.area == (2 * radius) ** 2
    assert rect_centered_at_xy.width == 2 * radius
    assert rect_centered_at_xy.height == 2 * radius
    assert rect_centered_at_xy == Rectangle.from_list((x - radius, y - radius, x + radius, y + radius))

    with pytest.raises(ValueError):
        Rectangle.centered_at(Point(1, 2), -1)


def test_rectangle_intersection():
    r_large = Rectangle.from_list([0, 0, 5, 5])
    r_small = Rectangle.from_list([1, 1, 2, 2])
    r_touching = Rectangle.from_list([0, 0, 4, 5])
    r_other = Rectangle.from_list([-3, -3, -1, -1])

    assert Rectangle.intersection([r_other, r_touching]) == Rectangle.empty()

    assert Rectangle.intersection([r_large, r_small]) == r_small
    assert Rectangle.intersection([r_large, r_large]) == r_large

    int1 = Rectangle.intersection([Rectangle.from_list([0, 0, 2, 2]), Rectangle.from_list([0, 2, 1, 3])])

    assert int1 == Rectangle.from_list([0, 2, 1, 2])
    assert int1 != Rectangle.empty()

    assert Rectangle.intersection([r_other, Rectangle.empty()]) == Rectangle.empty()

    with pytest.raises(ValueError):
        Rectangle.intersection([])
    with pytest.raises(ValueError):
        Rectangle.intersection([Rectangle.empty()])


@pytest.mark.parametrize(
    "src,clip_by,dst",
    [
        # X.clip(X) == X
        ([0, 0, 5, 5], [0, 0, 5, 5], [0, 0, 5, 5]),
        # If rectangles intersect, operation is equivalent to intersection (and therefore commutative):
        ([0, 0, 5, 5], [4, -10, 10, 10], [4, 0, 5, 5]),
        ([4, -10, 10, 10], [0, 0, 5, 5], [4, 0, 5, 5]),
        # If rectangles don't intersect, it should return degenerate rectangles on the border of ``clip_by``
        ([0, 0, 0, 0], [1, 1, 2, 2], [1, 1, 1, 1]),
        ([10, 10, 100, 100], [1, 1, 2, 2], [2, 2, 2, 2]),
        ([10, -10, 20, 10], [1, 1, 2, 2], [2, 1, 2, 2]),
        ([-10, 10, 10, 10], [1, 1, 2, 2], [1, 2, 2, 2]),
    ],
)
def test_rectangle_clip(src, clip_by, dst):
    assert Rectangle.from_list(src).clip(Rectangle.from_list(clip_by)) == Rectangle.from_list(dst)


def test_rectangle_resized():
    d = 3

    r = Rectangle.from_list([1, 2, 6, 7])
    R = r.resized(delta=d)

    assert R.area == 2 * d * (r.width + r.height + 2 * d) + r.area
    assert R.contains(r)
    assert Rectangle.intersection([R, r]) == r
    assert Rectangle.bounding_box([R, r]) == R

    with pytest.raises(AssertionError):
        _ = r.resized(delta=-6)

    assert r.resized(delta=-r.width / 2) == Rectangle(r.center, r.center)

    with pytest.raises(ValueError):
        Rectangle.bounding_box([])


def test_rectangle_unpacking():
    x, y, w, h = Rectangle(Point(3, 4), Point(5, 7))
    assert x == 3
    assert y == 4
    assert w == 2
    assert h == 3
