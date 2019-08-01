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
      _sql_constraints = [('id_product', 'unique(id_product)','Produit existe déja'),]
      name = fields.Char()
      description = fields.Text()
      price =fields.Float() 
      qte = fields.Integer()

      
    
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
      name = fields.Char()
      id_inv = fields.One2many('pdtinventory.pdtinventory','id_inv',string="Produits :",required='true')

   
      
      
class pdtinventory(models.Model):
      _name = 'pdtinventory.pdtinventory'
      id_product = fields.Many2one('productss.productss',ondelete="cascade")
      id_inv = fields.Many2one('inventairee.inventairee',ondelete="cascade")
      theoricalqte = fields.Integer(string="Quantité Théorique :",compute="_value_theoqte", store=True)
      realqte = fields.Integer(string="Quantité Réel :")

      @api.depends('id_product.qte')
      def _value_theoqte(self):
          for line in self:
             line.theoricalqte = self.id_product.qte
               


class chargee(models.Model):
      _name = 'chargee.chargee'
      nom = fields.Char()
      description = fields.Text()
      prix= fields.Float()

# Cree commande avec un nom
class commandee(models.Model):
      _name = 'commandee.commandee'
      name = fields.Char( required=True, index=True, copy=False, default='New')
      id_fournisseur = fields.Many2one('fournisseurr.fournisseurr',string="Fournisseur :",required='true',ondelete="cascade")
      id_cmdqte = fields.One2many('cmdqte.cmdqte','id_cmd',string="Produits :",required='true')
      totalcmd =  fields.Float(compute="_value_cmd", store=True)
      
      @api.depends('id_cmdqte.total')
      def _value_cmd(self):
          for order in self:
            for line in order.id_cmdqte:
                self.totalcmd += line.total

      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
        return super(commandee, self).create(vals)
  

class cmdqte(models.Model):
      _name = 'cmdqte.cmdqte'
      id_product = fields.Many2one('productss.productss',ondelete="cascade")
      id_cmd = fields.Many2one('commandee.commandee',ondelete="cascade")
      qte = fields.Integer()
      price_product = fields.Float()
      total = fields.Float(compute="_value_pc", store=True)

      
      @api.depends('price_product','qte')
      def _value_pc(self):
          for line in self:
             line.total = float(line.qte) *  line.price_product 
     

      


      
