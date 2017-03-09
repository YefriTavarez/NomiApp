// Copyright (c) 2016, Soldeva, SRL and contributors
// For license information, please see license.txt
frappe.ui.form.on('Subir Empleados', {
	onload: function(frm){
		frm.doc.project = "";
		frm.doc.record = "";
    	frm.set_df_property("project","reqd", frm.doc.update_record? 0 : 1);
	},
	validate: function(frm){
		validated = false;
	},
    refresh: function(frm) {
        frm.doc.date = frappe.datetime.get_today();
        cur_frm.toolbar.print_icon.addClass("hide");
		cur_frm.disable_save();
		setTimeout(function(){
			$("button[data-fieldname=validate_and_send]")
				.attr("class", "btn btn-primary btn-sm");
		},100);
    },
    update_record: function(frm){
    	frm.set_df_property("project","reqd", frm.doc.update_record? 0 : 1);
    	frm.set_df_property("record","reqd", frm.doc.update_record? 1 : 0);
    },
    validate_and_send: function(frm) {
    	var me = this;
    	if((!frm.doc.load_drivers && !frm.doc.load_operators) ||
    		(!frm.doc.update_record && !frm.doc.project) ||
    		(frm.doc.update_record && !frm.doc.record)) return;

        var callback = function(response) {
        	if("inserted" == response.message) frappe.msgprint("Registros agregados correctamente!");
        	if("updated" == response.message)  frappe.msgprint("Registros actualizados correctamente!");

	        delete_attachments();

	        frm.doc.load_drivers = "";
    	    frm.doc.load_operators = "";
        	refresh_many(["load_drivers", "load_operators"]);

            //setTimeout(frappe.hide_msgprint, 2000);
        	frm.save();
        }

        $c("runserverobj", args = {"method": "upload_files", "docs": cur_frm.doc }, callback);

	    function delete_attachments() {
	    	var attachments = cur_frm.attachments.get_attachments();
	    	attachments.forEach(function(attachment){ 
	    		delete_attachment(attachment.name);
	    	});
	    }

	    function delete_attachment(docname) {
	        frappe.call({
	            method: 'frappe.client.delete',
	            args: {
	                doctype: "File",
	                name: docname
	            },
	            callback: function(response) {
	                //frappe.utils.play_sound("submit");
	                frappe.model.clear_doc("File", docname);
	                cur_frm.reload_doc();
	            }
	        });
	    }
    }
});