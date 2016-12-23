frappe.pages['import-tool'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Import Tool',
		single_column: true
	});
}