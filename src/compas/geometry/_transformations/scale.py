"""
This library for transformations partly derived and was re-implemented from the
following online resources:

    * http://www.lfd.uci.edu/~gohlke/code/transformations.py.html
    * http://www.euclideanspace.com/maths/geometry/rotations/
    * http://code.activestate.com/recipes/578108-determinant-of-matrix-of-any-order/
    * http://blog.acipo.com/matrix-inversion-in-javascript/

Many thanks to Christoph Gohlke, Martin John Baker, Sachin Joglekar and Andrew
Ippoliti for providing code and documentation.
"""
from compas.utilities import flatten
from compas.geometry import allclose
from compas.geometry import multiply_matrices
from compas.geometry._transformations import decompose_matrix
from compas.geometry._transformations import matrix_from_scale_factors
from compas.geometry._transformations import matrix_from_change_of_basis
from compas.geometry._transformations import Transformation

__all__ = ['Scale']


class Scale(Transformation):
    """Creates a scale transformation.

    Parameters
    ----------
    matrix : 4x4 matrix-like, optional
        A 4x4 matrix (or similar) representing a scaling.

    Raises
    ------
    ValueError
        If the default constructor is used,
        and the provided transformation matrix is not a scale matrix.

    Examples
    --------
    >>> S = Scale.from_factors([1, 2, 3])
    >>> S[0, 0] == 1
    True
    >>> S[1, 1] == 2
    True
    >>> S[2, 2] == 3
    True

    >>> point = Point(2, 5, 0)
    >>> frame = Frame(point, (1, 0, 0), (0, 1, 0))
    >>> points = [point, Point(2, 10, 0)]
    >>> S = Scale.from_factors([2.] * 3, frame)
    >>> [p.transformed(S) for p in points]
    [Point(2.000, 5.000, 0.000), Point(2.000, 15.000, 0.000)]
    """

    def __init__(self, matrix=None):
        if matrix:
            scale, _, _, _, _ = decompose_matrix(matrix)
            check = matrix_from_scale_factors(scale)
            if not allclose(flatten(matrix), flatten(check)):
                raise ValueError('This is not a proper scale matrix.')
        super(Scale, self).__init__(matrix=matrix)

    @classmethod
    def from_factors(cls, factors, frame=None):
        """Construct a scale transformation from scale factors.

        Parameters
        ----------
        factors : list of float
            The scale factors along X, Y, Z.

        Returns
        -------
        Scale
            A scale transformation.

        Examples
        --------
        >>> point = Point(2, 5, 0)
        >>> frame = Frame(point, (1, 0, 0), (0, 1, 0))
        >>> points = [point, Point(2, 10, 0)]
        >>> S = Scale.from_factors([2.] * 3, frame)
        >>> [p.transformed(S) for p in points]
        [Point(2.000, 5.000, 0.000), Point(2.000, 15.000, 0.000)]
        """
        S = cls()
        if frame:
            from compas.geometry import Frame
            Tl = matrix_from_change_of_basis(Frame.worldXY(), frame)
            Sc = matrix_from_scale_factors(factors)
            Tw = matrix_from_change_of_basis(frame, Frame.worldXY())
            S.matrix = multiply_matrices(multiply_matrices(Tw, Sc), Tl)
        else:
            S.matrix = matrix_from_scale_factors(factors)
        return S


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import doctest
    from compas.geometry import Point, Frame
    doctest.testmod(globs=globals())
