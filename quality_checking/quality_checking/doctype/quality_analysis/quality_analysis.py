# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr
import os, json

class QualityAnalysis(Document):

	def validate(self):
		self.set_mandatory_fields()

	def set_mandatory_fields(self):
		frappe.errprint("hii")
		fields=self.get_mandatory_fields()
		field_names=self.get_field_names(fields)
		temp_len=0
		fields_to_print=''
		for field in field_names:
			if temp_len == len(field_names)-1:
				fields_to_print += field
			else:
				fields_to_print += field +','
			temp_len += 1
		
		self.mandatory_fields=fields_to_print
	
	def get_field_names(self,fields):
		field_names=[]
		for field in fields:
			field_name=frappe.db.sql("select fieldname from `tabDocField` where parent='QA Serial' and label='%s'"%(field[0]),as_list=1)
			if field_name:
				field_names.append(field_name[0][0])
		return field_names

	
	def get_mandatory_fields(self):
		return frappe.db.sql("select specification from `tabItem Quality Inspection Parameter` where mandatory='Yes' and parent='%s'"%(self.item_code),as_list=1)

	
	def get_details(self):
		serials=self.get_serials_details()
		qc_serial_d=self.get('qa_serial')
		if len(qc_serial_d) < 1:
			self.set('qa_serial', [])
		for serial in serials:
			self.validate_serial(serial[0])
			self.append_to_child(serial[0])
		if self.series:
			self.series += cstr(self.serial_from)+'-'+cstr(self.serial_to)+','
		else:
			self.series = cstr(self.serial_from)+'-'+cstr(self.serial_to)+','
		return "done"

	def get_serials_details(self):
		serials=frappe.db.sql("""select name from `tabSerial No` 
			where name between '%s' and 
			'%s' """%(self.serial_from,self.serial_to),as_list=1)
		return serials

	def append_to_child(self,serial):
		qc_details=frappe.get_doc('Serial No',serial).quality_parameters
		if qc_details:
			self.append_values_to_child(serial,qc_details[0])

	def append_values_to_child(self,serial,value):
		qa=self.append('qa_serial',{})
		qa.serial_no=serial
		qa.fe=value.fe
		qa.ca=value.ca
		qa.al=value.al
		qa.c=value.c
		qa.alpha=value.alpha
		qa.d10=value.d10
		qa.d50=value.d50
		qa.d90=value.d90
		#qa.mesh_365=value.mesh_365
		qa.qty=frappe.db.get_value('Serial No',{"name":serial},'qty')
		if self.total_qty:
			self.total_qty += qa.qty or 0
		else:
			self.total_qty=qa.qty or 0
		if self.total_drums:
			self.total_drums += 1
		else:
			self.total_drums=1

	
	def validate_serial(self,serial):
		for d in self.get('qa_serial'):
			if d.serial_no == serial:
				frappe.throw("Serial Already in list")

def get_source_from(doctype,txt,searchfield,start,page_len,filters):
	return frappe.db.sql("select name,qty,status from `tabSerial No` where item_code='%s' and qc_status!=''"%(filters.get('item_code'))) 
			







	


