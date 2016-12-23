// Copyright (c) 2016, Soldeva, SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bajar Empleados', {
	refresh: function(frm) {
		cur_frm.toolbar.print_icon.addClass("hide");
		cur_frm.disable_save();

		setTimeout(function(){
			$("button[data-fieldname=download_drivers]")
				.attr("class", "btn btn-primary btn-sm");

			$("button[data-fieldname=download_operators]")
				.attr("class", "btn btn-primary btn-sm");

		},400);

	}, download_drivers: function(){
		descargar("choferes");
	}, download_operators: function(){
		descargar("operadores");
	}
});

function descargar(tabla){
	if(!cur_frm.doc.project){
		frappe.msgprint("Debe de seleccionar una obra!");
		return 1;
	}

	var dowload_url = 
		"/api/method/nomiapp.nomiapp.doctype.empleados_en_obra.empleados_en_obra.descargar_" + tabla +
		"?obra=" + cur_frm.doc.project;
	window.open(dowload_url);
}
