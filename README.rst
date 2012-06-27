======
Molndx
======

Molndx is a Pymol plugin to handle GROMACS index files (.ndx). It allows to save selections and to load them.

A GROMACS index file is a succession of atom groups. Each group is described by
a header defining the group name and a list of atoms. Lines can be commented
using the # character. Note that the atoms are numbered starting at 1 in the
index file.

An index file look like :

::

    [ group_name ]
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22
    23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41
    42 43 44 45

    # This is a commented line
    [ group_name_2 ]
    1 2 3 # The end of a line can be commented
    4 5 6

Usage
=====

To load the plugin just type :

    run molndx.py

The plugin gives access to two methods :

- ndx_save <output_file> : save all selections
- ndx_load <input_file> : load the selections

Licence
=======

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by   
the Free Software Foundation, either version 3 of the License, or      
(at your option) any later version.                                    
                                                                      
This program is distributed in the hope that it will be useful,        
but WITHOUT ANY WARRANTY; without even the implied warranty of         
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          
GNU General Public License for more details.                           
                                                                          
A copy of the GNU General Public License is available at
http://www.gnu.org/licenses/gpl-3.0.html.

 
