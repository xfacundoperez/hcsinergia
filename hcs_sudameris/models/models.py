# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

#Regerencia de códigos de datos
_TipoGrupo = [('90', 'Payroll'), ('94', 'Proveedores')]

_TipoCobro = [('1', 'Sueldo'), ('2', 'Aguinaldo'), ('3', 'Anticipo de Sueldo'),
('4', 'Otras Remuneraciones'), ('7', 'Acreditación Tarjeta Prepaga'), ('8', 'Pago de Licencias')]

_Moneda = [('6900', 'Guaraníes'), ('1', 'Dólares Americanos')]

_TipoDocumento = [('1', 'CEDULA DE IDENTIDAD'), ('2', 'CREDENCIAL CIVICA'), ('3', 'R.U.C.'),
('4', 'PASAPORTE'), ('5', 'DNI-DOC.NAC.IDENTID.'), ('6', 'REGISTRO DE COMERCIO'),
('7', 'LIB.DE ENROLAMIENTO'), ('10', 'GARANTIA'), ('15', 'Entidades Públicas'), 
('16', 'CARNET-INMIGRACIONES'), ('98', 'No Registra'),  ('99', 'Inst. Financieras'),
('20', 'REPRES.DIPLOMATICAS')]

_ModalidadPago = [('20', 'Débito en Cta. Cte'), ('21', 'Débito Caja de Ahorro')]

_TipoContrato = [('1', 'Contrato Por Tiempo Indefinido'), ('2', 'Contrato Por Tiempo Definido')]

_CodigoPaises = [('105', 'BRASIL'), ('845', 'URUGUAY'), ('63', 'ARGENTINA'), ('586', 'PARAGUAY'),
('589', 'PERU'), ('13', 'AFGANISTAN'), ('17', 'ALBANIA'), ('20', 'ALBORANYPEREJIL,I'),
('23', 'ALEMANIA'), ('31', 'ALTOVOLTA'), ('37', 'ANDORRA'), ('39', 'AUSTRALIA'),
('40', 'ANGOLA'), ('43', 'ANTIGUA,ISLA'), ('47', 'ANTILLASHOLANDESAS'),
('53', 'ARABIASAUDITA'), ('59', 'ARGELIA'), ('69', 'AUSTRALIA'), ('72', 'AUSTRIA'),
('77', 'BAHAMAS,ISLAS'), ('80', 'BAHREIN'), ('81', 'BANGLADESH'), ('83', 'BARBADOS'),
('85', 'TOKELAN,ISLAS'), ('87', 'BELGICA-LUXEMBURGO'), ('88', 'BELICE'), ('90', 'BERMUDAS'),
('93', 'BIRMANIA'), ('97', 'BOLIVIA'), ('101', 'BOTSWANA'), ('108', 'BRUNEI'),
('111', 'BULGARIA'), ('115', 'BURUNDI'), ('119', 'BUTAN'), ('127', 'CABOVERDE,RCA.DE'),
('137', 'CAIMAN,ISLAS'), ('141', 'CAMBOYA'), ('145', 'CAMERUM'), ('149', 'CANADA'),
('153', 'CANARIAS,ISLAS'), ('159', 'CIUDADDELVATICANO'), ('165', 'COCOS,ISLAS'), ('169', 'COLOMBIA'),
('173', 'COMORAS'), ('177', 'CONGO'), ('183', 'COOK,ISLAS'), ('187', 'COREADELNORTE'),
('190', 'COREADELSUR'), ('193', 'COSTADEMARFIL'), ('196', 'COSTARICA'), ('199', 'CUBA'),
('203', 'CHAD'), ('207', 'CHECOSLOVAQUIA'), ('211', 'CHILE'), ('215', 'CHINA'),
('218', 'TAIWAN'), ('221', 'CHIPRE'), ('229', 'DENIN'), ('232', 'DINAMARCA'),
('235', 'DOMINICA,ISLA'), ('239', 'ECUADOR'), ('240', 'EGIPTO'), ('242', 'ELSALVADOR'),
('244', 'EMIRATOSARABESUNID'), ('245', 'ESPAÑA'), ('249', 'ESTADOSUNIDOS'), ('253', 'ETIOPIA'),
('259', 'FEROE,ISLAS'), ('267', 'FILIPINAS'), ('271', 'FINLANDIA'), ('275', 'FRANCIA'),
('281', 'GABON'), ('285', 'GAMBIA'), ('289', 'GHANA'), ('293', 'GIBRALTAR'),
('297', 'GRENADA'), ('301', 'GRECIA'), ('305', 'GROENLANDIA'), ('309', 'GUADALUPEYDEPENDEN'),
('313', 'GUAM'), ('317', 'GUATEMALA'), ('325', 'GUAYANAFRANCESA'), ('329', 'GUINEA'),
('331', 'GUINEAECUATORIAL'), ('334', 'GUINEABISSAU'), ('337', 'GUYANA'), ('341', 'HAITI'),
('345', 'HONDURAS'), ('351', 'HONGKONG'), ('355', 'HUNGRIA'), ('361', 'INDIA'),
('365', 'INDONESIA'), ('369', 'IRAK'), ('372', 'IRAN'), ('375', 'IRLANDA-EIRE-'),
('379', 'ISLANDIA'), ('383', 'ISRAEL'), ('386', 'ITALIA'), ('391', 'JAMAICA'),
('399', 'JAPON'), ('403', 'JORDANIA'), ('410', 'KENIA'), ('413', 'KUWAIT'),
('420', 'LAOS'), ('426', 'LESOTHO'), ('431', 'LIBANO'), ('434', 'LIBERIA'),
('438', 'LIBIA'), ('445', 'LUXEMBURGO'), ('447', 'MACAO'), ('450', 'MADAGASCAR'),
('455', 'MALASIA'), ('458', 'MALAWI'), ('461', 'MALDIVAS'), ('464', 'MALI'),
('467', 'MALTA'), ('474', 'MARRUECOS'), ('477', 'MARTINICA'), ('485', 'MAURICIO'),
('488', 'MAURITANIA'), ('493', 'MEXICO'), ('497', 'MONGOLIAREP.POPULAR'), ('501', 'MONTSERRAT,ISLA'),
('504', 'MOYOTTE'), ('505', 'MOZAMBIQUE'), ('508', 'NAURU'), ('511', 'NAVIDAD,ISLAS'),
('517', 'NEPAL'), ('521', 'NICARAGUA'), ('525', 'NIGER'), ('528', 'NIGERIA'),
('531', 'NIUE,ISLA'), ('535', 'NORFOLK,ISLA'), ('538', 'NORUEGA'), ('542', 'NUEVACALEDONIA'),
('545', 'PAPUANUEVAGUINEA'), ('548', 'NUEVAZELANDIA'), ('551', 'NUEVASHEBRIDAS'), ('556', 'OMAN'),
('563', 'PACIFICO,ISLAS-ADMIN'), ('566', 'PACIFICO,ISLAS-POSES'), ('569', 'PACIFICO,ISLAS-FIDEI'), ('573', 'HOLANDA'),
('576', 'PAKISTAN'), ('580', 'PANAMA'), ('593', 'PITCAIRN,ISLA'), ('599', 'POLINESIAFRANCESA'),
('603', 'POLONIA'), ('607', 'PORTUGAL'), ('611', 'PUERTORICO'), ('618', 'QATAR'),
('628', 'REINOUNIDO'), ('640', 'REPUBLICACENTROAFRI'), ('647', 'REPUBLICADOMINICANA'), ('660', 'REUNION,ISLA'),
('665', 'RODESIA'), ('670', 'RUMANIA'), ('675', 'RWANDA'), ('690', 'SAMOAOCCIDENTAL,EDO'),
('695', 'S.CRISTOBALNEVISY'), ('700', 'SANPEDROYMIQUELON'), ('705', 'SANVICENTE,ISLA'), ('710', 'SANTAELENA'),
('715', 'SANTALUCIA,ISLA'), ('720', 'SANTOTOMEYPRINCIP'), ('728', 'SENEGAL'), ('731', 'SEYCHELLES'),
('735', 'SIERRALEONA'), ('741', 'SINGAPUR'), ('744', 'SIRIA'), ('748', 'SOMALIA'),
('750', 'SRILANKA'), ('756', 'SUDAFRICAYNAMIBIA'), ('759', 'SUDAN'), ('764', 'SUECIA'),
('767', 'SUIZA'), ('770', 'SURINAM'), ('776', 'TAILANDIA'), ('780', 'TANZANIA'),
('783', 'DJIBOUTI'), ('785', 'TERRIT.ALTACOMIS.PA'), ('800', 'TOGO'), ('810', 'REINODETONGA'),
('815', 'TRINIDADYTOBAGO'), ('820', 'TUNEZ'), ('823', 'TURCASYCAICOS,ISLA'), ('827', 'TURQUIA'),
('833', 'UGANDA'), ('840', 'U.R.S.S.'), ('850', 'VENEZUELA'), ('855', 'VIETNAM'),
('863', 'VIRGENES,ISLAS-BRITA'), ('866', 'VISGENES,ISLAS-U.S.A'), ('870', 'FIDJI,ISLAS'), ('875', 'WALLISYFUTUNA,ISL'),
('880', 'YEMENDELNORTE'), ('881', 'YEMENDELSUR'), ('885', 'YUGOESLAVIA'), ('888', 'ZAIRE'),
('890', 'ZAMBIA'), ('895', 'ZONADELCANALDEPA'), ('896', 'HOLANDA'), ('897', 'ESCOCIA')]

class sudameris_salary_inherit(models.Model):
  _inherit = 'hr.employee'

  apellidos = fields.Char(string="Apellidos", required=True)
  tipo_documento = fields.Selection(selection=_TipoDocumento, string="Tipo de identificación", digits=(2), default="5")
  vencimiento_documento = fields.Date(string="Vencimiento de identificación")
  tipo_contrato = fields.Selection(selection=_TipoContrato, string="Tipo de Contrato", digits=(1), default="2")
  tipo_moneda = fields.Selection(string="Tipo de moneda", selection=_Moneda, default="6900")
  salario_bruto = fields.Float(string="Salario", digits=(18,2))
  codigo_direccion = fields.Integer(default=1, digits=(3))
  tipo_grupo = fields.Selection(selection=_TipoGrupo, string="Tipo de Grupo", digits=(3), default="90")
  ejecutivo = fields.Integer(string="Ejecutivo")
  fecha_ingreso = fields.Date(string="Fecha de ingreso")
  fecha_fin_contrato = fields.Date(string="Fecha de ingreso")
  numero_sucursal = fields.Char(string="Sucursal del Empleado")
  numero_cuenta = fields.Char(string="Número de la Cuenta", digits=(9), readonly=True)
  nombre_cuenta = fields.Char(string="Descripción de la Cuenta", digits=(30), readonly=True)

class sudameris_employee_salary_movement(models.Model):
  _name = 'sudameris_employee_salary_movement'
  _description = 'Movimientos de salario del empleado'
  _rec_name = 'empleado'

  def button_aproved(self):
    for rec in self:
      rec.state = 'aprobado'
      
  def button_reset(self):
    for rec in self:
      rec.state = 'preliquidacion'

  def _create_txt(self):
    # Composición del nombre: ENTIDAD_SERVICIO_FECHA+HORA.TXT
    # Ejemplo: GESTION_PAGODESALARIOS_20200519103252.TXT
    # Tipo de dato: I: Entero, C: Caracter o Alfanumérico, D: Fecha, N: Numérico decimal con dos valores decimales
    ## CABECERA: Identificador de cabecera(C:1);Código de contrato(I:9);E-mail asociado al Servicio(C:50);Moneda(I:4);Importe(N:15.2);Cantidad de Documentos(I:5); \
    ## Fecha de Pago(D:8);Referencia(C:18);Tipo de Cobro(I:3);Debito Crédito(I:1);Cuenta Débito(I:9);Sucursal Débito(I:3);Módulo Débito(I:3); \ 
    ## Moneda Débito(I:4)Operación Débito(I:9);Sub Operación Débito(I:3);Tipo Operación Débito(I:3)
    # Ejemplo CABECERA: H;999;mail@entidad.com;6900;52000.00;1;19/05/20; 202005902952101999;1;1;1982073;10;20;6900;0;0;0
    ## DETALLE: Identificador del detalle(C:1);Concepto(C:30);Primer Apellido(C:15);Segundo Apellido(C:15);Primer Nombre(C:15);Segundo Nombre(C:15); \ 
    ## País(I:3);Tipo de Documento(I:2);Número de Documento(C:15);Moneda(I:4);Importe(N:15.2);Fecha de Pago(D:8);Modalidad de Pago(I:3); \ 
    ## Número de Cuenta(I:9);Sucursal Empleado(I:3);Moneda Empleado(I:4);Operación Empleado(I:9);Tipo de Operación Empleado(I:3);Suboperación Empleado(I:3); \ 
    ## Referencia(C:18);Tipo de Contrato(I:3);Sueldo Bruto(N:15.2);Fecha Fin de Contrato(D:8);
    # Ejemplo DETALLE: D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99

    _txt = 'H;999;mail@entidad.com;6900;52000.00;1;19/05/20;202005902952101999;1;1;1982073;10;20;6900;0;0;0\n'
    for rec in self:
      if rec.state == 'aprobado':
        empleado = rec.empleado
        # Obtengo los nombres y los apellidos
        empleado_nombres = empleado.name.split(' ')
        if (len(empleado_nombres) == 1):
          empleado_nombres.append('')
        empleado_apellidos = empleado.apellidos.split(' ')
        if (len(empleado_apellidos) == 1):
          empleado_apellidos.append('')
        # Genero el detalle con los datos del empleado
        #D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
        _detalle = "D;PAGO DE SALARIO NUEVO SISTEMA;{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16};{17};{18};{19};{20}\n".format(
          empleado_apellidos[0],
          empleado_apellidos[1],
          empleado_nombres[0],
          empleado_nombres[1],
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
          '',
        )
        _txt += _detalle
    raise ValidationError(_txt)

  empleado = fields.Many2one(string='Empleado', comodel_name='hr.employee')
  identification_id = fields.Char(string='Nº identificación', related='empleado.identification_id', required=True)
  empleado_nombres = fields.Char(string='Nombre del Empleado', related='empleado.name', readonly=True)
  empleado_apellidos = fields.Char(string='Nombre del Empleado', related='empleado.apellidos', readonly=True)
  moneda = fields.Selection(selection=_Moneda, string="Moneda", related='empleado.tipo_moneda', readonly=True)
  salario_bruto_def = fields.Float(string="Salario del empleado", digits=(18, 2), related='empleado.salario_bruto', readonly=True)
  
  salario_importe = fields.Float(string="Salario a pagar", digits=(18, 2))
  tipo_cobro = fields.Selection(selection=_TipoCobro, string="Tipo de Cobro", default="1")
  fecha_pago = fields.Date(string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
  modalidad_pago = fields.Selection(string="Modalidad de pago", selection=_ModalidadPago, default="21")
  codigo_operacion = fields.Char(string="Operación")
  codigo_suboperacion = fields.Char(string="Suboperación")
  tipo_operacion = fields.Char(string="Tipo de Operación")
  referencia = fields.Char(string="Referencia")
  state = fields.Selection(string="Estado", selection=[('preliquidacion', 'Preliquidación'), ('aprobado', 'Aprobado'), ('enproceso', 'En Proceso'), ('cancelado', 'Cancelado'), ('liquidado', 'Liquidado')], default='preliquidacion')