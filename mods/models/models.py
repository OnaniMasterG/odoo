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


class stockk(models.Model):
      _name = 'stockk.stockk'
      name = fields.Char()
      description = fields.Text()
      
      
    
class productss(models.Model):
      _name = 'productss.productss'
      name = fields.Char()
      description = fields.Text()
      price = fields.Float()
      Nom_stock=fields.Many2one(comodel_name='stockk.stockk')
 

class clientt(models.Model):
      _name = 'clientt.clientt'
      name_client = fields.Char()
      email_client = fields.Char()
      adresse_client = fields.Text()
      numerotel_client = fields.Char(size=13)


class fournisseurr(models.Model):
      _name = 'fournisseurr.fournisseurr'
      name_fourni = fields.Char()
      email_fourni = fields.Text()
      adresse_fourni = fields.Float()
      numerotel_fourni = fields.Char(size=13)



      
