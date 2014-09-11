# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters ={}
	data=frappe.db.sql("""select a.t_warehouse, 
		(select batch_no from `tabSerial No` where name in (select serial_no from `tabWarehouse` where name=a.t_warehouse)) as batch,
		(select qty from `tabSerial No` where name in (select serial_no from `tabWarehouse` where name=a.t_warehouse)) as qty,
		(select grade from `tabSerial No` where name in (select serial_no from `tabWarehouse` where name=a.t_warehouse)) as grade,
		(select qc_status from `tabSerial No` where name in (select serial_no from `tabWarehouse` where name=a.t_warehouse)) as status 
		from `tabStock Entry Detail` as a where a.docstatus=1 
		and a.t_warehouse in (select name from `tabWarehouse` where is_flowbin='Yes')""",as_list=1)
	# columns = ["Name:Link/Quotation for Mulitple Quantity","Customer Code::120", "Item Code:Data","Qty1:Data","Rate1:Currency","Qty2:Data","Rate2:Currency","Qty3:Data","Rate3:Currency"]	
	columns = ["Name:Link/Warehouse:120","Batch:Data:100","Quantity:Data:100","Grade:Data:100","QC Status:Data:100"]
	return columns, data 
