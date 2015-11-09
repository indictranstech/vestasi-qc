# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	frappe.errprint(data)
	columns = get_columns()
	return columns, data

def get_data(filters):
	condition = get_condition(filters)
	data = frappe.db.sql(""" select a.name, a.item_code, a.qty, a.grade, a.serial_no_warehouse,
		b.fe, b.ca, b.al,b.c, b.alpha, b.o2, b.free_si, b.d10,b.d30,b.d50, b.d90,b.d100, b.mesh_625,
		b.ssa, a.serial_no_details from `tabSerial No` a left join `tabQuality Paramter Values` b on a.name = b.parent where %s and ifnull(a.qty,0)>0"""%(condition), as_list = 1)
	return data

def get_condition(filters):
	condition = '1=1'

	if filters.get('item_code') : condition += " and a.item_code = '%s'"%(filters.get('item_code'))
	if filters.get('grade') : condition += " and a.grade like '%%%s%%'"%(filters.get('grade'))
	if filters.get('drum_from') : condition += " and a.name >= '%s'"%(filters.get('drum_from'))
	if filters.get('drum_to') : condition += " and a.name <= '%s'"%(filters.get('drum_to'))
	if filters.get('warehouse') : condition += " and a.serial_no_warehouse = '%s'"%(filters.get('warehouse'))

	return condition

def get_columns():
	columns = [
		"Drum or Bag:Link/Serial No:100", "Item Code:Link/Item:120", "Qty:Float:70", 
		"Grade::60", "Location:Link/Warehouse:120", "Fe:Float:40",
		"Ca:Float:40", "Al:Float:40", "C:Float:40", 
		"Alpha:Float:40", "O2:Float:40", "Free Si:Float:40", "D10:Float:40", "d30:Float:40",
		"D10:Float:40", "d30:Float:40",
		"D100:Float:40", "MESH 635:Float:40","SSA:Float:40", "Remark::50"
	]
	return columns
