# -*- coding: utf-8 -*-
# TAMkin is a post-processing toolkit for thermochemistry and kinetics analysis.
# Copyright (C) 2008-2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>,
# Matthias Vandichel <Matthias.Vandichel@UGent.be> and
# An Ghysels <An.Ghysels@UGent.be>, Center for Molecular Modeling (CMM), Ghent
# University, Ghent, Belgium; all rights reserved unless otherwise stated.
#
# This file is part of TAMkin.
#
# TAMkin is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following five articles:
#
# "TAMkin: A Versatile Package for Vibrational Analysis and Chemical Kinetics",
# An Ghysels, Toon Verstraelen, Karen Hemelsoet, Michel Waroquier and Veronique
# Van Speybroeck, Journal of Chemical Information and Modeling, Articles ASAP
# (As Soon As Publishable)
# http://dx.doi.org/10.1021/ci100099g
#
# TAMkin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

import numpy, sys

from molmod.units import bar, liter, meter, mol, second, kjmol
from molmod.constants import boltzmann

__all__ = [
    "load_summary", "get_error_color",
    "temps", "invtemps", "experimental_k", "experimental_lnk", "experimental_A",
    "experimental_Ea", "covariance_parameters", "experimental_parameters",
]


def load_summary(fn):
    """Load a kinetics summary file

       Arguments:
         fn  --  a filename

       Returns:
         ks  --  The rate coefficients at 300, 400, 500 amd 600 K
         (A, Ea)  --  The pre-exponential factor and the activation energy
         E0, E  --  The zero-point corrected barrier and the classical barrier
    """
    f = file(fn)
    result = tuple(float(word) for word in f.next().split())
    f.close()
    return result[:-4], result[-4:-2], result[-2:]


def get_error_color(ratio):
    x = abs(ratio)
    if x < 1:
        rgb = (x,1.0,0.0)
    elif x < 2:
        rgb = (1.0,2.0-x,0.0)
    elif x < 3:
        rgb = ((4-x)/2,0.0,(x-2.0)/2)
    else:
        rgb = (0.5,0.0,0.5)
    result = "#%s" % "".join(hex(int(c*255))[2:].rjust(2,"0") for c in rgb)
    return result


temps = numpy.array([300, 400, 500, 600], float)
#temps = numpy.arange(300.0, 601.0, 10.0)
invtemps = 1/temps
N = len(temps)

centimeter = meter*0.01
experimental_k = 7.19e-15 * (temps/298)**2.44*numpy.exp(-22.45*kjmol/(boltzmann*temps))
experimental_k *= (centimeter**3/second)
experimental_k /= (meter**3/mol/second)
experimental_lnk = numpy.log(experimental_k)
print "unit conversion: %e" % (7.19e-15*(centimeter**3/second)/(meter**3/mol/second))
print "experimental_k:"
print experimental_k
print "experimental_lnk:"
print experimental_lnk

# fit experimental A and Ea and also sensitivity to errors

design_matrix = numpy.array([numpy.ones(N), -invtemps/boltzmann*kjmol]).transpose()
expected_values = experimental_lnk

A = numpy.dot(design_matrix.transpose(), design_matrix)
B = numpy.dot(design_matrix.transpose(), expected_values)

experimental_parameters = numpy.linalg.solve(A, B)
experimental_A = numpy.exp(experimental_parameters[0])
experimental_Ea = experimental_parameters[1]
covariance_lnk = numpy.ones((N,N),float)*numpy.log(10)**2 + numpy.identity(N,float)*numpy.log(2)**2
#covariance_lnk = numpy.identity(4,float)*numpy.log(10)**2
sensitivity = numpy.linalg.solve(A, design_matrix.transpose())
covariance_parameters = numpy.dot(numpy.dot(sensitivity, covariance_lnk), sensitivity.transpose())

print "experimental_A: %e" % experimental_A
print "experimental_Ea", experimental_Ea
#sys.exit()
# done fitting
