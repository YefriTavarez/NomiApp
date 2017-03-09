// Copyright (c) 2016, Soldeva, SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Empleados en Obra', {
	refresh: function(frm) {
		var me = this;
		if(!cur_frm.doc.__islocal)
			cur_frm.add_custom_button("Choferes", descargar_choferes,"Descargar CSV") &
			cur_frm.add_custom_button("Operadores", descargar_operadores,"Descargar CSV");

		function descargar_choferes(){
			descargar("choferes");
		}

		function descargar_operadores(){
			descargar("operadores");
		}

		function descargar(tabla){
			if(!cur_frm.doc.obra){
				frappe.msgprint("Debe de seleccionar una obra!");
				return 1;
			}

			var dowload_url = 
				"/api/method/nomiapp.api.descargar_" + tabla +
				"?with_data=True&emp_ob=" + cur_frm.doc.name + "&obra=" + cur_frm.doc.obra;
			window.open(dowload_url);
			
		}
	},
	obra: function(frm){
		if(!cur_frm.doc.obra){
			return ;
		}

		cur_frm.clear_table("choferes");

		frappe.call({
			method: "nomiapp.api.getChoferes",
			args: { obra: me.frm.doc.obra },
			callback: function(data) {
				agregarChoferes(data.message);
			}
		});

		function agregarChoferes(choferes){
			choferes.forEach(function(chofer){
				agregarChofer(chofer);
			});
		}

		function agregarChofer(chofer){
			cur_frm.add_child("choferes",{
		        employee : chofer.employee,
		        employee_name : chofer.employee_name,
		        odometer_start: 0.0,
		       	odometer_end: 0.0,
		       	kilometers: 0.0
		    });

			refresh_field("choferes");
		}

		cur_frm.clear_table("operadores");
	    
		frappe.call({
			method: "nomiapp.api.getOperadores",
			args: { obra: me.frm.doc.obra },
			callback: function(data) {
				agregarOperadores(data.message);
			}
		});

		function agregarOperadores(operadores){
			operadores.forEach(function(operador){
				agregarOperador(operador);
			});
		}

		function agregarOperador(operador){
			cur_frm.add_child("operadores",{
		        employee : operador.employee,
		        employee_name : operador.employee_name,
		        horometer_start: 0.0,
		       	horometer_end: 0.0,
		       	hours: 0.0
		    });

			refresh_field("operadores");
		}
	}
});

frappe.ui.form.on("Tabla de Choferes",{
 	odometer_start:	function(frm, child_doctype, child_name) { 
		var odometer_start = frappe.model.get_value(child_doctype, child_name,'odometer_start'); 
		var odometer_end = frappe.model.get_value(child_doctype, child_name,'odometer_end'); 

		var kilometers = flt(odometer_end) - flt(odometer_start);
		frappe.model.set_value(child_doctype, child_name,'kilometers', kilometers);
	},

	odometer_end: function(frm, child_doctype, child_name) { 
		var odometer_start = frappe.model.get_value(child_doctype, child_name,'odometer_start'); 
		var odometer_end = frappe.model.get_value(child_doctype, child_name,'odometer_end'); 

		var kilometers = flt(odometer_end) - flt(odometer_start);
		frappe.model.set_value(child_doctype, child_name,'kilometers', kilometers);
	},

	is_amount: function(frm, child_doctype, child_name) { 
		var is_amount = frappe.model.get_value(child_doctype, child_name,'is_amount');
		if(is_amount){
			frappe.model.set_value(child_doctype, child_name,'odometer_start', 0); 
			frappe.model.set_value(child_doctype, child_name,'odometer_end', 0); 
			frappe.model.set_value(child_doctype, child_name,'kilometers', 0); 
		} else {
			frappe.model.set_value(child_doctype, child_name,'amount', 0); 
		}
	}
});

frappe.ui.form.on("Tabla de Operadores", {
	horometer_start : function(frm, child_doctype, child_name) { 
		var horometer_start = frappe.model.get_value(child_doctype, child_name,'horometer_start'); 
		var horometer_end = frappe.model.get_value(child_doctype, child_name,'horometer_end'); 

		var hours = flt(horometer_end) - flt(horometer_start);

		if(hours < 6){
			var inactive_hours = 6 - hours;
			frappe.model.set_value(child_doctype, child_name,'inactive_hours', inactive_hours);
			//set the minimun amount of hours allowed in case it is less than 6
			hours = 6;
		}

		frappe.model.set_value(child_doctype, child_name,'hours', hours);
	},
	
	horometer_end: 	function(frm, child_doctype, child_name) { 
		var horometer_start = frappe.model.get_value(child_doctype, child_name,'horometer_start'); 
		var horometer_end = frappe.model.get_value(child_doctype, child_name,'horometer_end');

		if(horometer_end < horometer_start){
			frappe.msgprint("Horometro Final no puede ser menor que el Horometro Inicial.	");
		}

		var hours = flt(horometer_end) - flt(horometer_start);

		if(hours < 6){
			var inactive_hours = 6 - hours;
			frappe.model.set_value(child_doctype, child_name,'inactive_hours', inactive_hours);
			//set the minimun amount of hours allowed in case it is less than 6
			hours = 6;
		}

		frappe.model.set_value(child_doctype, child_name,'hours', hours);
	},
	is_amount: function(frm, child_doctype, child_name) { 
		var is_amount = frappe.model.get_value(child_doctype, child_name,'is_amount');
		if(is_amount){
			frappe.model.set_value(child_doctype, child_name,'horometer_start', 0); 
			frappe.model.set_value(child_doctype, child_name,'horometer_end', 0); 
			frappe.model.set_value(child_doctype, child_name,'hours', 0); 
		} else {
			frappe.model.set_value(child_doctype, child_name,'amount', 0); 
		}
	}
});