"""Tests of the arithmetic behind the place index.

The numbers come from the real case: the extract for Holm holds seventeen streets called
"Hauptstrasse". The index carried them as one and averaged their points -- the representative then
lay 490 m from the nearest real Hauptstrasse and 2.26 km from the centre of Holm.
"""

from itertools import pairwise

import pytest
from geometry import (
    by_housenumber,
    distance_m,
    group_lines,
    lowest_housenumber,
    median_housenumber,
    nearest_group,
    representative_point,
)

#: The centre of Holm from tiles/region.json, as (lat, lon).
HOLM = (53.62053, 9.67601)


class TestTheRepresentativePoint:
    def test_a_straight_street_is_represented_at_its_middle(self):
        line = [(53.620, 9.670), (53.620, 9.680)]
        lat, lon = representative_point([line])
        assert lat == pytest.approx(53.620, abs=1e-6)
        assert lon == pytest.approx(9.675, abs=1e-4)

    def test_the_point_lies_on_the_street_and_not_beside_it(self):
        # An L-shaped street. The centroid of its vertices lies in the corner of the bounding
        # box -- so beside the carriageway. That was exactly the error.
        line = [(53.620, 9.670), (53.620, 9.680), (53.630, 9.680)]
        point = representative_point([line])

        distance = min(_distance_to_segment(point, a, b) for a, b in pairwise(line))
        assert distance < 1.0, "the representative point has to lie on the course of the street"

    def test_a_long_street_without_intermediate_points_does_not_end_at_an_edge(self):
        # Two vertices, a kilometre apart. Searching only among the vertices lands at one end --
        # which is why the point is projected onto the segment.
        line = [(53.615, 9.676), (53.624, 9.676)]
        point = representative_point([line])
        assert distance_m(point, line[0]) > 400
        assert distance_m(point, line[1]) > 400

    def test_several_pieces_are_represented_together(self):
        piece_a = [(53.620, 9.670), (53.620, 9.675)]
        piece_b = [(53.620, 9.675), (53.620, 9.680)]
        assert representative_point([piece_a, piece_b]) == pytest.approx(
            representative_point([[(53.620, 9.670), (53.620, 9.680)]]), abs=1e-4
        )

    def test_without_points_nothing_is_guessed(self):
        with pytest.raises(ValueError):
            representative_point([])


class TestGrouping:
    def test_two_villages_yield_two_streets(self):
        # The actual failure case: the same name, kilometres apart.
        in_holm = [(53.6205, 9.6727), (53.6210, 9.6740)]
        in_the_next_village = [(53.6550, 9.6582), (53.6555, 9.6590)]
        assert len(group_lines([in_holm, in_the_next_village])) == 2

    def test_adjoining_pieces_stay_one_street(self):
        # Consecutive way pieces share their end point -- distance zero.
        first = [(53.620, 9.670), (53.620, 9.675)]
        second = [(53.620, 9.675), (53.620, 9.680)]
        assert len(group_lines([first, second])) == 1

    def test_a_long_street_does_not_fall_apart(self):
        # Three pieces, start and end more than a kilometre apart. Without the transitive
        # chaining the street would fall into parts and each part would get a point.
        pieces = [
            [(53.615, 9.676), (53.618, 9.676)],
            [(53.618, 9.676), (53.621, 9.676)],
            [(53.621, 9.676), (53.624, 9.676)],
        ]
        groups = group_lines(pieces)
        assert len(groups) == 1
        assert sorted(groups[0]) == [0, 1, 2]

    def test_the_order_of_the_pieces_changes_nothing(self):
        pieces = [
            [(53.621, 9.676), (53.624, 9.676)],
            [(53.6550, 9.6582), (53.6555, 9.6590)],
            [(53.618, 9.676), (53.621, 9.676)],
        ]
        groups = sorted(sorted(g) for g in group_lines(pieces))
        assert groups == [[0, 2], [1]]


class TestTheNearestGroup:
    def test_the_street_in_the_museums_village_wins(self):
        # From the real collection: Holm's Hauptstrasse lies 0.2 km from the village centre, the
        # largest group of the same name 2.0 km away in a neighbouring village. So the majority of
        # house numbers is precisely not what decides -- nearness to the village decides.
        candidates = [(53.6304, 9.6498), (53.6205, 9.6727), (53.6111, 9.6305)]
        assert nearest_group(candidates, HOLM) == 1

    def test_the_averaged_point_would_have_lost(self):
        # The old value: the average of all seventeen Hauptstrassen. It lies further from Holm
        # than Holm's own Hauptstrasse -- the proof that averaging was the wrong move.
        averaged = (53.6405036, 9.669539)
        in_holm = (53.6205, 9.6727)
        assert distance_m(averaged, HOLM) > distance_m(in_holm, HOLM)
        assert distance_m(averaged, HOLM) == pytest.approx(2260, abs=150)

    def test_without_candidates_nothing_is_guessed(self):
        with pytest.raises(ValueError):
            nearest_group([], HOLM)


class TestHouseNumbers:
    def test_walking_order_instead_of_the_alphabet(self):
        # Alphabetically "10" would come before "9" and "1a" before "2" -- the classic silent error.
        addresses = [(n, (53.62, 9.67)) for n in ["10", "1a", "2", "9", "1", "12"]]
        assert [n for n, _ in by_housenumber(addresses)] == [
            "1",
            "1a",
            "2",
            "9",
            "10",
            "12",
        ]

    def test_median_housenumber_represents_the_street(self):
        addresses = [
            ("1", (53.620, 9.670)),
            ("3", (53.620, 9.672)),
            ("5", (53.620, 9.674)),
        ]
        assert median_housenumber(addresses) == (53.620, 9.672)

    def test_the_input_order_does_not_change_the_middle(self):
        addresses = [("9", (53.62, 9.679)), ("1", (53.62, 9.671)), ("5", (53.62, 9.675))]
        assert median_housenumber(addresses) == (53.62, 9.675)
        assert median_housenumber(list(reversed(addresses))) == (53.62, 9.675)

    def test_with_an_even_count_the_smaller_one_wins(self):
        addresses = [("1", (53.62, 9.671)), ("2", (53.62, 9.672))]
        assert median_housenumber(addresses) == (53.62, 9.671)

    def test_lowest_housenumber_ignores_the_position_in_the_list(self):
        addresses = [
            ("12", (53.62, 9.679)),
            ("1a", (53.62, 9.671)),
            ("1", (53.62, 9.670)),
        ]
        assert lowest_housenumber(addresses) == (53.62, 9.670)

    def test_house_number_one_decides_between_two_villages(self):
        # The case at issue: two "Hauptstrassen". The one in the neighbouring village is longer
        # and its middle happens to be nearer the museum's village -- its number 1 is not.
        in_holm = [("1", (53.6205, 9.6727)), ("40", (53.6180, 9.6690))]
        in_the_next_village = [("1", (53.6550, 9.6582)), ("2", (53.6300, 9.6600))]
        candidates = [
            lowest_housenumber(in_holm),
            lowest_housenumber(in_the_next_village),
        ]
        assert nearest_group(candidates, HOLM) == 0

    def test_without_addresses_nothing_is_guessed(self):
        with pytest.raises(ValueError):
            median_housenumber([])
        with pytest.raises(ValueError):
            lowest_housenumber([])


def _distance_to_segment(point, start, end):
    """For the test only: does the point really lie on the segment?"""
    from geometry import _nearest_on_segment

    return distance_m(point, _nearest_on_segment(start, end, point))
