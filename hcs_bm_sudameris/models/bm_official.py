# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api, _
from odoo.modules.module import get_module_resource
from datetime import datetime, date
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class BM_Official(models.Model):
    _name = "bm.official"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tabla de funcionarios"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hcs_bm_sudameris', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.model
    def _default_country(self):
        return self.env['res.country'].search([('code_number','=','586')],limit=1).id

    @api.depends('job_id')
    def _compute_job_title(self):
        for official in self.filtered('job_id'):
            official.job_title = official.job_id.name

    @api.depends('department_id')
    def _compute_parent_id(self):
        for official in self.filtered('department_id.manager_id'):
            official.parent_id = official.department_id.manager_id

    @api.depends('parent_id')
    def _compute_coach(self):
        for official in self:
            manager = official.parent_id
            previous_manager = official._origin.parent_id
            if manager and (official.coach_id == previous_manager or not official.coach_id):
                official.coach_id = manager
            elif not official.coach_id:
                official.coach_id = False

    @api.depends('name')
    def _compute_name(self):
        for official in self:
            _nombre = official.name_first
            if (official.name_second):
                _nombre = "{} {}".format(
                    official.name_first, official.name_second)
            _apellido = official.surname_first
            if (official.surname_second):
                _apellido = "{} {}".format(
                    official.surname_first, official.surname_second)
            if _nombre and _apellido:
                official.name = '{} {}'.format(_nombre, _apellido)

    @api.depends('departured')
    def _compute_departured(self):
        for official in self:
            official.departured = self.env['bm.official.departure'].search(['&', ('official', '=', official.id), ('state', '=', 'active')], order='id desc', limit=1)

    @api.depends('welcome_kit', 'gross_salary')
    def _compute_welcome_kit(self):
        # Se computa solo si est?? en borrador
        if self.state in ['draft']:  # Solo si el funcionario no est?? listo, obtengo los kits y le asigno el kit minimo
            for kit in self.env['bm.product'].search([('product_type', '=', 'kit')], order='minimum_salary desc'):
                if self.gross_salary >= kit.minimum_salary:
                    self.welcome_kit = None
                    self.welcome_kit = [(4, kit.id)]
                    break
            # Asigno la segmentacion segun documentacion
            if self.gross_salary > 0 and self.gross_salary < 5000000:
                self.segmentation = '1'
            elif self.gross_salary >= 5000000 and self.gross_salary < 35000000:
                self.segmentation = '2'
            elif self.gross_salary >= 35000000:
                self.segmentation = '3'
            else:
                self.segmentation = None
        #elif self.state in ['check']:  # Solo si el funcionario no est?? listo, obtengo los kits y le asigno el kit minimo
        #    if not (self._origin.segmentation == self.segmentation):
        #        self.segmentation_check = True
    

    # Basic info
    name = fields.Char(string="Nombre", compute="_compute_name", required=False)
    name_first = fields.Char(string="Primer Nombre", required=True)
    name_second = fields.Char(string="Segundo Nombre")
    surname_first = fields.Char(string="Primer Apellido", required=True)
    surname_second = fields.Char(string="Segundo Apellido")
    gender = fields.Selection([
        ('male', 'Hombre'),
        ('female', 'Mujer'),
        ('other', 'Otro')
    ], "Sexo", default="male", tracking=True)
    marital = fields.Selection([
        ('single', 'Soltero(a)'),
        ('married', 'Casado(a)'),
        ('cohabitant', 'Cohabitante Legal'),
        ('widower', 'Viudo(a)'),
        ('divorced', 'Divorciado(a)')
    ], string='Estado Civil', default='single', tracking=True)
    identification_id = fields.Char(string='C??dula de identidad', tracking=True)
    identification_type = fields.Selection([
        ('1', 'CEDULA DE IDENTIDAD'),
        ('2', 'CREDENCIAL CIVICA'),
        ('3', 'R.U.C.'),
        ('4', 'PASAPORTE'),
        ('5', 'DNI-DOC.NAC.IDENTID.'),
        ('6', 'REGISTRO DE COMERCIO'),
        ('7', 'LIB.DE ENROLAMIENTO'),
        ('10', 'GARANTIA'),
        ('15', 'Entidades P??blicas'),
        ('16', 'CARNET-INMIGRACIONES'),
        ('98', 'No Registra'),
        ('99', 'Inst. Financieras'),
        ('20', 'REPRES.DIPLOMATICAS')], string="Tipo de C??dula", digits=(2), default="1")
    identification_expiry = fields.Date(string="Vencimiento de C??dula", required=True)
    country = fields.Many2one('res.country', 'Nacionalidad (Pa??s)', default=_default_country, required=True, tracking=True)
    city = fields.Many2one('res.country.state', 'Localidad', domain="[('country_id', '=?', country)]", required=True)
    department = fields.Many2one('res.country.departament', 'Departamento', domain="[('state_id', '=?', city)]", required=True)
    neighborhood = fields.Many2one('res.country.neighborhood', 'Barrio', domain="[('departament_id', '=?', department)]", required=True)
    real_address = fields.Char(string="Direcci??n", digits=(50), required=True)
    house_no = fields.Char(string="Nro. Casa", digits=(3), required=True)
    street_transversal = fields.Char(string="Calle Transversal", digits=(35))
    reference = fields.Char(string="Referencia")
    address_code = fields.Integer(default=1, digits=(3))
    birthday = fields.Date('Fecha de nacimiento', tracking=True, required=True)
    country_of_birth = fields.Many2one('res.country', 'Pa??s de Nacimiento', required=True, tracking=True)
    place_of_birth = fields.Many2one('res.country.state', 'Lugar de nacimiento', domain="[('country_id', '=?', country_of_birth)]", required=True, tracking=True)

    # contact
    email = fields.Char('E-mail')
    work_phone = fields.Char('Tel??fono Laboral', compute="_compute_phones", store=True, readonly=False)
    particular_phone = fields.Char('Tel??fono particular')
    mobile_phone = fields.Char('Tel??fono celular', required=True)
    idenfitication_image_front = fields.Binary(
        string="C??dula de Identidad (Frente)", max_width=100, max_height=100)
    idenfitication_image_back = fields.Binary(
        string="C??dula de Identidad (Dorso)", max_width=100, max_height=100)
    idenfitication_image_pdf = fields.Binary(string="C??dula de Identidad (PDF)")
    idenfitication_image_pdf_name = fields.Char(string="Nombre de c??dula de identidad (PDF)")
    image_1920 = fields.Image(default=_default_image)

    # Bank info
    contract_type = fields.Selection([
        ('1', 'Contrato Por Tiempo Indefinido'),
        ('2', 'Contrato Por Tiempo Definido')], string="Tipo de Contrato", required=True, digits=(1), default="2")
    currency_type = fields.Selection([
        ('6900', 'Guaran??es'),
        ('1', 'D??lares Americanos')], string="Tipo de moneda", default="6900")
    gross_salary = fields.Float(string="Salario Bruto", digits=(18, 2), required=True)
    group_type = fields.Selection([
        ('90', 'Payroll'),
        ('94', 'Proveedores')], string="Tipo de Grupo", digits=(3), default="90")
    executive = fields.Integer(string="Ejecutivo")
    admission_date = fields.Date(string="Fecha de ingreso", required=True)
    contract_end_date = fields.Date(string="Fecha de fin de contrato")
    branch_number = fields.Char(string="Sucursal del Funcionario")
    account_number = fields.Char(string="N??mero de la Cuenta", digits=(9))
    account_name = fields.Char(string="Descripci??n de la Cuenta", digits=(30))
    account_status = fields.Selection([
        ('0', 'Cuenta Activa'),
        ('71', 'Cuenta Inactiva'),
        ('74', 'WK Pendiente de Entrega'),
        ('99', 'Cuenta Cancelada')], string="Estado de la Cuenta")
    segmentation_aproved = fields.Boolean("Aprobar segmento")
    segmentation = fields.Selection([
        ('1', 'SUDAMERIS'),
        ('2', 'SUDAMERIS PLUS'),
        ('3', 'SUDAMERIS ELITE')], string="Recomendaci??n Segmentaci??n")
    segmentation_check = fields.Boolean("Verificar recomendaci??n", default=False)
    cam_check = fields.Boolean(default=False)
    reject_reason = fields.Text('Motivo de rechazo')
    sub_segmentation = fields.Selection([
        ('S', 'Crear'),
        ('N', 'No crear')], string="Sub segmentaci??n", digits=(1), default="N")
    welcome_kit = fields.Many2many('bm.product', 'official_welcome_kit_rel', 'official_id', string='Welcome Kit', compute='_compute_welcome_kit', store=True)

    # misc
    notes = fields.Text('Notas')
    color = fields.Integer('Color Index', default=0)
    # pin = fields.Char(string="PIN", copy=False, help="PIN used to Check In/Out in Kiosk Mode (if enabled in Configuration).")
    company_id = fields.Many2one('res.company', 'Nombre de la empresa', required=True, default=lambda self: self.env.company)
    company_code = fields.Integer("Codigo de Empresa", related='company_id.company_code', readonly=True)
    department_id = fields.Many2one('bm.department', 'Departamento de la empresa', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_id = fields.Many2one('bm.job', 'Cargo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char("Titulo del trabajo", compute="_compute_job_title", store=True, readonly=False)
    parent_id = fields.Many2one('bm.official', 'Gerente', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one('bm.official', 'Supervisor', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Seleccione el "funcionario" que es el supervisor de este funcionario.\n'
             'El "Supervisor" no tiene derechos o responsabilidades espec??ficos por defecto.')
    km_home_work = fields.Integer(string="Km Trabajo desde casa", tracking=True)

    # officials in company
    child_ids = fields.One2many('bm.official', 'parent_id', string='Direct subordinates')
    category_ids = fields.Many2many('bm.official.category', 'official_category_rel', 'official_id', 'category_id', string='Etiquetas')
    active = fields.Boolean("Active", default=True)
    unlinked = fields.Boolean("Desvinculado", default=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('check', 'En proceso de alta'),
        ('error', 'Revisar'),
        ('pending', 'Pendiente a Confirmar'),
        ('ready', 'Listo')],
        string="Estado", default='draft')
    reliable_base = fields.Boolean(
        string="Validaci??n", default=False, readonly=True)
    departured = fields.Many2one('bm.official.departure', 'Licencia', compute="_compute_departured")

    _sql_constraints = [
        ('identification_id_company_uniq', 'unique(identification_id,company_id)', 'Ya existe otro funcionario con la misma c??dula de identidad'),
        ('account_number_company_id_uniq', 'unique(account_number,company_id)', 'Ya existe otro funcionario con el mismo n??mero de cuenta'),
        ('mobile_phone_company_uniq', 'unique(mobile_phone,company_id)', 'Ya existe otro funcionario con el mismo n??mero de telefono celular'),
        ('email_company_uniq', 'unique(email,company_id)', 'Ya existe otro funcionario con el mismo E-Mail'),
        ('real_address_house_no_company_uniq', 'unique(real_address,house_no,company_id)', 'Ya existe otro funcionario con la misma direcci??n'),
    ]

    def write(self, vals):
        res = super(BM_Official, self).write(vals)
        # Primer horario: 8:30
        time_first = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        # Segundo horario: 16:00
        time_last = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
        # Si se realizaron cambios fuera de los horarios estipulados, se notifican
        #if datetime.now() < time_first or datetime.now() > time_last:
        #    self.notify_to_group('Centro Payroll', 'Cambios fuera de horario', 'Se realizaron cambios fuera de horario: {}'.format(vals))
        if self.segmentation_aproved and not self.cam_check:
            self.cam_check = True
        return res

    def show_message(self, title, message, *args):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'bm.official.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_message': message},
            'target': 'new'
        }

    def show_warning(self, title, message):
        return {
            'warning': {
                'title': title,
                'message': message,
            },
        }

    def notify_to_group(self, _channel, _subject, _message):
        channel_obj = self.env['mail.channel'].search([('name', 'ilike', _channel)])
        if channel_obj:
            self.env['mail.message'].create({
                'email_from': '"Sudameris BOT" <info@sudameris.com.py>', # Email
                'author_id': self.env['res.users'].search(['&', ('active', '=', False), ('id', '=', 1)]).id, # Odoo bot ID
                'model': 'mail.channel',
                'message_type': 'comment',
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'body': _message,
                'channel_ids': [(4, channel_obj.id)], # This is the channel where you want to send the message and all the users of this channel will receive message
                'res_id': channel_obj.id, # here add the channel you created.
            })

    @api.onchange('segmentation', 'welcome_kit')
    def _on_change_segmentation_welcome_kit(self):
        if (self.state in ['check']):
            products = {
                'origin': [],
                'new': []
            }
            for product in self._origin.welcome_kit:
                products['origin'].append(product.id)
            for product in self.welcome_kit:
                products['new'].append(product.id.origin)
            self._origin.segmentation_check = self.segmentation_check = (products['origin'] != products['new'] or self._origin.segmentation != self.segmentation)


    @api.onchange('identification_id')
    def _on_change_identification_id(self):
        if (self.identification_id):
            for official in self.env['bm.official'].search([('identification_id', '=', self.identification_id)]):
                self.identification_id = self._origin.identification_id
                return self.show_warning('N??mero de identificaci??n del funcionario', 'El funcionario {} ya posee este N??mero de Identificaci??n.'.format(official.name))

    @api.onchange('country')
    def _on_change_country(self):
        self.country_of_birth = self.country
        self.city = None

    @api.onchange('city')
    def _on_change_city(self):
        self.department = None

    @api.onchange('department')
    def _on_change_department(self):
        self.neighborhood = None

    @api.onchange('identification_expiry')
    def _on_change_identification_expiry(self):
        if self.identification_expiry:
            if date.today() > self.identification_expiry:
                self.identification_expiry = None
                return self.show_warning('Vencimiento de identificaci??n', 'El documento se encuentra vencido')

    @api.onchange('birthday')
    def _on_change_birthday(self):
        if self.birthday:
            if self.birthday < date(1900, 5, 10):
                self.birthday = None
                return self.show_warning('Fecha de nacimiento', 'La fecha de nacimiento debe ser may??r')

    @api.onchange('admission_date')
    def _on_change_admission_date(self):
        if self.admission_date:
            if self.admission_date < date(1900, 5, 10):
                self.admission_date = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso debe ser may??r')
            if self.admission_date > date.today():
                self.admission_date = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso no puede ser may??r al a??o vigente')

    @api.onchange('contract_end_date')
    def _on_change_contract_end_date(self):
        if self.contract_end_date:
            if self.contract_end_date < date(1900, 5, 10):
                self.contract_end_date = None
                return self.show_warning('Fecha de fin de contrato', 'La fecha fin de contrato debe ser may??r')

    def button_aprove(self):
        for official in self:
            if official.reliable_base:
                #if official.account_status == 'NORMAL':
                official.state = 'ready'
                official.reject_reason = None
                #else:
                #    official.state = 'pending'
            else:
                official.state = 'pending'
                return self.show_warning('Aprobar', 'Todav??a no se verific??')

    def button_refer(self):
        func_result = {
            'not_identification_id': [],
            'gross_salary_error': [],
            'has_account': [],
            'message': '',
            'count_ok': 0
        }
        # get officials selected
        officials = self.env['bm.official'].browse(self._context.get('active_ids')) or self
        # loop officials
        for official in officials:
            # if official has account, validate next one
            if official.reliable_base:
                if official.account_name or official.account_number:
                    func_result['has_account'].append('{}'.format(official.name))
            # if official is already checked or ready
            if official.state in ['check', 'ready']:
                continue
            # if official has not idenfitication_image or idenfitication_image_pdf, store error and go to next one
            if not ((official.idenfitication_image_front and official.idenfitication_image_back) or official.idenfitication_image_pdf):
                func_result['not_identification_id'].append('{}'.format(official.name))
                continue
            if not (official.gross_salary > 0):
                func_result['gross_salary_error'].append('{}'.format(official.name))
                continue
            # if its ok, change state
            if official.state in ['draft', 'error']:
                official.state = 'check'
                _validation = self.valid_client_reliable_base(official.id)
                func_result['count_ok'] += 1
        # if _ready_count > 1:
        if len(func_result['has_account']) > 0:
            func_result['message'] = '\nLos siguientes funcionarios ya poseen numero de cuenta:\n{}'.format('\n'.join(func_result['has_account']))
        if len(func_result['not_identification_id']) > 0:
            func_result['message'] = '\nLos siguientes funcionarios NO poseen "C??dula de identidad" correctamente cargada:\n{}'.format('\n'.join(func_result['not_identification_id']))
        if len(func_result['gross_salary_error']) > 0:
            func_result['message'] = '\nLos siguientes funcionarios NO poseen "Salario Bruto" asignado:\n{}'.format('\n'.join(func_result['gross_salary_error']))
        if func_result['count_ok'] > 0:
            # Notifica a los usuarios de Centro Payroll el cambio
            self.notify_to_group('Centro Payroll', 'Funcionarios a aprobar', 'Tiene {} nuevas solicitudes de Empresas para alta de cuentas.'.format(func_result['count_ok']))
        return self.show_message('Aprobar', 'Se remitieron {} funcionarios.\n{}'.format(func_result['count_ok'], func_result['message']))

    def button_refer_cam(self):
        for official in self:
            if official.state == 'check':
                if official.segmentation_check:
                    if not official.segmentation_aproved:
                        return self.show_message('Remitir al CAM', 'Se modific?? la recomendaci??n y se espera aprobaci??n')
                else:
                    official.segmentation_aproved = True
                    official.cam_check = True
            else:
                return self.show_message('Remitir al CAM', 'El funcionario no est?? en proceso de alta')

    def button_draft(self):
        for official in self:
            if official.state == 'check':
                official.state = 'draft'
                official.reliable_base = False

    def button_reset(self):
        for official in self:
            if official.state in ['check', 'error', 'pending', 'ready']:
                official.account_number = None
                official.account_name = None
                official.branch_number = None
                official.reliable_base = False
                official.cam_check = False
                official.segmentation_aproved = False
                official.segmentation_check = False
                official.unlinked = False
                official.state = 'draft'

    def button_unlink(self):
        for official in self:
            official.unlinked = True        
        return self.env.ref('hcs_bm_sudameris.bm_official_departure_report_xlsx').report_action(self)
        
    def create_officials_salary(self):
        func_result = {
            'has_payment': [],
            'message': '',
            'count_ok': 0
        }
        officials_salary = self.env['bm.official.salary'].sudo()
        officials = self.env['bm.official'].search([
                '&',
                '&', 
                ('id', 'in', self._context.get('active_ids')), 
                ('state', 'in', ['ready']),
                '&', 
                ('account_number', '!=', False),
                ('account_name', '!=', False),
                '&', 
                ('gross_salary', '>', 0),
                ('reliable_base', '=', True)
            ])
        # Obtengo los funcionarios seleccionados
        for official in officials:
            _create_official_salary = True
            # Get the last movement and check if in 35 range and is paid
            for official_salary in officials_salary.search([('official.id', '=', official.id)], order='id desc', limit=1):
                #if exist official salary for last 35 day
                diference_days = (datetime.now().date() - official_salary.payment_date).days
                if diference_days <= 35:
                    func_result['has_payment'].append('{}: {} dias'.format(official.name, diference_days))
                    _create_official_salary = False
            if _create_official_salary:
                officials_salary.create({
                    'official': official.id,
                })
                func_result['count_ok'] += 1
        if len(func_result['has_payment']) > 0:
            func_result['message'] = '\nLos siguientes funcionarios ya poseen registros validos:\n{}'.format('\n'.join(func_result['has_payment']))
        return self.show_message('Movimiento de salarios', 'Se crearon {} movimientos.\n{}'.format(func_result['count_ok'], func_result['message']))
