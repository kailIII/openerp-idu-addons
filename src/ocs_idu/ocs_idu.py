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
# Generated by the OpenERP plugin for Dia ! and modified by Andres Ignacio Baez

# This module is not general, is for IDU (Instituto de Desarrollo Urbano) customization

from osv import fields,osv
from base_geoengine import geo_model

class ocs_construction_claim(geo_model.GeoModel):
    _name="ocs.construction_claim"
    _inherit="crm.claim"
    _columns = {
        'csp_id':fields.many2one('ocs.crea_point','Crea Point',domain="[('close_date','=',False)]",
                                 help='Citizen Service Point',required = True,
                                 readonly = False, states = {'done':[('readonly',True)]}),
        'state':fields.selection([('draft', 'New'),('open', 'In Progress'),('cancel', 'Cancelled'),
                                  ('done', 'Closed'),('pending', 'Pending'),('review','Review')],
                                 'State',help='Introduce a new state between open and done, in this step,\
                                  other people makes a review and approve the response given to citizen')        
    }
ocs_construction_claim()

class ocs_crea_point(geo_model.GeoModel):
    """
    IDU High Specific Requeriment for Office of Citizen Service  with Outsource partner    
    """
    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Contract """
        res = {}
        for crea_point in self.browse(cr, uid, ids, context = context):
                res[crea_point.id] = "{0} / {1} ".format(crea_point.tract_id.full_name, crea_point.name)                         
        return  res
    
    _name="ocs.crea_point"
    _inherit="ocs.citizen_service_point"
    _columns = {
        'tract_id':fields.many2one('ocs.tract','Tract Id'),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),        
    }
    _rec_name = 'contract_id'
ocs_crea_point()


class ocs_contract(osv.osv):
    _name="ocs.contract"
    _columns = {
        'contract_id': fields.char('Contract Number',size=20,help="Contract Number or Serial", required=True),
        'start_date': fields.datetime('Start Date',help="When contract start", required=True),
        'end_date': fields.datetime('End Date',help="When contract ends"),
        'partner_id': fields.many2one('res.partner','Contractor',size=30,required=True),
    }
    _rec_name = 'contract_id'
ocs_contract()



class ocs_tract(osv.osv):
    """ This class is only for IDU (Instituto Desarrollo Urbano Colombia), who need take control about claims 
    in building projects, from outsourcing  """    
    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Contract """
        res = {}
        for tract in self.browse(cr, uid, ids, context = context):
                res[tract.id] = "{0} / {1} ".format(tract.contract_id.contract_id, tract.name)                         
        return  res 
    
    _name = 'ocs.tract'
    _columns = {
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        'road_id': fields.char('Road ID',size = 16,help="Road Identification Number",required=True),
        'name': fields.char('Description',size=20,required=True),
        'contract_id': fields.many2one('ocs.contract','Contract',required=True),
    }
    _rec_name = 'full_name'
ocs_tract()



     
    
    
    
    
    
    