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

import os.path
from unittest import TestCase, main
from copy import copy

import molndx

TEST_DIR = "test_resources"

class TestMolndx(TestCase) :
    def setUp(self) :
        self.read_reference = {
            "group1" : range(1, 100),
            "group2" : range(100, 200),
        }
        self.group_reference = copy(self.read_reference.keys())

        self.group_reference.sort()

    def check_content(self, infile, reference_dict, reference_list) :
        """
        Read an index file and check if its content is the same as the
        reference.

        :Parameters:
            - infile: the path to an index file to read
            - reference_dict: the index dictionary to compare with
            - reference_list: the group list to compare with
        """
        index, groups = molndx.read_ndx(open(infile))
        self.assertEqual(index, reference_dict, "Incorrect group dictionary.")
        self.assertEqual(groups, reference_list, "Incorrect group name list.")

    def test_read_regular(self) :
        """
        Test the reading of a regular file
        
        Read a file without any strange thing like comments of empty groups.
        """
        file_name = os.path.join(TEST_DIR, "test_index_regular.ndx")
        self.check_content(file_name, self.read_reference, self.group_reference)

    def test_read_empty_file(self) :
        """
        Test reading an empty file
        """
        file_name = os.path.join(TEST_DIR, "test_index_empty.ndx")
        index, groups = molndx.read_ndx(open(file_name))
        self.assertEqual(len(index), 0, "Dictionary should be empty.")
        self.assertEqual(len(groups), 0, "Group name list should be empty.")

    def test_read_enpty_group(self) :
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
        self.check_content(file_name, self.read_reference, self.group_reference)

    def test_read_comment_lines(self) :
        """
        Test reading in presence of comment lines
        """
        file_name = os.path.join(TEST_DIR, "test_index_comment_inline.ndx")
        self.check_content(file_name, self.read_reference, self.group_reference)

    def test_write(self) :
        pass

    def test_read_write(self) :
        pass


if __name__ == "__main__" :
    main()
