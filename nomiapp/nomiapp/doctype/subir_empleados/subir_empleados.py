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

		if self.update_record:
			if not self.record:
				frappe.throw("Debe de seleccionar un Registro valido!")

			empbo_doc = frappe.get_doc("Empleados en Obra", self.record)

			if self.load_drivers:
				self.clear_table(empbo_doc, "Drivers")

			if self.load_operators:
				self.clear_table(empbo_doc, "Operators")


		if self.load_drivers:
			self.read_file_and_add(self.load_drivers,"choferes",empbo_doc)

		if self.load_operators:
			self.read_file_and_add(self.load_operators,"operadores",empbo_doc)

		if self.load_drivers or self.load_operators:

			if self.update_record:
				empbo_doc.save()
				
			if not self.update_record:
				empbo_doc.insert()
			return "success"
		
	def read_file_and_add(self, path, key, doc):
		if not path.endswith(".csv"):
			frappe.throw("Extension no soportada. El sistema espera solo archivos CSV!")

		if "/private/" in path:
			full_path = "{0}{1}".format(frappe.conf.full_path2site, path)
		else:
			full_path = "{0}{1}{2}".format(frappe.conf.full_path2site, "/public", path)


		with open(full_path,'rb') as csvfile:
		    counter = 0
		    spamreader = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))

		    for row in spamreader:
		        if(counter == 1):
		            headers = row

		        if(counter > 1):
		            dictionary = dict(zip(headers,row))
		            doc.append(key,dictionary)

		        counter = counter + 1

	def clear_table(self, record, table_field):
		if table_field == "Drivers":
			for rec in record.choferes:
				rec.delete()

		if table_field == "Operators":
			for rec in record.operadores:
				rec.delete()