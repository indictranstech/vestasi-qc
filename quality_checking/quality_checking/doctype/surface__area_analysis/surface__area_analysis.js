cur_frm.fields_dict.sa_serial.grid.get_field("serial_no").get_query = function(doc) {
     	if(doc.item_code)
     	{
     		return {
				query: "erpnext.stock.custom_methods.get_serial_from_sa",
				filters:{
					'item_code': doc.item_code
				}
			}	
     	}

}
cur_frm.cscript.calculate=function(doc,cdt,cdn){
        var d=locals[cdt][cdn]       
        get_server_fields('qc_result',d,'',doc,cdt,cdn,1,function(r){
     		refresh_field('grade', d.name, 'sa_serial')
     		refresh_field('result', d.name, 'sa_serial')
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
		refresh_field('sa_serial')
}
