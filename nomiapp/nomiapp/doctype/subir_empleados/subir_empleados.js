// Copyright (c) 2016, Soldeva, SRL and contributors
// For license information, please see license.txt
frappe.ui.form.on('Subir Empleados', {
    refresh: function(frm) {
        frm.doc.date = frappe.datetime.get_today();
        cur_frm.toolbar.print_icon.addClass("hide");
		cur_frm.disable_save();
		setTimeout(function(){
			$("button[data-fieldname=validate_and_send]")
				.attr("class", "btn btn-primary btn-sm");
		},100);
    },

    validate_and_send: function(frm) {
    	var me = this;
    	if(! (frm.doc.load_drivers || frm.doc.load_operators)){
    		return 1;
    	}

        var callback = function(response) {
        	if(response.message == "success")
            	frappe.msgprint("Registros agregados correctamente!")

            setTimeout(frappe.hide_msgprint, 2000);
        }

        $c("runserverobj", args = {"method": "upload_files", "docs": cur_frm.doc }, callback);

        delete_file_doctype(cur_frm.doc.load_drivers);
        delete_file_doctype(cur_frm.doc.load_operators);

        frm.doc.load_drivers = "";
        frm.doc.load_operators = "";
        refresh_many(["load_drivers", "load_operators"]);
        frm.save();
        cur_frm.refresh();

	    function delete_file_doctype(file_url) {
	        var callback = function(response) {
	        	setTimeout(function(){
	            	delete_attachment(response);
	            }, 1000);
	        }

	        frappe.model.get_value("File", { "file_url": file_url }, "name", callback);
	    }

	    function delete_attachment(docname) {
	    	console.log(docname.name);
	        frappe.call({
	            method: 'frappe.client.delete',
	            args: {
	                doctype: "File",
	                name: docname.name
	            },
	            callback: function(res) {
	                frappe.utils.play_sound("submit");
	                frappe.model.clear_doc("File", docname.name);
	                cur_frm.refresh();
	            }
	        });
	    }
    }
});