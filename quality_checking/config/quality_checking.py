from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Quality Checking",
					"description": _("Chemical Analysis"),
					"label":"Chemical Analysis"

				},
				{
					"type": "doctype",
					"name": "PSD Analysis",
					"description": _("Particle Size Analysis"),
					"label":"PSD Analysis"

				},
				{
					"type": "doctype",
					"name": "Surface  Area Analysis",
					"description": _("Surface Area Analysis"),
					"label":"SSA Analysis"

				},
				{
					"type": "doctype",
					"name": "Grade",
					"description": _("Grade"),
				},
				{
					"type": "doctype",
					"name": "Parameter",
					"description": _("Parameter")
				},
				{
					"type": "doctype",
					"name": "Quality Analysis",
					"description": _("Quality Analysis Certificate"),
					"label":"Quality Certificate"
				},
			]
		},
		{
			"label": _("Main Reports"),
			"icon": "icon-table",
			"items": [
				{
					"type":"report",
					"is_query_report":True,
					"name": "Drum or Bag Details",
					"doctype": "Serial No",
					"description": _("Drum's or Bag's all information"),
					"icon": "icon-bar-chart"
				},
				{
					"type":"report",
					"is_query_report":True,
					"name": "Flowbin Details",
					"doctype": "Stock Entry",
					"icon": "icon-bar-chart"
				},
			]
		},
	]
