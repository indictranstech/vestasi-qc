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
					"description": _("Quality Control "),
					"label":"Quality Control"

				},
				{
					"type": "doctype",
					"name": "Grade",
					"description": _("Grade"),
				},
				{
					"type": "doctype",
					"name": "Parameter",
					"description": _("Parameter"),
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
					"is_query_report": False,
					"name": "Flowbin Details",
					"doctype": "Quality Checking",
					"icon": "icon-bar-chart",
				},
			]
		},
	]