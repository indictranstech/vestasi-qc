# Copyright (c) 2013, Indictrans technologies Pvt Ltd and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

test_records = frappe.get_test_records('Charge Number')

class TestChargeNumber(unittest.TestCase):
	pass
