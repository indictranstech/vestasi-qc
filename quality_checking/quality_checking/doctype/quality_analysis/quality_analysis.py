# Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr
import os, json

class QualityAnalysis(Document):

	def validate(self):
		# self.set_mandatory_fields()
                self.set_grade()

        def set_mandatory_fields(self):
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

        def set_grade(self):
                if self.serial_from:
                        self.grade = frappe.db.get_value('Serial No', self.serial_from, 'grade')

        def get_field_names(self,fields):
                field_names=[]
                for field in fields:
                        field_name=frappe.db.sql("""select fieldname 
                        	from `tabDocField` 
                        	where parent='QA Serial' 
                        	and label='%s'"""%(field[0]),as_list=1)
                        if field_name:
                                field_names.append(field_name[0][0])
                return field_names


        def get_mandatory_fields(self):
                return frappe.db.sql("""select specification from 
                	`tabItem Quality Inspection Parameter` 
                	where mandatory='Yes' and parent='%s'"""%(self.item_code),as_list=1)


        def get_details(self):
                serials=self.get_serials_details()
                qc_serial_d=self.get('qa_serial')
                if len(qc_serial_d) < 1:
                        self.set('qa_serial', [])
                for serial in serials:
                        self.validate_serial(serial[0])
                        self.append_to_child(serial[0])
                if self.series:
                        self.series = cstr(self.series)+','+cstr(self.serial_from)
                else:
                        self.series = cstr(self.serial_from)
                self.set_mandatory_field()
                return "done"

        def get_serials_details(self):
                serials=frappe.db.sql("""select name from `tabSerial No` 
                        where name between '%s' and 
                        '%s' and item_code = '%s' and ifnull(qty,0) > 0 and ifnull(qc_certificate, 'Not Completed')='Not Completed'"""%(self.serial_from,self.serial_to, self.item_code),as_list=1)
                return serials

        def set_mandatory_field(self):
                mandatory_fields = []
                serial_no = (self.series).split(',')
                for serial in serial_no:
                        sn_details = frappe.db.get_value('Serial No', serial, '*', as_dict=1)
                        if sn_details.qc_grade:
                                self.prepare_for_mandatory('Chemical', sn_details.qc_grade, mandatory_fields)
                        if sn_details.psd_grade:
                                self.prepare_for_mandatory('PSD', sn_details.psd_grade, mandatory_fields)
                        if sn_details.sa_grade:
                                self.prepare_for_mandatory('SSA', sn_details.sa_grade, mandatory_fields)
                self.update_parm(mandatory_fields)

        def prepare_for_mandatory(self, type_of_analysis, grade, mandatory_fields):
                type_of_field = ('a.has_chemical_analysis' if type_of_analysis == 'Chemical' else 'a.has_psd_analysis') if type_of_analysis in ['Chemical', 'PSD'] else 'a.has_ssa_analysis'
                type_of_table =  ('Chemical Analysis Specifications' if type_of_analysis == 'Chemical' else 'PSD Analysis Specifications') if type_of_analysis in ['Chemical', 'PSD'] else 'SSA Analysis Specifications'    
                get_parm = frappe.db.sql(""" select b.specification from `tab%s` b, `tabGrade` a
                                where %s = 'Yes' and b.mandatory = 'Yes' 
                                and b.parent = a.name order by b.idx"""%(type_of_table, type_of_field), as_dict=1)
                for parm in get_parm:
                        mandatory_fields.append(parm.specification)

        def update_parm(self, mandatory_fields):
                parm = sorted(set(mandatory_fields), key=mandatory_fields.index)
                self.mandatory_fields = ','.join(parm).lower().replace(' ', '_')

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
                qa.free_si=value.free_si
                qa.mesh_625=value.mesh_625
                qa.o2=value.o2
                qa.ssa=value.ssa
                qa.grade = frappe.db.get_value('Serial No',{"name":serial},'grade') 
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

        def before_submit(self):
                drum_list = ''
                for data in self.qa_serial:
                        if data.serial_no:
                                self.update_serial_status(data.serial_no, 'Completed')
                                drum_list += data.serial_no + '\n'
                self.drum_list = drum_list

        def before_cancel(self):
                self.update_status()

        def update_status(self):
                self.drum_list = ''
                for data in self.qa_serial:
                        self.update_serial_status(data.serial_no, 'Completed')
                                

        def update_serial_status(self, serial_no, status):
                frappe.db.sql(""" update `tabSerial No` set qc_certificate ='%s'
                        where name = '%s'"""%(status, serial_no))


def get_source_from(doctype,txt,searchfield,start,page_len,filters):
        condition = get_condition(filters.get('item_code'))
	return frappe.db.sql("""select name,qty,status from `tabSerial No` where item_code='%s' 
                and ifnull(qty,0) > 0 and %s and ifnull(qc_certificate, 'Not Completed') = 'Not Completed'
                and name like '%%%s%%' limit %s, %s"""%(filters.get('item_code'), condition, txt, start, page_len))

def get_condition(item_code):
        condition = '1=1'
        if item_code:
                item_details = frappe.db.get_value('Item', item_code, '*', as_dict=1)
                if item_details.chemical_analysis == 'Yes': condition += " and qc_status = 'Accepted'"
                if item_details.psd_analysis == 'Yes' : condition += " and psd_status = 'Accepted'"
                if item_details.ssa == 'Yes' : condition += " and sa_analysis = 'Accepted'"
        return condition


