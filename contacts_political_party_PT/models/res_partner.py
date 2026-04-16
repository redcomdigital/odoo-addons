from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ------------------------------------------------------------
    # Dados Complementares
    # ------------------------------------------------------------
    is_affiliated = fields.Boolean(string='É filiado?', default=False)
    cnf_number = fields.Char(string='CNF', help='9 dígitos numéricos', size=9)
    social_name = fields.Char(string='Nome Social')
    political_name = fields.Char(string='Nome Político')
    birth_date = fields.Date(string='Data de Nascimento')
    gender_identity = fields.Selection([
        ('man', 'Homem'),
        ('non_binary', 'Não Binário'),
        ('trans_man', 'Homem Trans'),
        ('trans_woman', 'Mulher Trans'),
        ('travesti', 'Travesti'),
        ('woman', 'Mulher'),
    ], string='Identidade de Gênero')
    sexual_orientation = fields.Selection([
        ('bisexual', 'Bissexual'),
        ('gay', 'Gay'),
        ('heterosexual', 'Heterossexual'),
        ('lesbian', 'Lésbica'),
        ('not_declared', 'Não Declarado'),
        ('other', 'Outros'),
        ('pansexual', 'Pansexual'),
    ], string='Orientação Sexual')
    ethnicity = fields.Selection([
        ('black', 'Preto'),
        ('brown', 'Pardo'),
        ('indigenous', 'Indígena'),
        ('not_informed', 'Não Informado'),
        ('white', 'Branco'),
        ('yellow', 'Amarelo'),
    ], string='Etnia')
    religion = fields.Selection([
        ('buddhist', 'Budista'),
        ('catholic', 'Católica'),
        ('evangelical', 'Evangélica'),
        ('islamic', 'Islâmica'),
        ('jewish', 'Judaica'),
        ('no_religion', 'Sem Religião'),
        ('other', 'Outra'),
        ('spiritist', 'Espírita'),
        ('umbanda', 'Umbanda/Candomblé'),
    ], string='Religião')

    # ------------------------------------------------------------
    # Abonador
    # ------------------------------------------------------------
    abonador_id = fields.Many2one('res.partner', string='Abonador',
                                  domain=[('is_affiliated', '=', True)])
    abonador_cnf = fields.Char(related='abonador_id.cnf_number', string='CNF do Abonador', readonly=True)
    
    # Campo auxiliar para pesquisa de abonador por CNF
    abonador_search = fields.Char(string='Buscar Abonador (CNF ou Nome)', 
                                  compute='_compute_abonador_search',
                                  inverse='_inverse_abonador_search',
                                  search='_search_abonador')
    
    def _compute_abonador_search(self):
        """Computa o valor do campo de busca baseado no abonador selecionado."""
        for record in self:
            if record.abonador_id:
                record.abonador_search = f"{record.abonador_id.display_name} ({record.abonador_id.cnf_number})"
            else:
                record.abonador_search = False
    
    def _inverse_abonador_search(self):
        """Permite definir o abonador através do campo de busca."""
        for record in self:
            if record.abonador_search:
                # Tenta buscar por CNF primeiro (9 dígitos)
                search_value = record.abonador_search.strip()
                clean_cnf = re.sub(r'\D', '', search_value)
                
                partner_domain = [('is_affiliated', '=', True)]
                
                if len(clean_cnf) == 9:
                    # Busca por CNF
                    partner_domain.append(('cnf_number', '=', clean_cnf))
                else:
                    # Busca por nome
                    partner_domain.append(('name', 'ilike', search_value))
                
                partner = self.search(partner_domain, limit=1)
                if partner:
                    record.abonador_id = partner
            else:
                record.abonador_id = False
    
    def _search_abonador(self, operator, value):
        """Permite pesquisar parceiros pelo campo de busca do abonador."""
        # Esta função é usada para domínios de pesquisa
        return []

    # ------------------------------------------------------------
    # Dados Partidários
    # ------------------------------------------------------------
    affiliation_date = fields.Date(string='Data de Filiação')
    disaffiliation_date = fields.Date(string='Data de Desfiliação')
    sectorial_ids = fields.Many2many('sectorial.category', string='Setoriais de Atuação')

    # ------------------------------------------------------------
    # Dados Eleitorais
    # ------------------------------------------------------------
    voter_registration = fields.Char(string='Título Eleitoral', help='12 dígitos numéricos')
    electoral_zone = fields.Char(string='Zona')
    electoral_section = fields.Char(string='Seção')
    country_of_affiliation = fields.Many2one('res.country', string='País de Filiação')
    state_of_affiliation = fields.Many2one('res.country.state', string='Estado de Filiação',
                                           domain="[('country_id', '=', country_of_affiliation)]")
    city_of_affiliation = fields.Many2one('res.city', string='Município de Filiação',
                                          domain="[('state_id', '=', state_of_affiliation)]")

    # ------------------------------------------------------------
    # Restrições de base de dados (unicidade parcial do CNF)
    # ------------------------------------------------------------
    def init(self):
        """Cria um índice único parcial para CNF não vazio."""
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS res_partner_cnf_number_unique
            ON res_partner (cnf_number)
            WHERE cnf_number IS NOT NULL AND cnf_number != '';
        """)

    # ------------------------------------------------------------
    # Validações Python
    # ------------------------------------------------------------
    @api.constrains('cnf_number')
    def _check_cnf_number(self):
        for record in self:
            if record.cnf_number:
                # Valida formato (9 dígitos)
                if not re.match(r'^\d{9}$', record.cnf_number):
                    raise ValidationError(_('O CNF deve conter exatamente 9 dígitos numéricos (0-9).'))
                # Valida unicidade (redundante em relação ao índice, mas dá mensagem amigável)
                existing = self.search([
                    ('cnf_number', '=', record.cnf_number),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(_('Já existe um contacto com o CNF %s. O CNF deve ser único.') % record.cnf_number)

    @api.constrains('voter_registration')
    def _check_voter_registration(self):
        for record in self:
            if record.voter_registration:
                if not re.match(r'^\d{12}$', record.voter_registration):
                    raise ValidationError(_('O Título Eleitoral deve conter exatamente 12 dígitos numéricos.'))

    @api.constrains('affiliation_date', 'disaffiliation_date')
    def _check_affiliation_dates(self):
        for record in self:
            if record.affiliation_date and record.disaffiliation_date:
                if record.disaffiliation_date < record.affiliation_date:
                    raise ValidationError(_('A data de desfiliação não pode ser anterior à data de filiação.'))

    def write(self, vals):
        # Obrigar data de desfiliação quando is_affiliated muda de True para False
        if 'is_affiliated' in vals:
            for record in self:
                old_value = record.is_affiliated
                new_value = vals['is_affiliated']
                if old_value and not new_value:
                    if 'disaffiliation_date' not in vals or not vals.get('disaffiliation_date'):
                        raise ValidationError(_('Ao desfiliar o contato, é obrigatório preencher a Data de Desfiliação.'))
        return super(ResPartner, self).write(vals)

    @api.onchange('cnf_number')
    def _onchange_cnf_number(self):
        """Completa automaticamente com zeros à esquerda para 9 dígitos."""
        if self.cnf_number:
            # Remove caracteres não numéricos
            clean_cnf = re.sub(r'\D', '', self.cnf_number)
            # Completa com zeros à esquerda para 9 dígitos
            if len(clean_cnf) <= 9:
                self.cnf_number = clean_cnf.zfill(9)

    # ------------------------------------------------------------
    # Pesquisa por CNF ou Nome
    # ------------------------------------------------------------
    def name_get(self):
        result = []
        for partner in self:
            if partner.cnf_number:
                name = f"{partner.cnf_number} - {partner.name}" if partner.cnf_number else partner.name
            else:
                name = partner.name
            result.append((partner.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('cnf_number', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
