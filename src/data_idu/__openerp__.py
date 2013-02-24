{
  'name': 'Módulo para crear datos del IDU',
  'version': 'openerp6.1-rev2013022400',
  'category': 'Generic Modules/Others',
  'description': "Módulo para cargar datos usados en el IDU",
  'author': 'STRT',
  'website': 'http://www.idu.gov.co',
  'depends': ['base'],
  'init_xml': [
      'crm.case.categ.csv',
      'crm.case.channel.csv',
      'ocs.contract.csv',
      'ocs.tract.csv',
      'ocs.citizen_service_point.csv',
      'ocs.claim_classification.csv',
      'ocs.claim_solution_classification.csv',
      'res.partner.csv',
      'ocs_orfeo.dependencia.csv',
  ],
  'update_xml': [],
  'installable': True,
}
