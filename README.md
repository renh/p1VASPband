p1VASPband
==========

# Introduction #
p1VASPband is a simple module plotting band structures of one-dimensional (1D) system from VASP band
calculation. It is written in python with numpy and matplotlib. Python 2.7 or later is required.

# Usage #
Simply run
```
$ python p1VASPband.py -h
```
for help information. Use `-d` to speicify the working directory, where the VASP output files 
`OUTCAR` and `EIGENVAL` reside.

By default, it will write a `band.dat` with the band structure flavored eigenvalues and is ready
plotting with `gnuplot`.

Figure file defaults in `pdf` format is saved if everything goes well.

