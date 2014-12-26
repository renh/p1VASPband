#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module imports
from __future__ import print_function
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl
#==============================================================================

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path',
                    help='Path to working directory', default='.')
parser.add_argument('-o', '--output',
                    help='Output base filename', default='band')
parser.add_argument('-f', '--format', nargs='+',
                    help='A list of figure formats', default=['pdf'])

parser.add_argument('-d', '--direction',
                    help='High symmetric direction', default='z')
parser.add_argument('-b', '--below',
                   help='Lower energy bound below Fermi level', type=float,
                   default=5.0)
parser.add_argument('-a', '--above',
                   help='Upper energy bound above Fermi level', type=float,
                   default=5.0)
parser.add_argument('-s', '--show',
                   help='show interactive band structures',
                   action='store_true')
args = parser.parse_args()

path = args.path
outcar = os.path.join(path, 'OUTCAR')
eigval = os.path.join(path, 'EIGENVAL')
of_dat = os.path.join(path, args.output+'.'+'dat')
directions = {'x':0, 'y':1, 'z':2}
direction = directions[args.direction]
lb = args.below
ub = args.above

# Read Fermi energy and nspin from OUTCAR
try:
    outcar_fh = open(outcar, 'r')
except IOError as e:
    print("I/O error({}): {}".format(e.errno, e.strerror))
    raise SystemExit

try:
    eigval_fh = open(eigval, 'r')
except IOError as e:
    print("I/O error({}): {}".format(e.errno, e.strerror))
    raise SystemExit

for l in outcar_fh:
    if l.startswith('   ISPIN'):
        break
else:
    print("ISPIN value not found in {}, exit...".format(outcar))
    raise SystemExit
nspin = int(l.split()[2])

while 1:
    l = outcar_fh.next()
    if l.startswith(' E-fermi'):
        break
else:
    print('E-fermi value not found in {}, exit...'.format(outcar))
    raise SystemExit
EFermi = float(l.split()[2])

outcar_fh.close()

# Read eigenvalues from EIGENVAL
for i in range(5):
    eigval_fh.next()

l = eigval_fh.next()
dump, nk, nb = [int(x) for x in l.split()]

eig = np.zeros([nb, nk, nspin])
kpts = np.zeros([nk,3])

for ik in range(nk):
    eigval_fh.next()
    l = eigval_fh.next()
    kpts[ik] = [float(x) for x in l.split()[:3]]
    for ib in range(nb):
        l = eigval_fh.next()
        eig[ib,ik] = [float(x) for x in l.split()[1:]]
eigval_fh.close()
eig -= EFermi


# Write band data
of_fh = open(of_dat, 'w')

fmt_str = "{:15.7E}" + "{:14.6F}" * nspin + '\n'

for ib in range(nb):
    for ik in range(nk):
        l = fmt_str.format(
            kpts[ik,direction],
            *eig[ib,ik]
        )
        of_fh.write(l)
    of_fh.write('\n')
of_fh.close()

# check high symmetric direction and raise warning if necessary
small = 1.0E-4
if abs(kpts[0,direction] - kpts[-1,direction]) < small:
    print('Warning: K-Points coordinates does not change as expected.')
    print('         I am treating with the {} direction in the k-space'.format(
        args.direction))
    print('         cooresponding to Column {} of the kpts coordiantes.'.format(
        direction))
    print("         I've written data into the output file:\n\n\t{}".format(of_dat))
    print('\nYou can check the help info for details: {} -h'.format(sys.argv[0]))
    print('\nIt is too difficult to plot such a band structure...\nsorry,\nbye...')
    raise SystemExit

# plot band structure
#mpl.rc('text',usetex=True)
#mpl.rcParams['text.latex.preamble'] = [
#           r'\usepackage{siunitx}',   # i need upright \micro symbols, but you need...
#           r'\sisetup{detect-all}',   # ...this to force siunitx to actually use your fonts
#           r'\usepackage{helvet}',    # set the normal font here
#           r'\usepackage{sansmath}',  # load up the sansmath so that math -> helvet
#           r'\sansmath'               # <- tricky! -- gotta actually tell tex to use!
#]  

fig, ax = plt.subplots(1, 1, sharex = True, figsize=(3.5,6))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)
colors = ['r','b']

ax.set_xlim([kpts[0,direction], kpts[-1,direction]])
ax.set_ylim([-lb, ub])

for ispin in range(nspin):
    for ib in range(nb):
        ax.plot(kpts[:,direction],eig[ib,:,ispin], '{}'.format(colors[ispin]),
               linewidth=1, alpha=0.8)

for y in range(int(-lb+1),int(+ub)):
    ax.plot(kpts[(0,-1),direction],[y,y],'k--',linewidth=0.5,alpha=0.5)

ax.set_xticks(kpts[(0,-1),direction])
ax.set_xticklabels([r'$\Gamma$', r'$\mathrm{X}$'])
ax.set_yticks(range(int(-lb+1),int(+ub),2))
ax.set_yticklabels(range(int(-lb+1),int(+ub),2))
mly = MultipleLocator(0.5)
ax.yaxis.set_minor_locator(mly)

ax.set_ylabel(r'$\mathsf{E - \mathrm{\mathsf{E_F}} (eV)}$',fontsize=14)

plt.tight_layout()
for fmt in args.format:
    of_fig = os.path.join(path, args.output+'.'+fmt)
    plt.savefig(of_fig)
if args.show:
    plt.show()



