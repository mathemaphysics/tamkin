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
# "Vibrational Modes in partially optimized molecular systems.", An Ghysels,
# Dimitri Van Neck, Veronique Van Speybroeck, Toon Verstraelen and Michel
# Waroquier, Journal of Chemical Physics, Vol. 126 (22): Art. No. 224102, 2007
# DOI:10.1063/1.2737444
#
# "Cartesian formulation of the Mobile Block Hesian Approach to vibrational
# analysis in partially optimized systems", An Ghysels, Dimitri Van Neck and
# Michel Waroquier, Journal of Chemical Physics, Vol. 127 (16), Art. No. 164108,
# 2007
# DOI:10.1063/1.2789429
#
# "Calculating reaction rates with partial Hessians: validation of the MBH
# approach", An Ghysels, Veronique Van Speybroeck, Toon Verstraelen, Dimitri Van
# Neck and Michel Waroquier, Journal of Chemical Theory and Computation, Vol. 4
# (4), 614-625, 2008
# DOI:10.1021/ct7002836
#
# "Mobile Block Hessian approach with linked blocks: an efficient approach for
# the calculation of frequencies in macromolecules", An Ghysels, Veronique Van
# Speybroeck, Ewald Pauwels, Dimitri Van Neck, Bernard R. Brooks and Michel
# Waroquier, Journal of Chemical Theory and Computation, Vol. 5 (5), 1203-1215,
# 2009
# DOI:10.1021/ct800489r
#
# "Normal modes for large molecules with arbitrary link constraints in the
# mobile block Hessian approach", An Ghysels, Dimitri Van Neck, Bernard R.
# Brooks, Veronique Van Speybroeck and Michel Waroquier, Journal of Chemical
# Physics, Vol. 130 (18), Art. No. 084107, 2009
# DOI:10.1063/1.3071261
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


from tamkin import *

import unittest, numpy
import pylab

__all__ = ["NMAToolsTestCase"]


class NMAToolsTestCase(unittest.TestCase):

    def test_load_coordinates_charmm(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor", "input/an/ethanol.hess.full")
        coordinates, masses, symbols = load_coordinates_charmm("input/an/ethanol.cor")
        for at in range(9):
            self.assertAlmostEqual(molecule.masses[at], masses[at], 3)
            for j in range(3):
                self.assertAlmostEqual(molecule.coordinates[at,j], coordinates[at,j], 3)

    def test_load_modes_charmm(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor", "input/an/ethanol.hess.full")

        # full Hessian
        nma = NMA(molecule)
        modes2, freqs2, masses2 = load_modes_charmm("input/an/ethanol.modes.full")
        for index in range(6,27):
            for j in range(27):
                self.assertAlmostEqual(abs(nma.modes[j,index]), abs(modes2[j,index]), 7)
        for at in range(27):
            self.assertAlmostEqual(nma.freqs[at], freqs2[at], 7)

        # MBH
        nma = NMA(molecule, MBH([[5,6,7,8]]))
        modes2, freqs2, masses2 = load_modes_charmm("input/an/ethanol.modes.mbh")
        for index in range(6,21):
            for j in range(27):
                self.assertAlmostEqual(abs(nma.modes[j,index]), abs(modes2[j,index]), 7)
        for at in range(21):
            self.assertAlmostEqual(nma.freqs[at], freqs2[at], 7)


    def test_overlap(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor","input/an/ethanol.hess.full")
        nma1 = NMA(molecule)
        fixed = load_fixed_txt("input/an/fixed.06.txt")
        nma2 = NMA(molecule, PHVA(fixed))
        overlap = compute_overlap(nma1, nma2)
        overlap = compute_overlap((nma1.modes, nma1.freqs), (nma2.modes, nma2.freqs))
        overlap = compute_overlap(nma1.modes, nma2.modes)
        overlap = compute_overlap(nma1.modes[:,0], nma2.modes[:,0])
        # TODO
        #self.assertAlmostEqual()


    def test_delta_vector(self):
        # from charmmcor
        coor1,masses1,symb1 = load_coordinates_charmm("input/an/ethanol.cor")
        coor2,masses2,symb2 = load_coordinates_charmm("input/an/ethanol.2.cor")
        delta = compute_delta(coor1, coor2)
        # TODO
        #self.assertAlmostEqual()
        delta = compute_delta(coor1, coor2, masses=masses1, normalize=True)
        #self.assertAlmostEqual()

    def test_eigenvalue_sensitivity(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor","input/an/ethanol.hess.full")
        nma = NMA(molecule)
        for i in range(7,27):
            sensit = compute_sensitivity_freq(nma, i)
            self.assertAlmostEqual(numpy.sum((numpy.dot(sensit,nma.modes)-nma.modes)**2,0)[i],0.0,9)



    def test_create_blocks_peptide_charmm(self):
        blocks1 = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH("RTB",blocksize=1))
        blocks2 = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH("RTB",blocksize=2))
        self.assertEqual(len(blocks1)/2+1, len(blocks2))
        subs1 = create_subs_peptide_charmm("input/charmm/crambin.crd", SubsPeptideVSA(frequency=1))
        subs2 = create_subs_peptide_charmm("input/charmm/crambin.crd", SubsPeptideVSA(frequency=2))
        self.assertEqual(len(subs1)/2, len(subs2))

        blocks = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH())
        self.assertEqual(len(blocks), 91)
        blocks = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH("dihedral"))
        self.assertEqual(len(blocks), 91)
        blocks = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH("RHbending"))
        self.assertEqual(len(blocks),136)
        blocks = create_blocks_peptide_charmm("input/charmm/crambin.crd", BlocksPeptideMBH("normal"))
        self.assertEqual(len(blocks), 91)

    def test_writing(self):
        subs = range(10)
        selectedatoms_write_to_file(subs, "output/subs-atoms.1.txt", shift=0)
        selectedatoms_write_to_file(subs, "output/subs-atoms.2.txt", shift=1)
        selectedatoms_write_to_file(subs, "output/subs-atoms.3.txt")

        subs1 = load_subs_txt("output/subs-atoms.1.txt", shift=0)
        self.assertEqual(len(subs),len(subs1))
        for (i,j) in zip(subs,subs1):
            self.assertEqual(i,j)
        subs2 = load_subs_txt("output/subs-atoms.2.txt", shift=-1)
        self.assertEqual(len(subs),len(subs2))
        for i,j in zip(subs,subs2):
            self.assertEqual(i,j)
        subs22 = load_subs_txt("output/subs-atoms.2.txt")  # should not matter
        self.assertEqual(len(subs),len(subs22))
        for i,j in zip(subs,subs22):
            self.assertEqual(i,j)
        subs3 = load_subs_txt("output/subs-atoms.3.txt")
        self.assertEqual(len(subs),len(subs3))
        for i,j in zip(subs,subs3):
            self.assertEqual(i,j)

        blocks = [range(10), range(10,20)]
        blocks_write_to_file(blocks, "output/blocks.1.txt", shift=0)
        blocks_write_to_file(blocks, "output/blocks.2.txt", shift=1)
        blocks_write_to_file(blocks, "output/blocks.3.txt")

        blocks1 = load_blocks_txt("output/blocks.1.txt", shift=0)
        self.assertEqual(len(blocks),len(blocks1))
        for bl,bl1 in zip(blocks,blocks1):
            for i,j in zip(bl,bl1):
                self.assertEqual(i,j)
        blocks2 = load_blocks_txt("output/blocks.2.txt", shift=-1)
        self.assertEqual(len(blocks),len(blocks2))
        for bl,bl1 in zip(blocks,blocks2):
            for i,j in zip(bl,bl1):
                self.assertEqual(i,j)
        blocks22 = load_blocks_txt("output/blocks.2.txt")  # should not matter
        self.assertEqual(len(blocks),len(blocks2))
        for bl,bl1 in zip(blocks,blocks2):
            for i,j in zip(bl,bl1):
                self.assertEqual(i,j)
        blocks3 = load_blocks_txt("output/blocks.3.txt")
        self.assertEqual(len(blocks),len(blocks3))
        for bl,bl1 in zip(blocks,blocks3):
            for i,j in zip(bl,bl1):
                self.assertEqual(i,j)

    def test_plot_spectrum(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor", "input/an/ethanol.hess.full")
        nma = NMA(molecule)
        plot_spectrum("lines","output/spectrum-lines.1.png", [nma.freqs, nma.freqs], title="standard settings")
        plot_spectrum("lines","output/spectrum-lines.2.png", [nma.freqs, nma.freqs], min=-10.0, max=500.0, title="zoom")

        plot_spectrum("dos","output/spectrum-dos.1.png", [nma.freqs], title="standard settings")
        plot_spectrum("dos","output/spectrum-dos.2.png", [nma.freqs], min=-10.0, max=1500.0, title="zoom")
        plot_spectrum("dos","output/spectrum-dos.3.png", [nma.freqs], min=-10.0, max=1500.0, width=50.0, title="width")
        plot_spectrum("dos","output/spectrum-dos.4.png", [nma.freqs], min=-10.0, max=1500.0, width=50.0, step=20.0, title="step size")
        plot_spectrum("dos","output/spectrum-dos.5.png", [nma.freqs, nma.freqs*1.1], title="two spectra")
        plot_spectrum("dos","output/spectrum-dos.6.png", [nma.freqs, nma.freqs*1.1], amplitudes=[1.0,2.0], title="different amplitude")


    def test_create_enm_molecule(self):
        molecule = load_molecule_charmm("input/an/ethanol.cor", "input/an/ethanol.hess.full")
        selected = range(5)
        mol = create_enm_molecule(molecule, selected)
        nma = NMA(mol)

        mol = create_enm_molecule(molecule.coordinates, rcut=5)
        nma = NMA(mol)

        mol = create_enm_molecule(molecule.coordinates, selected, masses=numpy.ones(molecule.size)*2.0, rcut=5)
        nma = NMA(mol)

