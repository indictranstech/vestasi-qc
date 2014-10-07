cur_frm.cscript.validate=function(doc,cdt,cdn){
	var d=locals[cdt][cdn]       
        get_server_fields('set_mandatory_fields','','',doc,cdt,cdn,1,function(r){
                refresh_field('mandatory_fields')
        })
}

cur_frm.fields_dict['serial_from'].get_query = function(doc, cdt, cdn) {
	return{
		query: "quality_checking.quality_checking.doctype.quality_analysis.quality_analysis.get_source_from",
		filters: {'item_code': doc.item_code}
	}
}
cur_frm.fields_dict["serial_to"].get_query = function(doc) {
	return{
		query: "quality_checking.quality_checking.doctype.quality_analysis.quality_analysis.get_source_from",
		filters: {'item_code': doc.item_code}
	}
}

cur_frm.cscript.get_details=function(doc,cdt,cdn){
        var d=locals[cdt][cdn]       
        get_server_fields('get_details','','',doc,cdt,cdn,1,function(r){
                refresh_field('qa_serial')
        })
}