	# Copyright (c) 2013, New Indictrans Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re
from frappe import _
from frappe.utils import cstr, flt, getdate, comma_and,cint

class QualityChecking(Document):
	def validate(self):
                self.validate_serial()
               
                

	def validate_serial(self):
        	sample_serial_no_list=[]
        	for d in self.get('qc_serial'):
                	if d in sample_serial_no_list:
                        	frappe.msgprint("Sample serial number can not duplicate",raise_exception=1)
                    		sample_serial_no_list.append(d.sample_serial_no)
                    	if cint(re.findall('\\d+', d.serial_from)[0]) > cint(re.findall('\\d+', d.serial_to)[0]):
                        	frappe.msgprint("From Serial No must be less than To Serial No",raise_exception=1)

	def qc_result(self,serial_no):
        	parameters=self.get_parameteres()
      		result=self.get_result(parameters,serial_no)
       		#self.get_grade(parameters,serial_no)
       		return "Done"
	
	def get_parameteres(self):
		if self.item_code:
                	return frappe.db.sql("select a.specification,a.min_value,a.max_value,a.hp,a.p,a.s from `tabItem Quality Inspection Parameter` as a , tabItem as b where a.mandatory='Yes' and a.parent=b.name and b.name='%s'"%(self.item_code),as_list=1)

	def get_result(self,parameters,serial_no):
   		icon_mapper={'Rejected':'icon-remove','Accepted':'icon-ok'}
		
        	for d in self.get('qc_serial'):
            		for data in parameters:
			
                		if d.sample_serial_no==serial_no:
                    			fieldname=frappe.db.sql("select fieldname from tabDocField where label='%s'"%(data[0]),as_list=1)
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
			series = frappe.db.get_value('Serial No',args.sample_serial_no,'naming_series')
			return series + ' - R' 

	
	def on_submit(self):
        	self.validate_qc_status()
        	self.change_qcstatus()


	
	def on_cancel(self):
    		self.change_qcstatus_on_cancel()

	
	def validate_qc_status(self):
        	for data in self.get('qc_serial'):
        		if data.result=='':
                		frappe.throw("QC Status Should be Either Accepted Or Rejected")
    
	
	def change_qcstatus(self):
		serials_qc_dic={}
		parameters=["fe","ca","al","c","alpha","d10","d50","mesh_625","d90","ssa","o2","free_si"]
		for data in self.get('qc_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` where status='Available' and name between '%s' and '%s' """%(data.serial_from,data.serial_to),as_list=1)
			for serial in serials:
				self.change_status(serial,data)
				#self.set_values(serial,data)
				self.set_values_to_dic(serial,data,serials_qc_dic,parameters)
				to_do=frappe.db.sql("""update `tabToDo` set status='Closed' where serial_no='%s'"""%(serial[0]))
		self.set_values_in_serial_qc(serials_qc_dic,parameters)

	def change_status(self,serial,data):
		serial_numbers=frappe.db.sql("""update `tabSerial No` set qc_status='%s',grade='%s' where name='%s'"""%(data.result,data.grade,serial[0]))

	def set_values_to_dic(self,sr_no,data_row,serials_qc_dic,parameters):
		if not sr_no[0] in serials_qc_dic.keys():
			pram_dic={}
			for parameter in parameters:
				if data_row.get(parameter):
					pram_dic.setdefault(parameter,data_row.get(parameter))
				else:
					pram_dic.setdefault(parameter,"")
			serials_qc_dic.setdefault(sr_no[0],pram_dic)
		else:
			pram_dic=serials_qc_dic.get(sr_no[0])
			for parameter in parameters:
				if data_row.get(parameter):
					pram_dic[parameter]=data_row.get(parameter)
			serials_qc_dic[sr_no[0]]=pram_dic
		return serials_qc_dic

	def set_values_in_serial_qc(self,serials_qc_dic,parameters):
			for key in serials_qc_dic:
				pram_dic=serials_qc_dic.get(key)
				sn=frappe.get_doc("Serial No",key)
				qp=sn.append("quality_parameters",{})
				qp.fe=pram_dic.get('fe')
				qp.ca=pram_dic.get('ca')
				qp.al=pram_dic.get('al')
				qp.c=pram_dic.get('c')
				qp.alpha=pram_dic.get('alpha')
				qp.d10=pram_dic.get('d10')
				qp.d50=pram_dic.get('d50')
				qp.d90=pram_dic.get('d90')
				qp.ssa=pram_dic.get('ssa')
				qp.o2=pram_dic.get('o2')
				qp.mesh_625=pram_dic.get('mesh_625')
				qp.free_si=pram_dic.get('free_si')
				sn.save(ignore_permissions=True)


	def set_values(self,serial,data):
		sn=frappe.get_doc("Serial No",serial[0])
		qp=sn.append("quality_parameters",
			{	"fe":data.fe,
				"ca":data.ca,
				"al":data.al,
				"c":data.c,
				"alpha":data.alpha,
				"d10":data.d10,
				"d50":data.d50,
				"mesh_625":data.mesh_625,
				"d90":data.d90,
				"ssa":data.ssa,
				"o2":data.o2,
				"free_si":data.free_si
			})
		sn.save(ignore_permissions=True)



	
	def change_qcstatus_on_cancel(self):
		for data in self.get('qc_serial'):
			serials=frappe.db.sql("""select name from `tabSerial No` where status='Available' and name between '%s' and '%s' """%(data.serial_from,data.serial_to),as_list=1)
			for serial in serials:
				serial_numbers=frappe.db.sql("""update `tabSerial No` set qc_status='',grade='' where name='%s'"""%(serial[0]))
				to_do=frappe.db.sql("""update `tabToDo` set status='Open' where serial_no='%s'"""%(serial[0]))
				frappe.db.sql("""delete from `tabQuality Paramter Values` where parent='%s'"""%(serial[0]))
				
 
