# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo import exceptions 



class productss(models.Model):
      _name = 'productss.productss'
      _sql_constraints = [('id_product', 'unique(id_product)','Produit existe déja'),]
      name = fields.Char()
      image = fields.Binary(string="Image")
      description = fields.Text()
      price =fields.Float() 
      qte = fields.Integer()

      
    
class clientt(models.Model):
      _name = 'clientt.clientt'
      name = fields.Char(string="Nom Client")
      email_client = fields.Char()
      adresse_client = fields.Char()
      numerotel_client = fields.Char(size=13)


class fournisseurr(models.Model):
      _name = 'fournisseurr.fournisseurr'
      name = fields.Char(string="Name Fournisseur")
      email_fourni = fields.Char()
      adresse_fourni = fields.Char()
      numerotel_fourni = fields.Char(size=13)
      

class inventairee(models.Model):
      _name = 'inventairee.inventairee'
      date = fields.Date(default=fields.Date.today,string="Date inventaire")
      id_inv = fields.One2many('pdtinventory.pdtinventory','id_inv',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      state= fields.Selection(string="State",selection=[ ('draft', 'Draft'),('confirm', 'Confirm'),], default="draft")

      @api.depends('id_inv.realqte')
      def changeqte(self):
        for line in self.id_inv:
          if line.realqte > 0 :
            self.state='confirm'
            self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(line.realqte ,line.id_product.id))
          else :
            raise exceptions.Warning('Quantité négatif') 
            """ self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(0 ,line.id_product.id)) """
          
      
      
class pdtinventory(models.Model):
      _name = 'pdtinventory.pdtinventory'
      id_product = fields.Many2one('productss.productss',ondelete="cascade")
      id_inv = fields.Many2one('inventairee.inventairee',ondelete="cascade")
      theoricalqte = fields.Integer(string="Quantité Théorique :",compute="_value_theoqte", store=True)
      realqte = fields.Integer(string="Quantité Réel :")

      @api.depends('id_product.qte')
      def _value_theoqte(self):
          for line in self:
             line.theoricalqte = line.id_product.qte
      
               


class chargee(models.Model):
      _name = 'chargee.chargee'
      name = fields.Char()
      date = fields.Date(default=fields.Date.today,string="Date")
      description = fields.Text()
      prix= fields.Float()

# Cree commande avec un nom
class commandee(models.Model):
      _name = 'commandee.commandee'
      name = fields.Char( required=True, index=True, copy=False, default='New')
      date = fields.Date(default=fields.Date.today,string="Date Achat")
      id_fournisseur = fields.Many2one('fournisseurr.fournisseurr',string="Fournisseur :",required='true',ondelete="cascade",readonly=True,states={'draft': [('readonly', False)]})
      id_cmdqte = fields.One2many('cmdqte.cmdqte','id_cmd',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      totalcmd =  fields.Float(compute="_value_cmd", store=True)
      state= fields.Selection(string="State",selection=[ ('draft', 'Draft'),('confirm', 'Confirm'),('return', 'Return'),], default="draft")
      
      @api.depends('id_cmdqte.qte')
      def achatfunc(self):
        test = 0
        for line in self.id_cmdqte :
          if line.qte > 0 and line.price_product > 0 :
            self.state='confirm'
            qteonchange = line.id_product.qte + line.qte
            self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
          else:
            test = 1
        if test == 0 :
          self.state='confirm'
        else :
          raise exceptions.Warning('Price and Quantity must be greater than 0')
      
      @api.depends('id_cmdqte.total')
      def _value_cmd(self):
          for order in self:
            for line in order.id_cmdqte:
                self.totalcmd += line.total

      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('achat.seq') or '/'
        return super(commandee, self).create(vals)

      @api.depends('id_cmdqte.qte','totalcmd')
      def achatrefund(self):
            test = 0
            for line in self.id_cmdqte :
              if line.qte > line.id_product.qte:
                test = 1
                raise exceptions.Warning('Out of stock') 
            
            if test == 0 :
              self.state='return'
              for line in self.id_cmdqte :
                qteonchange = line.id_product.qte - line.qte
                self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(qteonchange  ,line.id_product.id))
            self._cr.execute("UPDATE commandee_commandee SET totalcmd=%s where id=%s",(0 ,self.id))
            self._cr.execute("UPDATE cmdqte_cmdqte SET total=%s where id_cmd=%s",(0 ,self.id))
      
      @api.multi
      def print(self):
                return self.env.ref('purchase.report_purchase_quotation').report_action(self)
  

class cmdqte(models.Model):
      _name = 'cmdqte.cmdqte'
      id_product = fields.Many2one('productss.productss',ondelete="cascade")
      id_cmd = fields.Many2one('commandee.commandee',ondelete="cascade")
      id_vente = fields.Many2one('ventee.ventee',ondelete="cascade")
      qte = fields.Integer('Quantité')
      price_product = fields.Float('Price')
      total = fields.Float(compute="_value_pc", store=True)
     
      @api.depends('price_product','qte')
      def _value_pc(self):
          for line in self:
             line.total = float(line.qte) *  line.price_product 
     
     
class ventee(models.Model):

      _name = 'ventee.ventee'
      name = fields.Char( required=True, index=True, copy=False)
      date = fields.Date(default=fields.Date.today,string="Date Vente")
      id_client = fields.Many2one('clientt.clientt',string="client :",required='true',ondelete="cascade",readonly=True,states={'draft': [('readonly', False)]})
      id_cmdqte = fields.One2many('cmdqte.cmdqte','id_vente',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      totalcmd =  fields.Float(compute="_value_cmd", store=True)
      state= fields.Selection(string="State",selection=[ ('draft', 'Draft'),('confirm', 'Confirm'),('return', 'Return')], default="draft")

      @api.depends('id_cmdqte.qte')
      def ventefunc(self):
        test = 0
        for line in self.id_cmdqte :
          if line.qte > line.id_product.qte:
            test = 1
            raise exceptions.Warning('Out of stock')  
          elif line.qte > 0 and line.price_product > 0:
            self.state='confirm'
            qteonchange = line.id_product.qte - line.qte
            self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
          else:
            test = 1
        if test == 0 :
          self.state='confirm'
        else :
          raise exceptions.Warning('Price and Quantity must be greater than 0')

      @api.depends('id_cmdqte.qte','totalcmd')
      def venterefund(self):
            self.state='return'
            for line in self.id_cmdqte :
                qteonchange = line.id_product.qte + line.qte
                self._cr.execute("UPDATE productss_productss SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
            self._cr.execute("UPDATE ventee_ventee SET totalcmd=%s where id=%s",(0 ,self.id))
            self._cr.execute("UPDATE cmdqte_cmdqte SET total=%s where id_vente=%s",(0 ,self.id))
      
      @api.depends('id_cmdqte.total')
      def _value_cmd(self):
          for order in self:
            for line in order.id_cmdqte:
                self.totalcmd += line.total
      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vente.seq') or '/'
        return super(ventee, self).create(vals)
      


      
 
 #Reports

class reportsAchat(models.Model):
    _name = "reportsachat.reportsachat"
    _auto = False

    date = fields.Datetime()
    product_id = fields.Many2one('productss.productss', 'Product')
    fourni_id = fields.Many2one('fournisseurr.fournisseurr', 'Fournisseur')
    price_total = fields.Float()
    total_product = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW reportsachat_reportsachat 
        as SELECT min(c.id) as id , p.date as date , p.id_fournisseur 
        as fourni_id,p.totalcmd as price_total,c.id_product as product_id , c.total as total_product
        FROM cmdqte_cmdqte c join commandee_commandee p on (c.id_cmd=p.id) 
        GROUP BY p.id_fournisseur, c.total,p.date,p.totalcmd,c.id_product """)


class reportsVente(models.Model):
    _name = "reportsvente.reportsvente"
    _auto = False

    date = fields.Datetime()
    product_id = fields.Many2one('productss.productss', 'Product')
    client_id = fields.Many2one('clientt.clientt', 'Client')
    price_total = fields.Float()
    total_product = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW reportsvente_reportsvente 
        as SELECT min(c.id) as id,p.date as date,p.id_client 
        as client_id,p.totalcmd as price_total,c.id_product as product_id ,c.total as total_product
        FROM cmdqte_cmdqte c join ventee_ventee p on (c.id_vente=p.id) 
        GROUP BY p.id_client, c.total,p.date,p.totalcmd,c.id_product """)

class reportsCharge(models.Model):
    _name = "reportscharge.reportscharge"
    _auto = False

    date = fields.Datetime()
    prix = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW reportscharge_reportscharge 
        as SELECT min(id) as id,date,prix
        FROM chargee_chargee
        GROUP BY date, prix """)


  