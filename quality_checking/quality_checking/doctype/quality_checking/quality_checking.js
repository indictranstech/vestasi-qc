cur_frm.fields_dict.qc_serial.grid.get_field("serial_from").get_query = function(doc) {
     	if(doc.item_code)
     	{
     		return {
				query: "erpnext.stock.custom_methods.get_serial_from",
				filters:{
					'item_code': doc.item_code
				}
			}	
     	}

}

cur_frm.fields_dict.qc_serial.grid.get_field("serial_to").get_query = function(doc) {
     return {
		query: "erpnext.stock.custom_methods.get_serial_from",
		filters:{
			'item_code': doc.item_code
		}

	}
}

cur_frm.fields_dict.qc_serial.grid.get_field("sample_serial_no").get_query = function(doc,cdt,cdn) {
        var d = locals[cdt][cdn]
        if (d.serial_from && d.serial_to){
        	return "select name from `tabSerial No` where name between '"+d.serial_from+"' and '"+d.serial_to+"'"
        }	
        else{
        	return "select name from `tabSerial No` where ifnull(qc_status,'')='' and item_code='"+doc.item_code+"'"
        }
}

cur_frm.cscript.calculate=function(doc,cdt,cdn){
        var d=locals[cdt][cdn]       
        get_server_fields('qc_result',d,'',doc,cdt,cdn,1,function(r){
    		refresh_field('grade', d.name, 'qc_serial')
    		refresh_field('result', d.name, 'qc_serial')
        })
}

cur_frm.cscript.result=function(doc,cdt,cdn){
		var d=locals[cdt][cdn]
		if(d.result=='Accepted')
		{
			d.result_status='<icon class="icon-ok"></icon>'
		}else if(d.result=='Rejected'){
			d.result_status='<icon class="icon-remove"></icon>'
		}
		refresh_field('qc_serial')
}


