# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and,cint
import re
from erpnext.stock.custom_methods import update_serialNo_grade

class PSDAnalysis(Document):
	
	def validate(self):
		self.validate_serial()
		#self.change_qcstatus()

	def validate_serial(self):
		sample_serial_no_list=[]
		for d in self.get('psd_serial'):
			if d in sample_serial_no_list:
				frappe.msgprint("Sample serial number can not duplicate",raise_exception=1)
				sample_serial_no_list.append(d.sample_serial_no)
			if cint(re.findall('\\d+', d.serial_from)[0]) > cint(re.findall('\\d+', d.serial_to)[0]):
				frappe.msgprint("From Serial No must be less than To Serial No",raise_exception=1)

	def qc_result(self,args):
		# parameters=self.get_parameteres()
		# result=self.get_result(parameters,serial_no)
		# return "Done"
		grade = self.get_psd_grade(args)
		args['grade'] = grade
		return {'grade': grade, 'result': 'Rejected' if grade == 'R' else 'Accepted' }

	def get_psd_grade(self, args):
		grade = 'R'
		mapper = {'D10' : args.get('d10'), 'D30': args.get('d30'), 'D50' : args.get('d50'), 'D90': args.get('d90'),'D100': args.get('d100'), '635 MESH': args.get('mesh_625')}
		parents = frappe.db.sql(""" select parent from `tabPSD Analysis Specifications` a
			where a.specification = 'D50' and a.min_value <= %s and %s <= a.max_value """%(args.get('d50'), args.get('d50')), as_list=1)
		if parents:
			for parent in parents:
				grade = parent[0]
				specifications = frappe.db.sql(""" select specification, min_value, max_value from `tabPSD Analysis Specifications`
					where parent = '%s' and specification != 'D50' and mandatory ='Yes' """%(parent[0]), as_dict = 1)
				for data in specifications:
					if flt(data.min_value) > flt(mapper[data.specification]) and flt(mapper[data.specification]) > flt(data.max_value):
						grade = 'R'
						break
					elif flt(data.min_value) <= flt(mapper[data.specification]) and flt(mapper[data.specification]) <= flt(data.max_value):
						grade = parent[0]
				if grade!='R':
					break
		return grade
	
	def get_parameteres(self):
		if self.item_code:
			return frappe.db.sql("""select a.specification,a.min_value,a.max_value 
				from `tabItem Quality Inspection Parameter` as a ,
				tabItem as b 
				where a.mandatory='Yes' 
				and a.parent=b.name
				and b.name='%s' 
				and a.specification 
				in ("d10","d50","d90","Mesh 625")"""%(self.item_code),as_list=1)

	def get_result(self,parameters,serial_no):
		icon_mapper={'Rejected':'icon-remove','Accepted':'icon-ok'}
		for d in self.get('psd_serial'):
			for data in parameters:
				if d.sample_serial_no==serial_no:
					fieldname=frappe.db.sql("""select fieldname 
						from tabDocField where label='%s'"""%(data[0]),as_list=1)
					if fieldname:
						if (data[1] and data[2]) and (flt(d.get(fieldname[0][0])) >= flt(data[1]) and flt(d.get(fieldname[0][0])) <= flt(data[2])):
							d.result='Accepted'
						elif not data[2] and (flt(d.get(fieldname[0][0])) >= flt(data[1])):                                                
							d.result='Accepted'                  
						elif not data[1] and (flt(d.get(fieldname[0][0])) <= flt(data[2])):
							d.result='Accepted'                         
						else:
							d.result='Rejected'
							d.result_status='<icon class="icon-remove"></icon>'
							d.grade = self.get_rejected_grade(d)
							break
						if(d.result=='Accepted'):
							d.grade = frappe.db.get_value('Item',self.item_code,'grade')
							d.result_status='<icon class="icon-ok"></icon>'
        	return d.result

	def get_rejected_grade(self, args):
		if args.sample_serial_no:
			return 'R' 

	
	def on_submit(self):
		self.validate_qc_status()
		self.change_qcstatus()

	def on_cancel(self):
		self.change_qcstatus_on_cancel()

	
	def validate_qc_status(self):
		for data in self.get('psd_serial'):
			if data.result=='':
				frappe.throw("QC Status Should be Either Accepted Or Rejected")
    
	
	def change_qcstatus(self):
		serials_qc_dic={}
		parameters=["d10","d50","d90","mesh_625"]
		for data in self.get('psd_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` 
				where status='Available' and item_code = '%s'
				and name between '%s' 
				and '%s' """%(self.item_code, data.serial_from,data.serial_to),as_list=1)
			for serial in serials:
				self.set_values_in_serial_qc(serial[0],data)
				# grade=self.get_grade(serial[0],data)
				self.change_status(serial,data)
				update_serialNo_grade(serial[0])
				to_do=frappe.db.sql("""update `tabToDo` set status='Closed' where serial_no='%s'"""%(serial[0]))
				
	# def get_grade(self,serial,data):
	# 	sn=frappe.get_doc("Serial No",serial)
	# 	qc_grade=sn.qc_grade
	# 	sa_grade=sn.sa_grade
	# 	if not qc_grade and not sa_grade:
	# 		sn.grade=data.grade
	# 	elif qc_grade=='R' and sa_grade=='R':
	# 		sn.grade='R'
	# 	elif qc_grade=='R' and sa_grade!='R':
	# 		sn.grade='R '+cstr(sa_grade)
	# 	elif data.grade=='R' and sa_grade=='R':
	# 		sn.grade='R'
	# 	elif data.grade!='R' and qc_grade!='R' and sa_grade=='R':
	# 		sn.grade=cstr(data.grade)+' R'
	# 	elif data.grade!='R' and qc_grade!='R' and sa_grade!='R':
	# 		sn.grade=cstr(data.grade)+cstr(sa_grade)
	# 	elif data.grade=='R' and qc_grade=='R' and sa_grade!='R':
	# 		sn.grade='R '+cstr(sa_grade)
	# 	return sn.grade

	def change_status(self,serial,data):
		serial_numbers=frappe.db.sql("""update `tabSerial No` 
			set psd_status='%s',psd_grade='%s' 
			where name='%s'"""%(data.result,data.grade,serial[0]))

	def set_values_in_serial_qc(self,serial,data):
		sn=frappe.get_doc("Serial No",serial)
		if len(sn.quality_parameters)>0:
			for d in sn.quality_parameters:
				self.update_ex_qty(d, data)
		else:
			qp = sn.append('quality_parameters', {})
			self.add_new(data, qp)
		sn.save(ignore_permissions=True)

	def update_ex_qty(self, d, data):
		d.d10=data.d10
		d.d30 = data.d30
		d.d50=data.d50
		d.d90=data.d90
		d.d100 = data.d100
		d.mesh_625=data.mesh_625
	
	def add_new(self, data, qp):
		qp.d10=data.d10
		qp.d30 = data.d30
		qp.d50=data.d50
		qp.d90=data.d90
		qp.d100 = data.d100
		qp.mesh_625=data.mesh_625

	def change_qcstatus_on_cancel(self):
		for data in self.get('psd_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` 
				where status='Available' and item_code = '%s'
				and name between '%s' 
				and '%s' """%(self.item_code, data.serial_from,data.serial_to),as_list=1)
			for serial in serials:
				serial_numbers=frappe.db.sql("""update `tabSerial No` 
					set psd_status='',psd_grade=''
					where name='%s'"""%( serial[0]))
				to_do=frappe.db.sql("""update `tabToDo` 
					set status='Open' 
					where serial_no='%s'"""%(serial[0]))
				frappe.db.sql("""update
					`tabQuality Paramter Values` set d10 = 0 , d30 = 0, d50=0, d90=0, d100 = 0, mesh_625=0 
					where parent='%s'"""%(serial[0]))
				
