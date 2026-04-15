from odoo.tests import common

class TestContactFields(common.TransactionCase):
    def test_cnf_validation(self):
        partner = self.env['res.partner'].create({
            'name': 'Teste',
            'is_affiliated': True,
            'cnf_number': '123456789'
        })
        self.assertEqual(partner.cnf_number, '123456789')

        with self.assertRaises(Exception):
            partner.write({'cnf_number': '12345'})
