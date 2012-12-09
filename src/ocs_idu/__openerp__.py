# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# Generated by the OpenERP plugin for Dia !
{
        "name" : "OCS-IDU (Instituto de Desarrollo Urbano) Customization for Constructions",
        "version" : "openerp6.1-rev2012112100",
        "author" : "Angel María Fonseca, Andres Ignacio Baez Alba and Cinxgler Mariaca Minda",
        "website" : "www.idu.gov.co",
        "category" : "Social Management",
        "description": """For Public Organizations, useful to receive claims from Citizens""",
        "depends" : ['ocs'],
        "init_xml" : ['ocs_idu_view.xml'],
        "demo_xml" : [],
        "update_xml" : [
                        'security/ocs_idu_security.xml',
                        'security/ir.model.access.csv',
                        'ocs_idu_workflow.xml',
                        'ocs_idu_view.xml'
                        ],
        "installable": True
}
