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
#
#    Creado por Andres Ignacio Baez Alba
#
##############################################################################

from osv import osv, fields

class urban_bridge_wizard_import_elements(osv.osv_memory):
    """
    Wizard to load information from excel
    """ 
    _name="urban_bridge.wizard.import_elements"
    _columns={
        'srid':fields.integer('Source SRID','Source Data System Reference'),
        'file':fields.binary('File'),
    }
    
    def next (self,cr,uid,ids,context=None):
        bridges = self.browse(cr,uid,ids,context=None)
        
        return {'type': 'ir.actions.act_window_close'}
     
     
     