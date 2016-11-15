#	pdfminify - Tool to minify PDF files.
#	Copyright (C) 2016-2016 Johannes Bauer
#
#	This file is part of pdfminify.
#
#	pdfminify is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pdfminify is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pdfminify; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#


#> x := Matrix([[a,b,0],[c,d,0],[e,f,1]]);
#                                                                                   [a    b    0]
#                                                                                   [           ]
#                                                                              x := [c    d    0]
#                                                                                   [           ]
#                                                                                   [e    f    1]
#
#> y := Matrix([[a_,b_,0],[c_,d_,0],[e_,f_,1]]);
#                                                                                  [a_    b_    0]
#                                                                                  [             ]
#                                                                             y := [c_    d_    0]
#                                                                                  [             ]
#                                                                                  [e_    f_    1]
#
#> evalm(x&*y);
#                                                                 [  a a_ + b c_         a b_ + b d_       0]
#                                                                 [                                         ]
#                                                                 [  c a_ + d c_         c b_ + d d_       0]
#                                                                 [                                         ]
#                                                                 [e a_ + f c_ + e_    e b_ + f d_ + f_    1]

import collections

ImageExtents = collections.namedtuple("ImageExtents", [ "x", "y", "width", "height" ])

class TransformationMatrix(object):
	def __init__(self, a, b, c, d, e, f):
		self._a = a
		self._b = b
		self._c = c
		self._d = d
		self._e = e
		self._f = f

	@property
	def a(self):
		return self._a

	@property
	def b(self):
		return self._b

	@property
	def c(self):
		return self._c

	@property
	def d(self):
		return self._d

	@property
	def e(self):
		return self._e

	@property
	def f(self):
		return self._f

	def apply(self, x, y):
		return (
			self.a * x + self.c * y + self.e,
			self.b * x + self.d * y + self.f,
		)

	def extents(self, width = 1, height = 1, scale = 1):
		(x0, y0) = self.apply(0, 0)
		(x1, y1) = self.apply(width, height)
		(width, height) = (abs(x1 - x0), abs(y1 - y0))
		(xoffset, yoffset) = (min(x0, x1), min(y0, y1))
		return ImageExtents(x = scale * xoffset, y = scale * yoffset, width = scale * width, height = scale * height)

	def __imul__(self, other):
		return TransformationMatrix(
			self.a * other.a + self.b * other.c,
			self.a * other.b + self.b * other.d,
			self.c * other.a + self.d * other.c,
			self.c * other.b + self.d * other.d,
			self.e * other.a + self.f * other.c + other.e,
			self.e * other.b + self.f * other.d + other.f,
		)

	@classmethod
	def scale(cls, scale_factor):
		return cls(scale_factor, 0, 0, scale_factor, 0, 0)

	@classmethod
	def identity(cls):
		return cls.scale(1)

	def __repr__(self):
		return str(self)

	def __str__(self):
		return "Matrix<%f %f %f %f %f %f>" % (self.a, self.b, self.c, self.d, self.e, self.f)
