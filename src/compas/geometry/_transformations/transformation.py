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
import math

from compas.geometry import multiply_matrices
from compas.geometry import transpose_matrix

from compas.geometry._transformations import identity_matrix
from compas.geometry._transformations import matrix_inverse
from compas.geometry._transformations import matrix_determinant
from compas.geometry._transformations import matrix_from_frame
from compas.geometry._transformations import matrix_from_euler_angles
from compas.geometry._transformations import basis_vectors_from_matrix
from compas.geometry._transformations import translation_from_matrix
from compas.geometry._transformations import decompose_matrix


__all__ = ['Transformation']


class Transformation(object):
    """The ``Transformation`` represents a 4x4 transformation matrix.

    It is the base class for transformations like :class:`Rotation`,
    :class:`Translation`, :class:`Scale`, :class:`Reflection`,
    :class:`Projection` and :class:`Shear`.

    The class allows to concatenate Transformations by multiplication, to
    calculate the inverse transformation and to decompose a transformation into
    its components of rotation, translation, scale, shear, and perspective.
    The matrix follows the row-major order, such that translation components
    x, y, z are in the right column of the matrix, i.e. ``M[0][3], M[1][3],
    M[2][3] = x, y, z``.

    Parameters
    ----------
    matrix : list of list of float, optional
        The 4x4 transformation matrix.

    Attributes
    ----------
    matrix : list of list of float
        A 4x4 transformation matrix.

    Examples
    --------
    >>> from compas.geometry import Frame
    >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
    >>> T = Transformation.from_frame(f1)
    >>> Sc, Sh, R, Tl, P = T.decomposed()
    >>> Tinv = T.inverse()
    """

    __module__ = 'compas.geometry'

    def __init__(self, matrix=None):
        """Construct a transformation from a 4x4 transformation matrix.
        """
        self.matrix = matrix

    def __mul__(self, other):
        return self.concatenated(other)

    def __imul__(self, other):
        return self.concatenated(other)

    def __getitem__(self, key):
        i, j = key
        return self.matrix[i][j]

    def __setitem__(self, key, value):
        i, j = key
        self.matrix[i][j] = value

    def __iter__(self):
        return iter(self.matrix)

    def __eq__(self, other, tol=1e-05):
        try:
            A = self.matrix
            B = other.matrix
            for i in range(4):
                for j in range(4):
                    if math.fabs(A[i][j] - B[i][j]) > tol:
                        return False
            return True
        except BaseException:
            return False

    def copy(self):
        """Returns a copy of the transformation.
        """
        cls = type(self)
        return cls(self.matrix.copy())

    def __repr__(self):
        return "Transformation({})".format(self.matrix)

    def __len__(self):
        return len(self.matrix)

    @classmethod
    def from_data(cls, data):
        """Creates a ``Transformation`` from a data dict.

        Parameters
        ----------
        data : :obj:`dict`
            A dictionary with a transformation matrix stored under the key "matrix".

        Returns
        -------
        Transformation
            The ``Transformation`` object.

        Examples
        --------
        >>> matrix = [[1, 0, 0, 3], [0, 1, 0, 4], [0, 0, 1, 5], [0, 0, 0, 1]]
        >>> data = {'matrix': matrix}
        >>> T = Transformation.from_data(data)

        """
        return cls(data['matrix'])

    def to_data(self):
        """Convert a ``Transformation`` object to a data dict.

        Returns
        -------
        dict
            A dictionary with a transformation matrix stored under the key "matrix".
        """
        return {'matrix': self.matrix}

    @classmethod
    def from_matrix(cls, matrix):
        """Creates a ``Transformation`` from a 4x4 matrix-like object.

        Parameters
        ----------
        matrix : 4x4 matrix-like
            The 4x4 transformation matrix.

        Returns
        -------
        Transformation
            The ``Transformation`` object.
        """
        return cls(matrix)

    @classmethod
    def from_list(cls, numbers):
        """Creates a ``Transformation`` from a list of 16 numbers.

        Parameters
        ----------
        numbers : :obj:`list` of :obj:`float`
            A list of 16 numbers

        Returns
        -------
        Transformation
            The ``Transformation`` object.

        Examples
        --------
        >>> numbers = [1, 0, 0, 3, 0, 1, 0, 4, 0, 0, 1, 5, 0, 0, 0, 1]
        >>> T = Transformation.from_list(numbers)

        Notes
        -----
        Since the transformation matrix follows the row-major order, the
        translational components must be at the list's indices 3, 7, 11.
        """
        matrix = identity_matrix(4)
        for i in range(4):
            for j in range(4):
                matrix[i][j] = float(numbers[i * 4 + j])
        return cls(matrix)

    @classmethod
    def from_frame(cls, frame):
        """Computes a transformation from world XY to frame.

        Parameters
        ----------
        frame : :class:`Frame`
            A frame describing the targeted Cartesian coordinate system.

        Returns
        -------
        Transformation
            The ``Transformation`` object.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> f1 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame(f1)
        >>> f2 = Frame.from_transformation(T)
        >>> f1 == f2
        True

        Notes
        -----
        It is the same as from_frame_to_frame(Frame.worldXY(), frame).

        """
        return cls(matrix_from_frame(frame))

    @classmethod
    def from_frame_to_frame(cls, frame_from, frame_to):
        """Computes a transformation between two frames.

        This transformation allows to transform geometry from one Cartesian
        coordinate system defined by "frame_from" to another Cartesian
        coordinate system defined by "frame_to".

        Parameters
        ----------
        frame_from : :class:`Frame`
            A frame defining the original Cartesian coordinate system.
        frame_to : :class:`Frame`
            A frame defining the targeted Cartesian coordinate system.

        Returns
        -------
        Transformation
            The ``Transformation`` object representing a change of basis.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> f1 = Frame([2, 2, 2], [0.12, 0.58, 0.81], [-0.80, 0.53, -0.26])
        >>> f2 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame_to_frame(f1, f2)
        >>> f1.transform(T)
        >>> f1 == f2
        True
        """
        T1 = cls.from_frame(frame_from)
        T2 = cls.from_frame(frame_to)
        return cls(multiply_matrices(T2.matrix, matrix_inverse(T1.matrix)))

    @classmethod
    def change_basis(cls, frame_from, frame_to):
        """Computes a change of basis transformation between two frames.

        A basis change is essentially a remapping of geometry from one
        coordinate system to another.

        Parameters
        ----------
        frame_from : :class:`Frame`
            A frame defining the original Cartesian coordinate system.
        frame_to : :class:`Frame`
            A frame defining the targeted Cartesian coordinate system.

        Examples
        --------
        >>> from compas.geometry import Point, Frame
        >>> f1 = Frame([2, 2, 2], [0.12, 0.58, 0.81], [-0.80, 0.53, -0.26])
        >>> f2 = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.change_basis(f1, f2)
        >>> p_f1 = Point(1, 1, 1)  # point in f1
        >>> p_f1.transformed(T)  # point represented in f2
        Point(1.395, 0.955, 1.934)
        >>> Frame.local_to_local_coords(f1, f2, p_f1)
        Point(1.395, 0.955, 1.934)
        """
        T1 = cls.from_frame(frame_from)
        T2 = cls.from_frame(frame_to)
        return cls(multiply_matrices(matrix_inverse(T2.matrix), T1.matrix))

    @property
    def rotation(self):
        """Returns the rotation components of the transformation matrix.
        """
        Sc, Sh, R, T, P = self.decomposed()
        return R

    @property
    def translation(self):
        """Returns the translation components of the transformation matrix.
        """
        return translation_from_matrix(self.matrix)

    @property
    def scale(self):
        """Returns the scale components of the transformation matrix.
        """
        return [self.matrix[0][0], self.matrix[1][1], self.matrix[2][2]]

    @property
    def basis(self):
        """Returns the basis vectors from the ``Rotation`` component of the ``Transformation``.
        """
        from compas.geometry import Vector
        sc, sh, a, t, p = decompose_matrix(self.matrix)
        R = matrix_from_euler_angles(a, static=True, axes='xyz')
        xv, yv = basis_vectors_from_matrix(R)
        return Vector(*xv), Vector(*yv)

    @property
    def list(self):
        """Flattens the 4x4 transformation matrix into a list of 16 numbers.
        """
        return [a for c in self.matrix for a in c]

    def transpose(self):
        """Transpose the matrix of this transformation.

        Returns
        -------
        None
            The transformation is transposed in-place.
        """
        self.matrix = transpose_matrix(self.matrix)

    def transposed(self):
        """Create a transposed copy of this transformation.

        Returns
        -------
        T: :class:`compas.geometry.Transformation`
            The transposed transformation object.
        """
        T = self.copy()
        T.transpose()
        return T

    def invert(self):
        """Invert this transformation."""
        self.matrix = matrix_inverse(self.matrix)

    def inverse(self):
        """Returns the inverse transformation.

        Returns
        -------
        Transformation
            The inverse transformation.

        Examples
        --------
        >>> from compas.geometry import Frame
        >>> f = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])
        >>> T = Transformation.from_frame(f)
        >>> I = Transformation(identity_matrix(4))
        >>> I == T * T.inverse()
        True

        """
        T = self.copy()
        T.invert()
        return T

    inverted = inverse

    def determinant(self):
        """The determinant of the matrix of the transformation.

        Returns
        -------
        float
            The determinant of the matrix of this transformation.
        """
        return matrix_determinant(self.matrix)

    def decomposed(self):
        """Decompose the ``Transformation`` into its ``Scale``, ``Shear``,
        ``Rotation``, ``Translation`` and ``Perspective`` components.

        Returns
        -------
        5-tuple of Transformation
            The scale, shear, rotation, tranlation, and projection components
            of the current transformation.

        Examples
        --------
        >>> trans1 = [1, 2, 3]
        >>> angle1 = [-2.142, 1.141, -0.142]
        >>> scale1 = [0.123, 2, 0.5]
        >>> T1 = Translation.from_vector(trans1)
        >>> R1 = Rotation.from_euler_angles(angle1)
        >>> S1 = Scale.from_factors(scale1)
        >>> M = (T1 * R1) * S1
        >>> Sc, Sh, R, T, P = M.decomposed()
        >>> S1 == Sc
        True
        >>> R1 == R
        True
        >>> T1 == T
        True
        """
        from compas.geometry import Scale  # noqa: F811
        from compas.geometry import Shear
        from compas.geometry import Rotation  # noqa: F811
        from compas.geometry import Translation  # noqa: F811
        from compas.geometry import Projection
        sc, sh, a, t, p = decompose_matrix(self.matrix)
        Sc = Scale.from_factors(sc)
        Sh = Shear.from_entries(sh)
        R = Rotation.from_euler_angles(a, static=True, axes='xyz')
        T = Translation.from_vector(t)
        P = Projection.from_entries(p)
        return Sc, Sh, R, T, P

    def concatenate(self, other):
        """Concatenate another transformation to this transformation.

        Parameters
        ----------
        other: :class:`compas.geometry.Transformation`
            The transformation object to concatenate.

        Returns
        -------
        None
            This transformation object is changed in-place.

        Notes
        -----
        Rz * Ry * Rx means that Rx is first transformation, Ry second, and Rz third.
        """
        self.matrix = multiply_matrices(self.matrix, other.matrix)

    def concatenated(self, other):
        """Concatenate two transformations into one ``Transformation``.

        Parameters
        ----------
        other: :class:`compas.geometry.Transformation`
            The transformation object to concatenate.

        Returns
        -------
        T: :class:`compas.geometry.Transformation`
            The new transformation that is the concatenation of this one and the other.

        Notes
        -----
        Rz * Ry * Rx means that Rx is first transformation, Ry second, and Rz third.
        """
        cls = type(self)
        if isinstance(other, cls):
            return cls(multiply_matrices(self.matrix, other.matrix))
        return Transformation(multiply_matrices(self.matrix, other.matrix))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas.geometry import Translation  # noqa: F401
    from compas.geometry import Rotation  # noqa: F401
    from compas.geometry import Scale  # noqa: F401
    from compas.geometry import Frame  # noqa: F401

    import doctest
    doctest.testmod(globs=globals())

    world = Frame.worldXY()
    frame = Frame([1.0, 1.0, 1.0], [0, 0, -1], [1, 0, 0])

    X1 = Transformation.from_frame_to_frame(world, frame)
    X2 = Transformation.from_frame(frame)
    X3 = Transformation.change_basis(frame, world)

    print(X1.matrix)
    print(X2.matrix)
    print(X3.matrix)
