# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo import exceptions 



class x_product(models.Model):
      _name = 'x.product'
      _sql_constraints = [('name', 'unique(name)','Produit existe déja'),]
      name = fields.Char(string="Nom Produit")
      reference=fields.Char()
      image = fields.Binary(string="Image")
      description = fields.Text()
      price =fields.Float(string="Prix") 
      qte = fields.Integer(string="Quantité")

      
    
class x_client(models.Model):
      _name = 'x.client'
      name = fields.Char(string="Nom Client")
      email_client = fields.Char()
      adresse_client = fields.Char()
      numerotel_client = fields.Char(size=13)


class x_fournisseur(models.Model):
      _name = 'x.fournisseur'
      name = fields.Char(string="Nom Fournisseur")
      email_fourni = fields.Char()
      adresse_fourni = fields.Char()
      numerotel_fourni = fields.Char(size=13)
      

class x_inventaire(models.Model):
      _name = 'x.inventaire'
      date = fields.Date(default=fields.Date.today,string="Date inventaire")
      id_inv = fields.One2many('x.produitinventaire','id_inv',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      state= fields.Selection(string="State",selection=[ ('draft', 'Brouillon'),('confirm', 'Confirmé'),], default="draft")

      @api.depends('id_inv.realqte')
      def changeqte(self):
        for line in self.id_inv:
          if line.realqte > 0 :
            self.state='confirm'
            self._cr.execute("UPDATE x_product SET qte=%s where id=%s",(line.realqte ,line.id_product.id))
          else :
            raise exceptions.Warning('Quantité négatif') 
           
        
      
class x_produitinventaire(models.Model):
      _name = 'x.produitinventaire'
      id_product = fields.Many2one('x.product',ondelete="cascade")
      id_inv = fields.Many2one('x.inventaire',ondelete="cascade")
      theoricalqte = fields.Integer(string="Quantité Théorique :",compute="_value_theoqte", store=True)
      realqte = fields.Integer(string="Quantité Réel :")

      @api.depends('id_product.qte')
      def _value_theoqte(self):
          for line in self:
             line.theoricalqte = line.id_product.qte
      
               


class x_charge(models.Model):
      _name = 'x.charge'
      name = fields.Char(string="Nom Charge")
      date = fields.Date(default=fields.Date.today,string="Date")
      description = fields.Text()
      prix= fields.Float()

# Cree commande avec un nom
class x_commande(models.Model):
      _name = 'x.commande'
      name = fields.Char( required=True, index=True, copy=False, default='New')
      date = fields.Date(default=fields.Date.today,string="Date Achat")
      id_fournisseur = fields.Many2one('x.fournisseur',string="Fournisseur :",required='true',ondelete="cascade",readonly=True,states={'draft': [('readonly', False)]})
      id_cmdqte = fields.One2many('x.cmdqte','id_cmd',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      totalcmd =  fields.Float(compute="_value_cmd", store=True)
      state= fields.Selection(string="State",selection=[ ('draft', 'Brouillon'),('confirm', 'Confirmé'),('return', 'Retourné'),], default="draft")
      
      @api.depends('id_cmdqte.qte')
      def achatfunc(self):
        test = 0
        for line in self.id_cmdqte :
          if line.qte > 0 and line.price_product > 0 :
            self.state='confirm'
            qteonchange = line.id_product.qte + line.qte
            self._cr.execute("UPDATE x_product SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
          else:
            test = 1
        if test == 0 :
          self.state='confirm'
        else :
          raise exceptions.Warning('Le prix et la quantité doivent être supérieur a 0')
      
      @api.depends('id_cmdqte.total')
      def _value_cmd(self):
          for order in self:
            for line in order.id_cmdqte:
                self.totalcmd += line.total

      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('achat.seq') or '/'
        return super(x_commande, self).create(vals)

      @api.depends('id_cmdqte.qte','totalcmd')
      def achatrefund(self):
            test = 0
            for line in self.id_cmdqte :
              if line.qte > line.id_product.qte:
                test = 1
                raise exceptions.Warning('Stock épuisé') 
            
            if test == 0 :
              self.state='return'
              for line in self.id_cmdqte :
                qteonchange = line.id_product.qte - line.qte
                self._cr.execute("UPDATE x_product SET qte=%s where id=%s",(qteonchange  ,line.id_product.id))
            self._cr.execute("UPDATE x_commande SET totalcmd=%s where id=%s",(0 ,self.id))
            self._cr.execute("UPDATE x_cmdqte SET total=%s where id_cmd=%s",(0 ,self.id))
      
      @api.multi
      def print(self):
                return self.env.ref('purchase.report_purchase_quotation').report_action(self)
  

class x_cmdqte(models.Model):
      _name = 'x.cmdqte'
      id_product = fields.Many2one('x.product',ondelete="cascade")
      id_cmd = fields.Many2one('x.commande',ondelete="cascade")
      id_vente = fields.Many2one('x.vente',ondelete="cascade")
      qte = fields.Integer('Quantité')
      price_product = fields.Float('Prix Unitaire')
      total = fields.Float(string='Sous Total',compute="_value_pc", store=True)
     
      @api.depends('price_product','qte')
      def _value_pc(self):
          for line in self:
             line.total = float(line.qte) *  line.price_product 
     
     
class x_vente(models.Model):

      _name = 'x.vente'
      name = fields.Char( required=True, index=True, copy=False,string="Nom Vente")
      date = fields.Date(default=fields.Date.today,string="Date Vente")
      id_client = fields.Many2one('x.client',string="client :",required='true',ondelete="cascade",readonly=True,states={'draft': [('readonly', False)]})
      id_cmdqte = fields.One2many('x.cmdqte','id_vente',string="Produits :",required='true',states={'confirm': [('readonly', True)]})
      totalcmd =  fields.Float(compute="_value_cmd", store=True)
      state= fields.Selection(string="State",selection=[ ('draft', 'Brouillon'),('confirm', 'Confirmé'),('return', 'Retuourné')], default="draft")

      @api.depends('id_cmdqte.qte')
      def ventefunc(self):
        test = 0
        for line in self.id_cmdqte :
          if line.qte > line.id_product.qte:
            test = 1
            raise exceptions.Warning('Stock épuisé')  
          elif line.qte > 0 and line.price_product > 0:
            self.state='confirm'
            qteonchange = line.id_product.qte - line.qte
            self._cr.execute("UPDATE x_product SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
          else:
            test = 1
        if test == 0 :
          self.state='confirm'
        else :
          raise exceptions.Warning('Le prix et la quantité doivent être supérieur a 0')

      @api.depends('id_cmdqte.qte','totalcmd')
      def venterefund(self):
            self.state='return'
            for line in self.id_cmdqte :
                qteonchange = line.id_product.qte + line.qte
                self._cr.execute("UPDATE x_product SET qte=%s where id=%s",(qteonchange ,line.id_product.id))
            self._cr.execute("UPDATE x_vente SET totalcmd=%s where id=%s",(0 ,self.id))
            self._cr.execute("UPDATE x_cmdqte SET total=%s where id_vente=%s",(0 ,self.id))
      
      @api.depends('id_cmdqte.total')
      def _value_cmd(self):
          for order in self:
            for line in order.id_cmdqte:
                self.totalcmd += line.total
      @api.model
      def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vente.seq') or '/'
        return super(x_vente, self).create(vals)
      


      
 
 #Reports

class x_reportsAchat(models.Model):
    _name = "x.reportsachat"
    _auto = False

    date = fields.Datetime()
    product_id = fields.Many2one('x.product', 'Product')
    fourni_id = fields.Many2one('x.fournisseur', 'Fournisseur')
    price_total = fields.Float()
    total_product = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW x_reportsachat 
        as SELECT min(c.id) as id , p.date as date , p.id_fournisseur 
        as fourni_id,p.totalcmd as price_total,c.id_product as product_id , c.total as total_product
        FROM x_cmdqte c join x_commande p on (c.id_cmd=p.id) 
        GROUP BY p.id_fournisseur, c.total,p.date,p.totalcmd,c.id_product """)


class x_reportsVente(models.Model):
    _name = "x.reportsvente"
    _auto = False

    date = fields.Datetime()
    product_id = fields.Many2one('x.product', 'Product')
    client_id = fields.Many2one('x.client', 'Client')
    price_total = fields.Float()
    total_product = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW x_reportsvente 
        as SELECT min(c.id) as id,p.date as date,p.id_client 
        as client_id,p.totalcmd as price_total,c.id_product as product_id ,c.total as total_product
        FROM x_cmdqte c join x_vente p on (c.id_vente=p.id) 
        GROUP BY p.id_client, c.total,p.date,p.totalcmd,c.id_product """)

class x_reportsCharge(models.Model):
    _name = "x.reportscharge"
    _auto = False

    date = fields.Datetime()
    prix = fields.Float()

    @api.model_cr
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW x_reportscharge 
        as SELECT min(id) as id,date,prix
        FROM x_charge
        GROUP BY date, prix """)


  