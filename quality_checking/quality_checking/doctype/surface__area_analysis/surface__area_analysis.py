# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and,cint
import re
from erpnext.stock.custom_methods import update_serialNo_grade

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
			
	def qc_result(self,args):
		grade = self.get_ssa_grade(args)
		args['grade'] = grade
		return {'grade': grade, 'result': 'Rejected' if grade == 'R' else 'Accepted' }
	
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

	def get_ssa_grade(self, args):
		grade = frappe.db.sql(""" select parent from `tabSSA Analysis Specifications` 
			where specification = 'SSA' and min_value <= '%s' and '%s' <= max_value """%(args.get('ssa'), args.get('ssa')), as_list=1)
		grade = grade[0][0] if grade else 'R'
		return grade

	# def get_result(self,parameters,serial_no):
	# 	icon_mapper={'Rejected':'icon-remove','Accepted':'icon-ok'}
	# 	for d in self.get('sa_serial'):
	# 		if cstr(d.serial_no)==cstr(serial_no):
	# 			d.grade=''
	# 			if cint(d.ssa)>= 6 and cint(d.ssa)<=7.99:
	# 				d.grade='L'
	# 				d.result='Accepted'
	# 			elif cint(d.ssa)>= 8 and cint(d.ssa) <=9.99:
	# 				d.grade='M'
	# 				d.result='Accepted'
	# 			elif cint(d.ssa) >= 10:
	# 				d.grade='H'
	# 				d.result='Accepted'
	# 			else:
	# 				d.grade = 'R'
	# 				d.result='Rejected'
	# 			if d.result=='Accepted':
	# 				d.result_status='<icon class="icon-ok"></icon>'
	# 			else:
	# 				d.result_status='<icon class="icon-remove"></icon>'
						


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
			# grade=self.get_grade_serial(data.serial_no,data)
			self.change_status(data.serial_no,data)
			update_serialNo_grade(data.serial_no)
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
			sn.grade=qc_grade or psd_grade + data.grade #issue
		return sn.grade

			
	def change_status(self,serial,data):
		serial_numbers=frappe.db.sql("""update `tabSerial No` 
			set sa_analysis='%s',sa_grade='%s' 
			where name='%s'"""%(data.result,data.grade,serial))

	
	def set_values_in_serial_qc(self,data,parameters):
		sn=frappe.get_doc("Serial No",data.serial_no)
		if len(sn.quality_parameters)>0:
			for d in sn.quality_parameters:
				self.update_ex_qty(d, data)
		else:
			qp = sn.append('quality_parameters', {})
			self.add_new(data, qp)
		sn.save(ignore_permissions=True)

	def update_ex_qty(self, d, data):
		d.ssa=data.ssa

	def add_new(self, data, qp):
		qp.ssa=data.ssa
		
	def change_qcstatus_on_cancel(self):
		for data in self.get('sa_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` 
				where status='Available' 
				and name = '%s' """%(data.serial_no),as_list=1)
			for serial in serials:
				serial_numbers=frappe.db.sql("""update `tabSerial No` 
					set sa_analysis='',sa_grade='' 
					where name='%s'"""%(serial[0]))
				update_serialNo_grade(serial[0])
				to_do=frappe.db.sql("""update `tabToDo` 
					set status='Open' 
					where serial_no='%s'"""%(serial[0]))
				frappe.db.sql("""update
					`tabQuality Paramter Values` set ssa = 0 
					where parent='%s'"""%(serial[0]))
				

