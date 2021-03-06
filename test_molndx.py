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
Unit tests for the molndx module.
"""

import os
import tempfile
from unittest import TestCase, main
from copy import copy
from subprocess import Popen, PIPE, STDOUT

import molndx

TEST_DIR = "test_resources"

class TestMolndx(TestCase) :
    """
    Run tests for molndx as a module.
    """
    def setUp(self) :
        self.read_reference = {
            "group1" : range(1, 100),
            "group2" : range(100, 200),
        }
        self.group_reference = copy(self.read_reference.keys())

        self.group_reference.sort()

    def test_read_regular(self) :
        """
        Test the reading of a regular file
        
        Read a file without any strange thing like comments of empty groups.
        """
        file_name = os.path.join(TEST_DIR, "test_index_regular.ndx")
        check_content(file_name, self.read_reference, self.group_reference)

    def test_read_empty_file(self) :
        """
        Test reading an empty file
        """
        file_name = os.path.join(TEST_DIR, "test_index_empty.ndx")
        index, groups = molndx.read_ndx(open(file_name))
        self.assertEqual(len(index), 0, "Dictionary should be empty.")
        self.assertEqual(len(groups), 0, "Group name list should be empty.")

    def test_read_empty_group(self) :
        """
        Test reading an empty group
        """
        file_name = os.path.join(TEST_DIR, "test_index_empty_group.ndx")
        index, groups = molndx.read_ndx(open(file_name))
        self.assertEqual(len(index["group1"]), 0, "Group should be empty.")
        self.assertEqual(groups[0], "group1", "Group name is wrong.")

    def test_read_comment_lines(self) :
        """
        Test reading in presence of comment lines
        """
        file_name = os.path.join(TEST_DIR, "test_index_comment_lines.ndx")
        check_content(file_name, self.read_reference, self.group_reference)

    def test_read_comment_inline(self) :
        """
        Test reading in presence of inline comments
        """
        file_name = os.path.join(TEST_DIR, "test_index_comment_inline.ndx")
        check_content(file_name, self.read_reference, self.group_reference)

    def test_read_write_no_groups(self) :
        """
        Test if the writing works when no group filter is provided.

        It is assumed that reading works. But there is enough tests above to
        assume that, isn't it ?
        """
        tmp = tempfile.mkstemp()[1]
        with open(tmp, "w") as doc :
            molndx.write_ndx(self.read_reference, doc)
        index, groups = molndx.read_ndx(open(tmp))
        self.assertEqual(index, self.read_reference,
                "Dictionary do not match. See %s." % tmp)
        groups.sort()
        self.assertEqual(groups, self.group_reference,
                "Group list do not match. See %s." % tmp)
        # The temporary file is deleted only if the test pass
        os.remove(tmp)

    def test_read_write_all_groups(self) :
        """
        Test if the writing works when all the groups are provided.

        It is assumed that reading works. But there is enough tests above to
        assume that, isn't it ?
        """
        tmp = tempfile.mkstemp()[1]
        with open(tmp, "w") as doc :
            molndx.write_ndx(self.read_reference, doc, self.group_reference)
        index, groups = molndx.read_ndx(open(tmp))
        self.assertEqual(index, self.read_reference,
                "Dictionary do not match. See %s." % tmp)
        self.assertEqual(groups, self.group_reference,
                "Group list do not match. See %s." % tmp)
        # The temporary file is deleted only if the test pass
        os.remove(tmp)

    def test_read_write_extra_groups(self) :
        """
        Test if the writing works when to many groups are provided.

        It is assumed that reading works. But there is enough tests above to
        assume that, isn't it ?
        """
        tmp = tempfile.mkstemp()[1]
        groups = copy(self.group_reference) + ["group3"]
        with open(tmp, "w") as doc :
            molndx.write_ndx(self.read_reference, doc, groups)
        index, groups = molndx.read_ndx(open(tmp))
        self.assertEqual(index, self.read_reference,
                "Dictionary do not match. See %s." % tmp)
        self.assertEqual(groups, self.group_reference,
                "Group list do not match. See %s." % tmp)
        # The temporary file is deleted only if the test pass
        os.remove(tmp)

class TestPlugin(TestCase) :
    """
    Run tests for molndx in the context of Pymol.
    """
    def test_run(self) :
        """
        In python, load the plugin.
        """
        tmp = tempfile.mkstemp(suffix=".pml")[1]
        with open(tmp, "w") as pml :
            print >> pml, "run molndx.py"
            print >> pml, "quit"
        status, output = pymol(tmp)
        self.assertFalse("Traceback" in output)
        os.remove(tmp)

    def test_write(self) :
        """
        In python, do some selections and write them.
        """
        tmp = tempfile.mkstemp(suffix=".pml")[1]
        tmp_ndx = tempfile.mkstemp()[1]
        with open(tmp, "w") as pml :
            print >> pml, "load %s/1BTA.pdb" % TEST_DIR
            print >> pml, "select res1, resid 1"
            print >> pml, "select res2, resid 20"
            print >> pml, "run molndx.py"
            print >> pml, "ndx_save %s" % tmp_ndx
            print >> pml, "quit"
        pymol(tmp)
        compare_ndx(tmp_ndx, os.path.join(TEST_DIR, "ref_1BTA.ndx"))
        os.remove(tmp_ndx)
        os.remove(tmp)

    def test_load_write(self) :
        """
        In python, load a file, write the selection and check consistency.
        """
        tmp = tempfile.mkstemp(suffix=".pml")[1]
        tmp_ndx = tempfile.mkstemp()[1]
        with open(tmp, "w") as pml :
            print >> pml, "load %s/1BTA.pdb" % TEST_DIR
            print >> pml, "run molndx.py"
            print >> pml, "ndx_load %s" % os.path.join(TEST_DIR, "ref_1BTA.ndx")
            print >> pml, "ndx_save %s" % tmp_ndx
            print >> pml, "quit"
        pymol(tmp)
        compare_ndx(tmp_ndx, os.path.join(TEST_DIR, "ref_1BTA.ndx"))
        os.remove(tmp_ndx)
        os.remove(tmp)

    def test_internal_external(self) :
        """
        Check that there is no regression about issue #2.
        
        The system in start.pdb showed that there can be a discrepency between
        the atom order in the input pdb file and the internal order in Pymol.
        
        The order in Pymol can be access through the "index" selection keyword
        when the PDB order is accessed by the "id" one.

        This test aim to check if the right atoms are selected when the internal
        and external order are different.
        """
        tmp = tempfile.mkstemp(suffix=".pml")[1]
        with open(tmp, "w") as pml :
            print >> pml, "load %s/start.pdb" % TEST_DIR
            print >> pml, "run molndx.py"
            print >> pml, "ndx_load %s" % os.path.join(TEST_DIR, "layers.ndx")
            print >> pml, "iterate Top_layer, print name"
        status, output = pymol(tmp)
        self.assertEqual(output.count("PO4"), 144,
            "All the atoms do not have the expected name.")
        os.remove(tmp)


def check_content(infile, reference_dict, reference_list) :
    """
    Read an index file and check if its content is the same as the
    reference.

    :Parameters:
        - infile: the path to an index file to read
        - reference_dict: the index dictionary to compare with
        - reference_list: the group list to compare with
    """
    index, groups = molndx.read_ndx(open(infile))
    assert index == reference_dict,\
            "Incorrect group dictionary.\n%s" % str(index)
    assert groups == reference_list,\
            "Incorrect group name list.\n%s" % str(groups)

def compare_ndx(infile_A, infile_B) :
    """
    Assert that two ndx files have the same content.
    """
    index_A, groups_A = molndx.read_ndx(open(infile_A))
    index_B, groups_B = molndx.read_ndx(open(infile_B))
    assert index_A == index_B,\
            ("Group dictionaries are not matching."
             "See %s and %s." % (infile_A, infile_B))
    assert groups_A == groups_B,\
            ("Group name lists are nor matching."
             "See %s and %s." % (infile_A, infile_B))

def pymol(pml) :
    """
    Run pymol in batch mode with a PML file.

    :Paramaters:
        - pml: the path to the PML file to run Pymol with

    :Returns:
        - the Pymol exit status
    """
    process = Popen(["pymol", "-c", pml], stdout=PIPE, stderr=STDOUT)
    status = process.wait()
    output = process.communicate()[0]
    print output
    assert status == 0, "Pymol exit status is not 0"
    return status, output

if __name__ == "__main__" :
    main()
