# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "nomiapp"
app_title = "NomiApp"
app_publisher = "Soldeva, SRL"
app_description = "Una aplicacion para la ayuda de la Recursos Humanos."
app_icon = "octicon octicon-flame"
app_color = "#332"
app_email = "soporte@soldeva.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nomiapp/css/nomiapp.css"
# app_include_js = "/assets/nomiapp/js/nomiapp.js"

# include js, css files in header of web template
# web_include_css = "/assets/nomiapp/css/nomiapp.css"
# web_include_js = "/assets/nomiapp/js/nomiapp.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "nomiapp.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "nomiapp.install.before_install"
# after_install = "nomiapp.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nomiapp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"nomiapp.tasks.all"
# 	],
# 	"daily": [
# 		"nomiapp.tasks.daily"
# 	],
# 	"hourly": [
# 		"nomiapp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"nomiapp.tasks.weekly"
# 	]
# 	"monthly": [
# 		"nomiapp.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "nomiapp.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nomiapp.event.get_events"
# }

