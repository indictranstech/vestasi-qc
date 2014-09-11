# Copyright (c) 2013, Indictrans technologies Pvt Ltd and Contributors
# See license.txt

import frappe
import unittest

test_records = frappe.get_test_records('Grade')

class TestGrade(unittest.TestCase):
	pass
