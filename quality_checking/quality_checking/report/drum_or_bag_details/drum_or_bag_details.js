// Copyright (c) 2013, Indictrans technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Drum or Bag Details"] = {
	"filters": [
	    {
			"fieldname":"drum_from",
			"label": __("Drum From"),
			"fieldtype": "Link",
			"options": "Serial No"
		},
		{
			"fieldname":"drum_to",
			"label": __("Drum To"),
			"fieldtype": "Link",
			"options": "Serial No"
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"grade",
			"label": __("Grade"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"warehouse",
			"label": __("Location"),
			"fieldtype": "Link",
			"options" : "Warehouse"
		},
	]
}
ouse