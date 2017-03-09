
from __future__ import unicode_literals
import frappe, time, json
from frappe import _
from frappe.utils import get_last_day, get_first_day, nowdate, cstr

from frappe.utils import add_days, cint, flt, getdate, rounded, date_diff, money_in_words
from math import ceil

from frappe.utils.csvutils import UnicodeWriter

@frappe.whitelist()
def process_missing_components(doc, method):
	#month_start = get_first_day(nowdate())
	#month_end = get_last_day(nowdate())

	earnings = doc.get("earnings")

	if not has_component(earnings, "Kilometros") and not has_component(earnings, "Horas"):
		set_missing_earning_component(doc)

	set_missing_deduction_component(doc)

def set_missing_earning_component(salary_slip):
	salary_slip.designation = frappe.get_value("Employee", salary_slip.employee, "designation")
	
	if not salary_slip.designation:
		frappe.throw(_("Employee {0} has not any designation set!").format(salary_slip.employee))

	if salary_slip.designation == "Chofer" or salary_slip.designation == "Operador":
		salary_slip.earnings = []
	
	amount = 0

	if salary_slip.designation == "Chofer":

		kilometers_list = get_kilometros_de_chofer(salary_slip.employee, salary_slip.start_date, salary_slip.end_date)

		if kilometers_list:
			for row in kilometers_list:
				amount += ((float(row.kilometers)-5)*float(row.adict_kilometer_rate))+float(row.kilometer_rate)
				if row.is_amount:
					amount += float(row.amount)

			add_component_to_earnings(salary_slip, "Kilometros", amount)
			

	if salary_slip.designation == "Operador":
		hours_list = get_horas_de_operador(salary_slip.employee, salary_slip.start_date, salary_slip.end_date)

		if hours_list:
			for row in hours_list:
				amount += float(row.hours) * float(row.rate)
				if row.is_amount:
					amount += float(row.amount)

			add_component_to_earnings(salary_slip, "Horas", amount)
			if amount < 12000:
				add_component_to_earnings(salary_slip, "Sueldo Base", 12000 - amount)
				
		else:
			add_component_to_earnings(salary_slip, "Sueldo Base", 12000)

	#salary_slip.calculate_net_pay()
	salary_slip.validate()

def set_missing_deduction_component(salary_slip):
	component = get_component(salary_slip.get("deductions"), "ISR")

	if not component:
		component = frappe.get_doc({
			"doctype" : "Salary Detail",
			"salary_component": "ISR",
			"default_amount": 0,
			"amount_based_on_formula": 0,
			"denpends_on_lwp": 0
		})

	component.amount = calculate_isr_amount(salary_slip)
	
	if component.amount and not has_component(salary_slip.get("deductions"),"ISR"):
		salary_slip.append("deductions", component)
		salary_slip.validate()


def get_choferes_result(obra, emp_ob=None):
	if emp_ob:
		return frappe.db.sql("""SELECT 
			chofer.employee,
			chofer.employee_name,
			chofer.kilometer_rate,
			chofer.adict_kilometer_rate,
			chofer.odometer_start,
			chofer.odometer_end,
			chofer.kilometers,
			chofer.is_amount,
			chofer.amount 
		FROM `tabTabla de Choferes` AS chofer 
		JOIN `tabEmpleados en Obra` project on chofer.parent = project.name 
		WHERE project.name = %(project)s""",{"project": emp_ob }, as_dict=True)

	return frappe.db.sql("""SELECT chofer.employee, chofer.employee_name
	FROM `tabEmpleado en Proyecto` AS chofer 
	JOIN tabProject project on chofer.parent = project.name 
	WHERE chofer.parentfield = 'choferes' 
	AND project.name = %(project)s""",{"project": obra }, as_dict=True)

def get_operadores_result(obra, emp_ob=None):
	if emp_ob:
		return frappe.db.sql("""SELECT 
			operador.employee,
			operador.employee_name,
			operador.rate,
			operador.horometer_start,
			operador.horometer_end,
			operador.hours,
			operador.inactive_hours,
			operador.is_amount,
			operador.amount
		FROM `tabTabla de Operadores` AS operador 
		JOIN `tabEmpleados en Obra` project ON operador.parent = project.name 
		WHERE project.name = %(project)s""",{"project": emp_ob }, as_dict=True)

	return frappe.db.sql("""SELECT operador.employee, operador.employee_name
	FROM `tabEmpleado en Proyecto` AS operador 
	JOIN tabProject project ON operador.parent = project.name 
	WHERE operador.parentfield = 'operadores' 
	AND project.name = %(project)s""",{"project": obra }, as_dict=True)

@frappe.whitelist()
def getChoferes(obra):
	return frappe.db.sql("SELECT * FROM `tabEmpleado en Proyecto` \
		WHERE parent = '{0}' \
		AND parentfield = 'choferes'"
	.format(obra), as_dict=True)

@frappe.whitelist()
def getOperadores(obra):
	return frappe.db.sql("SELECT * FROM `tabEmpleado en Proyecto` \
		WHERE parent = '{0}' \
		AND parentfield = 'operadores'"
	.format(obra), as_dict=True)

def get_kilometros_de_chofer(chofer, from_date, to_date):
	return frappe.db.sql("SELECT kilometers, adict_kilometer_rate, kilometer_rate, amount, is_amount \
		FROM `tabTabla de Choferes` AS c \
		JOIN `tabEmpleados en Obra` AS o \
		ON c.parent = o.name \
		WHERE c.employee = '{0}' \
		AND o.fecha >= '{1}' \
		AND o.fecha <= '{2}' \
		AND c.docstatus <> 2"
	.format(chofer, from_date, to_date), as_dict=True)

def get_horas_de_operador(operador, from_date, to_date):
	return frappe.db.sql("SELECT hours, rate, amount, is_amount \
		FROM `tabTabla de Operadores` AS c \
		JOIN `tabEmpleados en Obra` AS o \
		ON c.parent = o.name \
		WHERE c.employee = '{0}' \
		AND o.fecha >= '{1}' \
		AND o.fecha <= '{2}' \
		AND c.docstatus <> 2"
	.format(operador, from_date, to_date), as_dict=True)

def add_component_to_earnings(salary_slip, salary_component, amount):
	salary_slip.append("earnings",{
		"default_amount": 0,
		"amount_based_on_formula": 0,
		"denpends_on_lwp": 0,
		"salary_component": salary_component,
		"amount": amount
	})

def has_component(array, component):
	found = False

	for current in array:
		if component == current.salary_component:
			found = True

	return found

def get_component(array, component):
	component_found = None
	
	for current in array:
		if component == current.salary_component:
			component_found = current
	
	return component_found

def del_component(array, component):
	deleted = False
	
	for current in array:
		if component == current.salary_component:
			current.delete()
			deleted = True
	
	return deleted

def calculate_isr_amount(salary_slip):
	if not salary_slip.gross_pay:
		salary_slip.gross_pay = 0

	def after_afp(net_pay):
		if has_component(salary_slip.get("deductions"), "AFP"):
			component = get_component(salary_slip.get("deductions"), "AFP")
			return float(net_pay - component.amount)

		return 0

	def after_sfs(net_pay):
		if has_component(salary_slip.get("deductions"), "SFS"):
			component = get_component(salary_slip.get("deductions"), "SFS")
			return float(net_pay - component.amount)
	
		return 0

	def get_acumulated():
		if salary_slip.anual_gross_pay > float(anual_isr_from_25):
			return (((float(anual_isr_to_15) - float(anual_isr_from_15)) * 0.15)) + (((float(anual_isr_to_20) - float(anual_isr_from_20)) * 0.20))

		elif salary_slip.anual_gross_pay > float(anual_isr_from_20):
			return ((float(anual_isr_to_15) - float(anual_isr_from_15)) * 0.15)

	frappe.errprint("gross_pay: {0}".format(salary_slip.gross_pay))
	frappe.errprint("anual gross_pay: {0}".format(salary_slip.gross_pay * 12))
	net_pay = salary_slip.gross_pay
	#net_pay = after_afp(salary_slip.gross_pay) # to deduct only after the afp
	#net_pay = after_sfs(net_pay) # to deduct only after the sfs

	salary_slip.anual_gross_pay = float(net_pay * 12)

	anual_isr_from_25 = frappe.get_value(doctype="Configuracion ISR", fieldname="from25")
	#anual_isr_to_25 = frappe.get_value(doctype="Configuracion ISR", fieldname="to25")
	anual_isr_from_20 = frappe.get_value(doctype="Configuracion ISR", fieldname="from20")
	anual_isr_to_20 = frappe.get_value(doctype="Configuracion ISR", fieldname="to20")
	anual_isr_from_15 = frappe.get_value(doctype="Configuracion ISR", fieldname="from15")
	anual_isr_to_15 = frappe.get_value(doctype="Configuracion ISR", fieldname="to15")

	if salary_slip.anual_gross_pay > float(anual_isr_from_25):
		return ((float(salary_slip.anual_gross_pay) - float(anual_isr_from_25)) * 0.25 + ceil(get_acumulated())) /12

	elif salary_slip.anual_gross_pay > float(anual_isr_from_20):
		return ((float(salary_slip.anual_gross_pay) - float(anual_isr_from_20))  * 0.2  + ceil(get_acumulated()))/12

	elif salary_slip.anual_gross_pay > float(anual_isr_from_15):
		return ((float(salary_slip.anual_gross_pay) - float(anual_isr_from_15)) * 0.15)/12

	else:
		return 0
		
@frappe.whitelist()
def descargar_choferes(obra, with_data=False, emp_ob=None):
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

	if with_data:
		if not emp_ob:
			frappe.throw("Se necesita un Documento tipo <i>Empleados en Obra</i> para continuar!")

		for chofer in get_choferes_result(obra, emp_ob):
			w.writerow([ 
				chofer.employee,
				chofer.employee_name,
				chofer.kilometer_rate,
				chofer.adict_kilometer_rate,
				chofer.odometer_start,
				chofer.odometer_end,
				chofer.kilometers,
				chofer.is_amount,
				chofer.amount 
			])
	else:
		for chofer in get_choferes_result(obra):
			w.writerow([ chofer.employee, chofer.employee_name, 105, 15, "", "", "", 0, 0	])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "template_choferes_" + str(int(time.time()))

@frappe.whitelist()
def descargar_operadores(obra, with_data=False, emp_ob=None):

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

	if with_data:
		if not emp_ob:
			frappe.throw("Se necesita un Documento tipo <i>Empleados en Obra</i> para continuar!")

		for operador in get_operadores_result(obra, emp_ob):
			w.writerow([ 
				operador.employee,
				operador.employee_name,
				operador.rate,
				operador.horometer_start,
				operador.horometer_end,
				operador.hours,
				operador.inactive_hours,
				operador.is_amount,
				operador.amount
			])
	else:
		for operador in get_operadores_result(obra):
			w.writerow([ operador.employee, operador.employee_name, 110, "", "", "", 0, 0, 0 ])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "template_operadores_" + str(int(time.time()))

@frappe.whitelist()
def delete_doc_list(doctype=None):
	if not doctype: 
		return "fail"

	for current in frappe.get_list(doctype):
		doc = frappe.get_doc(doctype, current.name)

		if doc.docstatus == 1:
			frappe.errprint("Cancelling doc: {0}".format(doc.name))
			doc.cancel()

		frappe.errprint("Deleting doc: {0}".format(doc.name))
		doc.delete()

	frappe.errprint("Committing to the Database")
	frappe.db.commit()

