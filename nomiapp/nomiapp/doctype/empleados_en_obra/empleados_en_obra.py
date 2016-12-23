# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, formatdate, format_datetime
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter
import time

class EmpleadosenObra(Document):
	pass

@frappe.whitelist()
def descargar_choferes(obra):
	w = UnicodeWriter()
	w.writerow([
		"Empleado",
		"Nombre del Empleado",
		"Precio de Kilometros (5KM)",
		"Precio de Kilometros Adicionales",
		"Odometro Inicial",
		"Odometro Final",
		"Kilometros",
		"Es en Monto",
		"Monto"
	])

	w.writerow([
		"employee",
		"employee_name",
		"kilometer_rate",
		"adict_kilometer_rate",
		"odometer_start",
		"odometer_end",
		"kilometers",
		"is_amount",
		"amount" 
	])

	for chofer in get_choferes_result(obra):
		w.writerow([ chofer.employee, chofer.employee_name, 105, 15, "", "", "", 0, 0	])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "template_choferes_" + str(int(time.time()))

@frappe.whitelist()
def descargar_operadores(obra):

	w = UnicodeWriter()
	w.writerow([
		"Empleado",
		"Nombre del Empleado",
		"Precio por Hora",
		"Horometro Inicial",
		"Horometro Final",
		"Cantidad de Horas",
		"Horas Inactivas",
		"Es en Monto",
		"Monto"
	])

	w.writerow([
		"employee",
		"employee_name",
		"rate",
		"horometer_start",
		"horometer_end",
		"hours",
		"inactive_hours",
		"is_amount",
		"amount"
	])
	
	for operador in get_operadores_result(obra):
		w.writerow([ operador.employee, operador.employee_name, 110, "", "", "", 0, 0, 0 ])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "template_operadores_" + str(int(time.time()))


@frappe.whitelist()
def get_choferes_result(obra):
	return frappe.db.sql("""SELECT 
		chofer.employee,
		chofer.employee_name
	FROM `tabEmpleado en Proyecto` AS chofer 
	JOIN tabProject project on chofer.parent = project.name 
	WHERE chofer.parentfield = 'choferes' 
	AND project.name = %(project)s""",{"project": obra }, as_dict=True)

@frappe.whitelist()
def get_operadores_result(obra):
	return frappe.db.sql("""SELECT 
		operador.employee,
		operador.employee_name
	FROM `tabEmpleado en Proyecto` AS operador 
	JOIN tabProject project on operador.parent = project.name 
	WHERE operador.parentfield = 'operadores' 
	AND project.name = %(project)s""",{"project": obra }, as_dict=True)


@frappe.whitelist()
def getChoferes(obra):
	return frappe.db.sql("SELECT * FROM `tabEmpleado en Proyecto` \
		WHERE parent = '{0}' \
		AND parentfield = 'choferes'"
	.format(obra), as_dict=1)

@frappe.whitelist()
def getOperadores(obra):
	return frappe.db.sql("SELECT * FROM `tabEmpleado en Proyecto` \
		WHERE parent = '{0}' \
		AND parentfield = 'operadores'"
	.format(obra), as_dict=1)

@frappe.whitelist()
def getKilometrosDeChofer(chofer, desde, hasta):
	return frappe.db.sql("SELECT kilometers, adict_kilometer_rate, kilometer_rate, amount \
		FROM `tabTabla de Choferes` AS c \
		JOIN `tabEmpleados en Obra` AS o \
		ON c.parent = o.name \
		WHERE c.employee = '{0}' \
		AND o.fecha >= '{1}' \
		AND o.fecha <= '{2}' \
		AND c.docstatus <> 2"
	.format(chofer, desde, hasta), as_dict=1)

@frappe.whitelist()
def getHoursDeOperador(operador, desde, hasta):
	return frappe.db.sql("SELECT hours, rate, amount \
		FROM `tabTabla de Operadores` AS c \
		JOIN `tabEmpleados en Obra` AS o \
		ON c.parent = o.name \
		WHERE c.employee = '{0}' \
		AND o.fecha >= '{1}' \
		AND o.fecha <= '{2}' \
		AND c.docstatus <> 2"
	.format(operador, desde, hasta), as_dict=1)


@frappe.whitelist()
def setMissingComponent(salary_slip, employee, desde, hasta):
	designation = frappe.db.get_value("Employee", {"name": employee},"designation")
	amount = 0

	if designation == "Chofer":
		kilometersList = getKilometrosDeChofer(employee, desde, hasta)

	if designation == "Operador":
		hoursList = getHoursDeOperador(employee, desde, hasta)

	delete_sueldo_base_component(salary_slip)
	salary_slip_doc = frappe.get_doc("Salary Slip", salary_slip)

	if designation == "Chofer" and kilometersList:
		for row in kilometersList:
			amount += ((float(row.kilometers)-5)*float(row.adict_kilometer_rate))+float(row.kilometer_rate)
			if row.amount:
				amount += float(row.amount)

		add_component_to_earnings(salary_slip_doc, "Kilometros", amount)

	if designation == "Operador" and hoursList:
		for row in hoursList:
			amount += float(row.hours) * float(row.rate)
			if row.amount:
				amount += float(row.amount)

		add_component_to_earnings(salary_slip_doc, "Horas", amount)

	salary_slip_doc.validate()
	salary_slip_doc.save()

@frappe.whitelist()
def add_component_to_earnings(salary_slip_doc, salary_component ,amount):
	salary_slip_doc.append("earnings",{
		"default_amount": 0,
		"amount_based_on_formula": 0,
		"denpends_on_lwp": 0,
		"salary_component": salary_component,
		"amount": amount
	})

def delete_sueldo_base_component(salary_slip):
	frappe.db.sql("""DELETE FROM `tabSalary Detail` 
		WHERE parenttype='Salary Slip' 
		AND salary_component = 'Sueldo Base' 
		AND parent = %(salary_slip)s""", 
		{"salary_slip": salary_slip}, 
		as_dict=1)