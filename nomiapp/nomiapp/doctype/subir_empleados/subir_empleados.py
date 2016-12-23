# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import csv, os

class SubirEmpleados(Document):
	def upload_files(self):
		empbo_doc = frappe.get_doc({
		    "doctype": "Empleados en Obra",
		    "obra": self.project,
		    "fecha": self.date		            	
		})

		if self.load_drivers:
			self.read_file_and_add(self.load_drivers,"choferes",empbo_doc)
		if self.load_operators:
			self.read_file_and_add(self.load_operators,"operadores",empbo_doc)

		if self.load_drivers or self.load_operators:
			empbo_doc.insert()
			return "success"
		
	def read_file_and_add(self, path, key, doc):
		if not path.endswith(".csv"):
			frappe.throw("Extension no soportada. El sistema espera solo archivos CSV!")

		with open(frappe.conf.site_name + path,'rb') as csvfile:
		    counter = 0
		    spamreader = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))

		    for row in spamreader:
		        if(counter == 1):
		            headers = row

		        if(counter > 1):
		            dictionary = dict(zip(headers,row))
		            doc.append(key,dictionary)

		        counter = counter + 1

		        