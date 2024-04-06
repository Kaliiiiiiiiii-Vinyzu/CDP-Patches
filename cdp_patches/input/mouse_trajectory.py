import math
import random
from typing import Any, Callable, List, NoReturn, Tuple, Union

import numpy as np


# From https://github.com/riflosnake/HumanCursor/blob/main/humancursor/utilities/human_curve_generator.py
# Edited by Vinyzu for more realistic mouse movements
class HumanizeMouseTrajectory:
    def __init__(self, from_point: Tuple[int, int], to_point: Tuple[int, int]) -> None:
        self.from_point = from_point
        self.to_point = to_point

        if self.from_point == self.to_point:
            self.to_point = (self.from_point[0] + 10, self.from_point[1] + 10)

        self.points = self.generate_curve()
        self.points.append(to_point)

    def easeOutQuad(self, n: float) -> float:
        if not 0.0 <= n <= 1.0:
            raise ValueError("Argument must be between 0.0 and 1.0.")
        return -n * (n - 2)

    def generate_curve(self) -> List[Tuple[float, float]]:
        """Generates the curve based on arguments below, default values below are automatically modified to cause randomness"""
        left_boundary = min(self.from_point[0], self.to_point[0]) - 40
        right_boundary = max(self.from_point[0], self.to_point[0]) + 40
        down_boundary = min(self.from_point[1], self.to_point[1]) - 40
        up_boundary = max(self.from_point[1], self.to_point[1]) + 40

        points_distance = math.sqrt((self.from_point[0] - self.to_point[0]) ** 2 + (self.from_point[1] - self.to_point[1]) ** 2)
        internalKnots = self.generate_internal_knots(left_boundary, right_boundary, down_boundary, up_boundary, int(points_distance**0.25))
        points = self.generate_points(internalKnots)
        points = self.distort_points(points, 2, 2, 0.6)

        target_points = int(points_distance // 4) if int(points_distance // 4) > 2 else 2
        points = self.tween_points(points, target_points)
        return points

    def generate_internal_knots(
        self, l_boundary: Union[int, float], r_boundary: Union[int, float], d_boundary: Union[int, float], u_boundary: Union[int, float], knots_count: int
    ) -> Union[List[Tuple[int, int]], NoReturn]:
        """Generates the internal knots of the curve randomly"""
        if not (self.check_if_numeric(l_boundary) and self.check_if_numeric(r_boundary) and self.check_if_numeric(d_boundary) and self.check_if_numeric(u_boundary)):
            raise ValueError("Boundaries must be numeric values")
        if not isinstance(knots_count, int) or knots_count < 0:
            knots_count = 0
        if l_boundary > r_boundary:
            raise ValueError("left_boundary must be less than or equal to right_boundary")
        if d_boundary > u_boundary:
            raise ValueError("down_boundary must be less than or equal to upper_boundary")

        # knotsX = np.random.choice(range(int(l_boundary), int(r_boundary)), size=knots_count)
        # knotsY = np.random.choice(range(int(d_boundary), int(u_boundary)), size=knots_count)
        # knots = list(zip(knotsX, knotsY))

        # Standard deviation for normal distribution
        midpoint_x = (l_boundary + r_boundary) / 2
        midpoint_y = (d_boundary + u_boundary) / 2
        std_deviation = min(midpoint_x - l_boundary, r_boundary - midpoint_x, midpoint_y - d_boundary, u_boundary - midpoint_y)

        # Generate knotsX and knotsY using normal distribution
        knotsX = np.random.normal(midpoint_x, std_deviation, size=knots_count).astype(int)
        knotsY = np.random.normal(midpoint_y, std_deviation, size=knots_count).astype(int)

        # Clip values to within boundaries
        knotsX = np.clip(knotsX, l_boundary, r_boundary)
        knotsY = np.clip(knotsY, d_boundary, u_boundary)
        knots = list(zip(knotsX, knotsY))

        # Sort Knots
        def distance(knot):
            return math.sqrt((self.from_point[0] - knot[0]) ** 2 + (self.from_point[0] - knot[1]) ** 2)

        sorted_knots = sorted(knots, key=lambda knot: distance(knot))
        return sorted_knots

    def generate_points(self, knots: List[Tuple[int, int]]) -> List[Tuple[float, float]]:
        """Generates the points from BezierCalculator"""
        if not self.check_if_list_of_points(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max(
            abs(self.from_point[0] - self.to_point[0]),
            abs(self.from_point[1] - self.to_point[1]),
            2,
        )
        knots = [self.from_point] + knots + [self.to_point]
        return BezierCalculator.calculate_points_in_curve(int(midPtsCnt), knots)

    def distort_points(self, points: List[Tuple[float, float]], distortion_mean: int, distortion_st_dev: int, distortion_frequency: float) -> Union[List[Tuple[float, float]], NoReturn]:
        """Distorts points by parameters of mean, standard deviation and frequency"""
        if not (self.check_if_numeric(distortion_mean) and self.check_if_numeric(distortion_st_dev) and self.check_if_numeric(distortion_frequency)):
            raise ValueError("Distortions must be numeric")
        if not self.check_if_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortion_frequency <= 1):
            raise ValueError("distortion_frequency must be in range [0,1]")

        distorted: List[Tuple[float, float]] = []
        for i in range(1, len(points) - 1):
            x, y = points[i]
            delta = int(np.random.normal(distortion_mean, distortion_st_dev) if random.random() < distortion_frequency else 0)
            distorted.append((x + delta // 5, y + delta // 5))
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tween_points(self, points: List[Tuple[float, float]], target_points: int) -> Union[List[Tuple[float, float]], NoReturn]:
        """Modifies points by tween"""
        if not self.check_if_list_of_points(points):
            raise ValueError("List of points not valid")
        if not isinstance(target_points, int) or target_points < 2:
            raise ValueError("target_points must be an integer greater or equal to 2")

        res: List[Tuple[float, float]] = []
        for i in range(target_points):
            index = int(self.easeOutQuad(float(i) / (target_points - 1)) * (len(points) - 1))
            res.append(points[index])
        return res

    @staticmethod
    def check_if_numeric(val: Any) -> bool:
        """Checks if value is proper numeric value"""
        return isinstance(val, (float, int, np.integer, np.float32, np.float64))

    def check_if_list_of_points(self, list_of_points: Union[List[Tuple[int, int]], List[Tuple[float, float]]]) -> bool:
        """Checks if list of points is valid"""
        try:

            def point(p):
                return (len(p) == 2) and self.check_if_numeric(p[0]) and self.check_if_numeric(p[1])

            return all(map(point, list_of_points))
        except (KeyError, TypeError):
            return False


class BezierCalculator:
    @staticmethod
    def binomial(n: int, k: int) -> float:
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernstein_polynomial_point(x: int, i: int, n: int) -> float:
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return float(BezierCalculator.binomial(n, i) * (x**i) * ((1 - x) ** (n - i)))  # Quirky for mypy :D

    @staticmethod
    def bernstein_polynomial(points: List[Tuple[int, int]]) -> Callable[[float], Tuple[float, float]]:
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the Bezier described by these points
        """

        def bernstein(t):
            n = len(points) - 1
            x = y = 0.0
            for i, point in enumerate(points):
                bern = BezierCalculator.bernstein_polynomial_point(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y

        return bernstein

    @staticmethod
    def calculate_points_in_curve(n: int, points: List[Tuple[int, int]]) -> List[Tuple[float, float]]:
        """
        Given list of control points, returns n points in the Bézier curve,
        described by these points
        """
        curvePoints: List[Tuple[float, float]] = []
        bernstein_polynomial = BezierCalculator.bernstein_polynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints += (bernstein_polynomial(t),)
        return curvePoints
