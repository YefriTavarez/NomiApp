# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmpleadosenObra(Document):
	def get_list(self):
		doclist = frappe.db.sql("""SELECT name 
			FROM `tabEmpleados en Obra`
			WHERE docstatus <> 2 ORDER BY name ASC""", as_dict=True)

		if not doclist:
			return []

		return doclist