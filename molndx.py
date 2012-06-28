#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by   
# the Free Software Foundation, either version 3 of the License, or      
# (at your option) any later version.                                    
#                                                                       
# This program is distributed in the hope that it will be useful,        
# but WITHOUT ANY WARRANTY; without even the implied warranty of         
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          
# GNU General Public License for more details.                           
#                                                                           
# A copy of the GNU General Public License is available at
# http://www.gnu.org/licenses/gpl-3.0.html.

 
"""
Pymol plugin to handle GROMACS index (.ndx) files.

This plugin allow to load Pymol selections from an index file and to store
Pymol selections into an index file.

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

    ; This is a commented line
    [ group_name_2 ]
    1 2 3 ; The end of a line can be commented
    4 5 6
"""

__author__ = "Jonathan Barnoud <jonathan@barnoud.net>"

# If we are in Pymol then we need to load the API
try :
    from pymol import cmd
except (ImportError, KeyError):
    is_pymol = False
else :
    is_pymol = True

from textwrap import wrap

# Life would be easier if python 2.6 would have ordereddict. Then it would have
# been trivial to store groups in the order of reading. However the ordereddict
# type is only available for python 2.6 through a external library and I don't
# want any dependency out of the standard library.

def read_ndx(infile) :
    """
    Read a GROMACS index file and return a dictionary.

    :Parameters:
        - infile : a file descriptor like instance of a ndx file

    :Return:
        - A dictionary like {group name : list of indices}.
        - The list of group names ordered as the input file.
    """
    indices = {}
    current_group = None
    groups = []
    for line in infile :
        if "[" in line :
            current_group = line
            current_group = current_group.replace("[", "")
            current_group = current_group.replace("]", "")
            current_group = current_group.strip()
            groups.append(current_group)
            indices[current_group] = []
        elif not current_group is None :
            indices[current_group] += [int(i) for i in line.split()]
    return indices, groups

def write_ndx(groups, outfile, group_filter=None) :
    """
    Write a GROMACS index file.

    :Parameters:
        - groups : a dictionary with group names as keys and list of indices
          as values.
        - outfile : a file descriptor in which will be written the indices.
        - group_filter : a list of keys of the "groups" dictionary, groups
          will be written in this order in the file, only the groups in
          group_filter will be written. If group_filter is None (default) all
          groups are written in a random order.
    """
    if group_filter is None :
        group_filter = groups.keys()
    else :
        group_filter = (group for group in group_filter if group in groups)
    for group in group_filter :
        print >> outfile, "[ %s ]" % group
        indices = " ".join((str(x) for x in groups[group]))
        print >> outfile, "\n".join(wrap(indices, width=60))

def ndx_load(infile) :
    """
    Create selections from a GROMACS index file.

    :Parameters:
        - infile : input file name
    """
    ndx, names = read_ndx(open(infile))
    print names
    for name, content in ((key, ndx[key]) for key in names) :
        # Pymol does not like & and | characters
        name = name.replace("&", "_and_")
        name = name.replace("|", "_or_")
        if len(content) > 0 :
            print "Selection of %s" % name
            # Pymol does not like long selection strings so I select the group
            # iteratively
            cmd.select(name, "index %i" % content[0])
            subcontents = (content[i:i+10] for i in xrange(1, len(content), 10))
            for subcontent in subcontents :
                selstring = "index " + "+".join(str(i) for i in subcontent)
                cmd.select(name, "%s | %s" % (name, selstring))
        else :
            print "Group %s is empty" % name
    cmd.select("none")
    print "Loading of %s done" % infile

def ndx_save(outfile) :
    """
    Save all the selections into a GROMACS index file.

    :Parameters:
        - outfile : output file name
    """
    group_names = cmd.get_names("selections")
    ndx = {}
    for group in group_names :
        storage = {'indices' : []}
        cmd.iterate(group, 'indices.append(index)', space=storage)
        ndx[group] = storage['indices']
    # Pymol will likely have a "sele" group. If this group is empty we do not
    # want it in the output file.
    if "sele" in ndx and len(ndx["sele"]) == 0 :
        del ndx["sele"]
    write_ndx(ndx, open(outfile, "w"), group_names)
    print "%s written with %i groups in it." % (outfile, len(group_names))

# If we are in Pymol then declare the new commands
if is_pymol :
    cmd.extend('ndx_load', ndx_load)
    cmd.extend('ndx_save', ndx_save)

