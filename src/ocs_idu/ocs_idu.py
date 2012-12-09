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
# INSTITUTO DE DESARROLLO URBANO - BOGOTA (COLOMBIA)
#
# Customization developed by:
# ANGEL MARIA FONSECA CORREA - CIO
# ANDRES IGNACIO BAEZ ALBA - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
#
###############################################################################

from osv import fields,osv
from base_geoengine import geo_model
from crm import crm
from tools.translate import _

class crm_claim(crm.crm_case,osv.osv):
    """
    Inherit from ocs and ocs crm_claim
    """

    def _check_is_outsourced(self,cr,uid,ids,fieldname,arg,context=None):
        """
        Check if the citizen service point is outsourced, with this
        validates when is csp outsourced
        """
        res = {}
        for claim in self.browse(cr, uid, ids, context = context):
            res[claim.id] = claim.csp_id.is_outsourced
        return  res

    def case_review(self, cr, uid, ids, *args):
        """Review the Case
        :param ids: List of case Ids
        """
        cases = self.browse(cr, uid, ids)
        self.message_append(cr, uid, cases, _('Review'))
        for case in cases:
            data = {'state': 'review', 'active': True }
            if not case.user_id:
                data['user_id'] = uid
            self.write(cr, uid, case.id, data)
        self._action(cr, uid, cases, 'review')
        return True

    _name="crm.claim"
    _inherit="crm.claim"
    _columns = {
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True, readonly=True),
        'date_deadline': fields.date('Deadline',readonly=True),
        'state':fields.selection([('draft', 'New'),('open', 'In Progress'),('cancel', 'Cancelled'),
                                  ('review','Review'),('done', 'Closed'),('pending', 'Pending')],
                                 'State',help='Introduce a new state between open and done, in this step,\
                                  other people makes a review and approve the response given to citizen'),
        'is_outsourced':fields.function(_check_is_outsourced,type='boolean',string='Is Outsourced',method=True),
    }

crm_claim()

class ocs_citizen_service_point(geo_model.GeoModel):
    """
    IDU High Specific Requeriment for Office of Citizen Service  with Outsourced partner
    """

    def _check_is_outsourced (self,cr,uid,context):
        """
        Verifiy Context to Set default value
        """
        if context.has_key("is_outsourced"):
            if context["is_outsourced"]:
                return True
            else :
                return False
        return False

    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Contract """
        res = {}
        for csp in self.browse(cr, uid, ids, context = context):
            if csp.is_outsourced:
                res[csp.id] = "{0} / {1} ".format(csp.tract_id.full_name, csp.name)
            else :
                res[csp.id] = "{0}".format(csp.name)
        return  res

    _name="ocs.citizen_service_point"
    _inherit="ocs.citizen_service_point"
    _columns = {
        'is_outsourced':fields.boolean('is Outsourced',help='When is set, this is an outsourced citizen service point'),
        'tract_id':fields.many2one('ocs.tract','Tract Id'),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
    }
    _defaults={
        'is_outsourced':  _check_is_outsourced,
    }
    _rec_name = 'full_name'
ocs_citizen_service_point()


class ocs_contract(osv.osv):
    """
    Contract Information
    """
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
