# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, osv
import time
import datetime

#TODO: Cuando un proyecto se cierra verificar que los sub proyectos esten terminados o cancelados
class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"

    _columns = {
        'etapa_id': fields.many2one('project_idu.etapa','Etapa', select=True),
        'clasificacion_id': fields.many2one('project_idu.proyecto_tipificacion','Clasificación', select=True),
        #Punto de inversion
        #Centro de costo
        #Fuente de Financiacion
    }

project()

class task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"

    def _participacion_ciudadana(self, cr, uid, ids, prop, unknow_none, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context):
            if record['clasificacion_id']:
                participacion_ciudadana = record['clasificacion_id'].participacion_ciudadana
                res.append((record['id'], participacion_ciudadana))
            else:
                res.append((record['id'], False))
        return dict(res)

    def _get_task_ids_from_tipificacion(self, cr, uid, ids, context=None):
        result = {}
        for record in self.pool.get('project_idu.tarea_tipificacion').browse(cr, uid, ids, context=context):
            for task in record.task_ids:
                result[task.id] = True
        return result.keys()

    _columns = {
        'clasificacion_id': fields.many2one('project_idu.tarea_tipificacion','Clasificación', select=True),
        'producto_intermedio_id': fields.many2one('project_idu.producto_intermedio','Producto intermedio afectado', 
            select=True,
            domain="[('project_id','=',project_id)]"),
        'etapa_id': fields.related(
            'project_id',
            'etapa_id',
            type="many2one",
            relation="project_idu.etapa",
            string="Etapa del Proyecto",
            store=True),
        'numero_convocados': fields.integer('Número de convocados'),
        'numero_asistentes': fields.integer('Número de asistentes'),
        'participacion_ciudadana': fields.function(_participacion_ciudadana, type="boolean",
            string='Participación ciudadana',
            help='Requiere de participación ciudadana? debe indicar número de convocados y número de participantes',
            store={
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['clasificacion_id'], 10),
                'project_idu.tarea_tipificacion': (_get_task_ids_from_tipificacion, ['participacion_ciudadana'], 20),
            }),
    }

    _defaults = {
        'project_id' : lambda self, cr, uid, context : context['project_id'] if context and 'project_id' in context else None, #Set by default the project given in the context
        'producto_intermedio_id' : lambda self, cr, uid, context : context['producto_intermedio_id'] if context and 'producto_intermedio_id' in context else None
    }

task()

class project_idu_etapa(osv.osv):
    _name = "project_idu.etapa"

    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
    }

project_idu_etapa()

#TODO: De acuerdo a la etapa del proyecto desplegar la tipificación correspondiente de actividades
class project_idu_tarea_tipificacion(osv.osv):
    _name = "project_idu.tarea_tipificacion"
    _description = "Clasificación de las tareas dentro de los proyectos"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nombre'),
        'parent_id': fields.many2one('project_idu.tarea_tipificacion','Clasificación padre', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_idu.tarea_tipificacion', 'parent_id', string='Clasificaciones hijas'),
        'sequence': fields.integer('Sequence', select=True, help="Secuencia para el ordenamiento en las listas"),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'active':fields.boolean('Active',help='Activo/Inactivo'),
        'participacion_ciudadana':fields.boolean('Participación ciudadana',help='Este tipo de tareas requiere la participación de la ciudadanía?'),
        'task_ids': fields.one2many('project.task', 'clasificacion_id', string='Tareas relacionadas'),
    }
    _defaults = {
        'active': True,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_idu_tarea_tipificacion where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! No puede crear clasificaciones recursivas.', ['parent_id']),
    ]

project_idu_tarea_tipificacion()

class project_idu_proyecto_tipificacion(osv.osv):
    _name = "project_idu.proyecto_tipificacion"
    _description = "Clasificación de los proyectos del IDU"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nombre'),
        'parent_id': fields.many2one('project_idu.proyecto_tipificacion','Clasificación padre', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_idu.proyecto_tipificacion', 'parent_id', string='Clasificaciones hijas'),
        'sequence': fields.integer('Sequence', select=True, help="Secuencia para el ordenamiento en las listas"),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'active':fields.boolean('Active',help='Activo/Inactivo'),
    }
    _defaults = {
        'active': True,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_idu_proyecto_tipificacion where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! No puede crear clasificaciones recursivas.', ['parent_id']),
    ]

project_idu_proyecto_tipificacion()

class project_idu_producto_intermedio(osv.osv):
    _name = "project_idu.producto_intermedio"
    _description = "Productos secundarios que no son parte del objeto contractual"

    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'clasificacion_id': fields.many2one('project_idu.producto_intermedio_tipificacion', 'Clasificación', help="Tipo de producto intermedio"),
        'description': fields.text('Descripcion'),
        'ubicacion': fields.char('Ubicación', size=255),
        'imagen': fields.binary("Imagen", help="Imagen del producto intermedio"),
        'active':fields.boolean('Activo',help='Activo/Inactivo'),
        'state':fields.selection([('abierto', 'Abierto'),('cerrado', 'Cerrado'),('aplazado', 'Aplazado'),('anulado', 'Anulado')],'Estado'),
        'task_ids': fields.one2many('project.task', 'producto_intermedio_id', string='Tareas que afectan este producto'),
        'project_id': fields.many2one('project.project','Proyecto', select=True, ondelete='cascade'),
    }
    _defaults = {
        'active': True,
        'state': 'abierto',
        'project_id' : lambda self, cr, uid, context : context['project_id'] if context and 'project_id' in context else None #Set by default the project given in the context
    }

project_idu_producto_intermedio()

class project_idu_producto_intermedio_tipificacion(osv.osv):
    _name = "project_idu.producto_intermedio_tipificacion"
    _description = "Clasificación de los productos intermedios del IDU"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nombre'),
        'parent_id': fields.many2one('project_idu.producto_intermedio_tipificacion','Clasificación padre', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_idu.producto_intermedio_tipificacion', 'parent_id', string='Clasificaciones hijas'),
        'sequence': fields.integer('Sequence', select=True, help="Secuencia para el ordenamiento en las listas"),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'active':fields.boolean('Active',help='Activo/Inactivo'),
    }
    _defaults = {
        'active': True,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_idu_producto_intermedio_tipificacion where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! No puede crear clasificaciones recursivas.', ['parent_id']),
    ]

project_idu_proyecto_tipificacion()

class project_pmi_wbs_item(osv.osv):
    _name = "project_pmi.wbs_item"
    _inherit = "project_pmi.wbs_item"

    def _get_wbs_item_and_parents(self, cr, uid, ids, context=None):
        return super(project_pmi_wbs_item, self)._get_wbs_item_and_parents(cr, uid, ids, context=context)

    def _opportunity_evaluation(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['date_deadline','date_end'], context=context)
        res = {}
        for record in reads:
            opportunity = '';
            if record['date_deadline']:
                today = datetime.datetime.now().date()
                date_deadline = datetime.datetime.strptime(record['date_deadline'], '%Y-%m-%d').date()
                if record['date_end']:
                    date_end = datetime.datetime.strptime(record['date_end'], '%Y-%m-%d').date()
                    if date_end <= date_deadline:
                        opportunity = 'is_on_time'
                    elif date_end > date_deadline:
                        opportunity = 'is_late'
                elif today >= date_deadline:
                    opportunity = 'is_not_finished'
            res[record['id']] = opportunity
        return res

    _columns = {
        'opportunity_evaluation': fields.function(_opportunity_evaluation, type="char", translate=True, string='is late, on time, not finished?',store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['date_end','date_deadline'], 10),
        }),
    }

project_pmi_wbs_item()

#===============================================================================
# ACTIVIDADES
# -----------
# 
# Contratista:
#     * Crea actividad de tipo reunión de inicio
#     * Ingresa la deadline
#     * Ingresa acta de la reunión
#         * Ingresa el número de personas convocadas y listado
#         * Ingresa el número de personas que asistieron y listado
#     * Ingresa documentos de soporte
#     * Agrega compromisos como actividad hija (tipo de actividad compromiso)
# 
# Interventor:
#     * Revisa actividad
#     * Aprueba o Rechaza
# 
# Coordinador Social IDU:
#     * Revisa actividad y da comentarios
#     * Genera estadísticas
# 
# Elementos a inventariar
# - Tipo
#     * Actas de vecindad
#     * Actas de compromiso
#     * Puntos Satelite
#     * Comite CREA
# - Descripción
# - Estado (pendiente, live, done)
# - Imágen
# - Adjuntos
# - Ubicación (opcional)
# - Afectado por Tarea many2many
# 
#
#TODO: Crear árbol de tipo de actividades con validación para cierre
#TODO: Crear boton para manejar adjuntos desde la actividad
#TODO: Crear clasificación de adjuntos
#TODO: Crear grupos para roles de usuario con acl y reglas de dominio para acceso a proyecto y modificación
#TODO: Crear workflow en la actividad para aprobación de actividades
#TODO: Crear vistas con indicadores de gestión social
