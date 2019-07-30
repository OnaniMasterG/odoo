# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mods(models.Model):
      _name = 'mods.mods'
      name = fields.Char()
      value = fields.Integer()
      value2 = fields.Float(compute="_value_pc", store=True)
      description = fields.Text()
 
      @api.depends('value')
      def _value_pc(self):
          self.value2 = float(self.value) / 100
      
      
    
class productss(models.Model):
      _name = 'productss.productss'
      name = fields.Char()
      description = fields.Text()
      price =fields.Float() 
 

class clientt(models.Model):
      _name = 'clientt.clientt'
      name_client = fields.Char()
      email_client = fields.Char()
      adresse_client = fields.Char()
      numerotel_client = fields.Char(size=13)


class fournisseurr(models.Model):
      _name = 'fournisseurr.fournisseurr'
      name_fourni = fields.Char()
      email_fourni = fields.Char()
      adresse_fourni = fields.Char()
      numerotel_fourni = fields.Char(size=13)
      

class inventairee(models.Model):
      _name = 'inventairee.inventairee'
      id_product = fields.Many2one(comodel_name='productss.productss')
      qte = fields.Integer()
      _sql_constraints = [('id_product', 'unique(id_product)',
                     'Produit existe déja'),]

class chargee(models.Model):
      _name = 'chargee.chargee'
      nom = fields.Char()
      description = fields.Text()
      prix= fields.Float()

# Cree commande avec un nom
class commandee(models.Model):
      _name = 'commandee.commandee'
      name = fields.Char( required=True, index=True, copy=False, default='New')
      id_fournisseur = fields.Many2one('fournisseurr.fournisseurr',string="Fournisseur :",required='true')
      id_cmdqte = fields.One2many('cmdqte.cmdqte','id_cmd',string="Produits :",required='true')
 

      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
        return super(commandee, self).create(vals)
  

class cmdqte(models.Model):
      _name = 'cmdqte.cmdqte'
      id_product = fields.Many2one('productss.productss')
      id_cmd = fields.Many2one('commandee.commandee')
      qte = fields.Integer()
      price_product = fields.Float()
      total = fields.Float(compute="_value_pc", store=True)

      
      @api.depends('price_product','qte')
      def _value_pc(self):
          for line in self:
             line.total = float(line.qte) *  line.price_product 
     

      


      
