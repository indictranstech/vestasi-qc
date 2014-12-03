# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and,cint
import re

class SurfaceAreaAnalysis(Document):

	def validate(self):
		self.validate_serial()
		#self.change_qcstatus()

	def validate_serial(self):
		sample_serial_no_list=[]
		for d in self.get('sa_serial'):
			if d in sample_serial_no_list:
				frappe.msgprint("Sample serial number can not duplicate",raise_exception=1)
				sample_serial_no_list.append(d.serial_no)
			
	def qc_result(self,serial_no):
		parameters=self.get_parameteres()
		result=self.get_result(parameters,serial_no)
		return "Done"
	
	def get_parameteres(self):
		if self.item_code:
			return frappe.db.sql("""select a.specification,a.min_value,a.max_value 
				from `tabItem Quality Inspection Parameter` as a ,
				tabItem as b 
				where a.mandatory='Yes' 
				and a.parent=b.name
				and b.name='%s' 
				and a.specification 
				in ('SSA')"""%(self.item_code),as_list=1)

	def get_result(self,parameters,serial_no):
		icon_mapper={'Rejected':'icon-remove','Accepted':'icon-ok'}
		for d in self.get('sa_serial'):
			frappe.errprint("in the get result")
			if cstr(d.serial_no)==cstr(serial_no):
				d.grade=''
				if cint(d.ssa)>= 6 and cint(d.ssa)<=7.99:
					d.grade='L'
					d.result='Accepted'
				elif cint(d.ssa)>= 8 and cint(d.ssa) <=9.99:
					d.grade='M'
					d.result='Accepted'
				elif cint(d.ssa) >= 10:
					d.grade='H'
					d.result='Accepted'
				else:
					d.grade = 'R'
					d.result='Rejected'
				if d.result=='Accepted':
					d.result_status='<icon class="icon-ok"></icon>'


	def on_submit(self):
		self.validate_qc_status()
		self.change_qcstatus()

	def on_cancel(self):
		self.change_qcstatus_on_cancel()

	
	def validate_qc_status(self):
		for data in self.get('sa_serial'):
			if data.result=='':
				frappe.throw("QC Status Should be Either Accepted Or Rejected")
    
	
	def change_qcstatus(self):
		serials_qc_dic={}
		parameters=["ssa"]
		for data in self.get('sa_serial'):
			self.set_values_in_serial_qc(data,parameters)
			grade=self.get_grade_serial(data.serial_no,data)
			self.change_status(data.serial_no,data,grade)
			to_do=frappe.db.sql("""update `tabToDo` set 
				status='Closed' where serial_no='%s'"""%(data.serial_no))

	def get_grade_serial(self,serial,data):
		sn=frappe.get_doc("Serial No",serial)
		qc_grade=sn.qc_grade
		psd_grade=sn.psd_grade
		if not qc_grade and not psd_grade and data.grade:
			sn.grade=data.grade
		elif qc_grade=='R' or psd_grade=='R' and data.grade and data.grade=='R':
			sn.grade='R'
		elif qc_grade!='R' or psd_grade!='R' and data.grade and data.grade!='R':
			sn.grade=qc_grade or psd_grade + data.grade
		return sn.grade

			
	def change_status(self,serial,data,grade):
		serial_numbers=frappe.db.sql("""update `tabSerial No` 
			set sa_analysis='%s',grade='%s',sa_grade='%s' 
			where name='%s'"""%(data.result,grade,data.grade,serial))

	
	def set_values_in_serial_qc(self,data,parameters):
		sn=frappe.get_doc("Serial No",data.serial_no)
		temp=0
		cl=sn.get('quality_parameters')
		if cl:
			for d in cl:
				if temp==0:
					d.ssa=data.ssa
					sn.save(ignore_permissions=True)
					temp +=1
		else:
			sn.append('quality_parameters',{"ssa":data.ssa})
			sn.save(ignore_permissions=True)



	def change_qcstatus_on_cancel(self):
		for data in self.get('sa_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` 
				where status='Available' 
				and name between '%s' 
				and '%s' """%(data.serial_from,data.serial_to),as_list=1)
			for serial in serials:
				serial_numbers=frappe.db.sql("""update `tabSerial No` 
					set sa_analysis='',sa_grade='' 
					where name='%s'"""%(serial[0]))
				to_do=frappe.db.sql("""update `tabToDo` 
					set status='Open' 
					where serial_no='%s'"""%(serial[0]))
				frappe.db.sql("""delete from 
					`tabQuality Paramter Values` 
					where parent='%s'"""%(serial[0]))
				

