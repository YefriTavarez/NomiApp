// Copyright (c) 2016, Soldeva, SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Empleados en Obra', {
	add_navigation_buttons: function(frm){
		var callback = function(response){
			if(frm.doc.__islocal || !response.message) return ;

			var list = response.message;
			var index = 0, prev_index = 0, next_index = 0;
			var cur_route, prev_route, next_route;

			for( ; index < list.length; index ++){
				prev_index = index - 1 < 0 ? 0 : index - 1;
				next_index = index + 1 >= list.length ? list.length - 1 : index + 1;

				if(frm.doc.name == list[index].name){
					//console.log("found");
					prev_route = list[prev_index].name;
					next_route = list[next_index].name;
					cur_route = list[index].name;

					break;
				}
			}

			var route_next = function(res){ set_emp_route(next_route); };
			var route_prev = function(res){  set_emp_route(prev_route); };
			var set_emp_route = function(docname){ frappe.set_route("Form/Empleados en Obra",docname); };

			if(next_route != prev_route) frm.add_custom_button("<< Prev", route_prev);

			if(next_route != cur_route)	frm.add_custom_button("Next >>", route_next);
		};
		
		$c("runserverobj", args={"method": "get_list", "docs": cur_frm.doc}, callback=callback);
	},
	refresh: function(frm) {
		var me = this;
		if(!frm.doc.__islocal)
			frm.add_custom_button("Choferes", descargar_choferes,"Descargar CSV") &
			frm.add_custom_button("Operadores", descargar_operadores,"Descargar CSV");

		cur_frm.trigger("add_navigation_buttons");

		function descargar_choferes(){
			descargar("choferes");
		}

		function descargar_operadores(){
			descargar("operadores");
		}

		function descargar(tabla){
			if(!frm.doc.obra){
				frappe.msgprint("Debe de seleccionar una obra!");
				return 1;
			}

			var dowload_url = 
				"/api/method/nomiapp.api.descargar_" + tabla +
				"?with_data=True&emp_ob=" + frm.doc.name + "&obra=" + frm.doc.obra;
			window.open(dowload_url);
			
		}
	},
	obra: function(frm){
		if(!frm.doc.obra) return ;

		frm.clear_table("choferes");

		frappe.call({
			method: "nomiapp.api.getChoferes",
			args: { obra: me.frm.doc.obra },
			callback: function(data) {
				agregarChoferes(data.message);
			}
		});

		function agregarChoferes(choferes){
			if(!choferes){ 
				frm.clear_table("choferes");
				refresh_field("choferes");
				return ; 
			}

			choferes.forEach(function(chofer){
				agregarChofer(chofer);
			});
		}

		function agregarChofer(chofer){
			frm.add_child("choferes",{
		        employee : chofer.employee,
		        employee_name : chofer.employee_name,
		        odometer_start: 0.0,
		       	odometer_end: 0.0,
		       	kilometers: 0.0
		    });

			refresh_field("choferes");
		}

		frm.clear_table("operadores");
	    
		frappe.call({
			method: "nomiapp.api.getOperadores",
			args: { obra: me.frm.doc.obra },
			callback: function(data) {
				agregarOperadores(data.message);
			}
		});

		function agregarOperadores(operadores){
			if(!operadores){ 
				frm.clear_table("operadores");
				refresh_field("operadores");
				return ; 
			}

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