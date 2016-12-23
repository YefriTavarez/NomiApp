# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ConfiguracionISR(Document):
	pass

@frappe.whitelist()
def getRangosISR():
	return frappe.db.sql("SELECT field, value \
		FROM `tabSingles` \
		WHERE doctype='Configuracion ISR' \
		AND (field like 'from%' OR field like 'to%') \
		ORDER BY field", as_dict=1)


	comment = """return frappe.db.sql("SELECT value \
		FROM `tabSingles` \
		WHERE doctype='Configuracion ISR'\
		AND field='{0}'"
	.format(field),as_dict=1)"""