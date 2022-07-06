# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#create a new class for MultipleProductSale. 
class MultipleSolTravel(models.TransientModel):
    _name = "multiple.sol.travel"
 
    sol_ids = fields.Many2many('sale.order.line',string='Servicios')

    def add_multiple_sol_travel(self):
        # Id del Viaje
        v_travel_id = self._context.get('active_id')

        #Tramo del Viaje ordenado por id de manera ascendente y solo los tramos no cancelados
        travel_route_obj = self.env['tms.travel.route'].search([('travel_id', '=',v_travel_id), ('state', '!=','cancel')], order='id asc')

        #Ver si hay Tramo con la cual validar
        if not travel_route_obj:
            raise ValidationError(_('Debe ingresar al menos un Tramo de Viaje válido.'))

        #Ver si hay Servicios SOL seleccionados
        if not self.sol_ids:
            raise ValidationError(_('Debe ingresar al menos un Servicio a Planificar.'))

        v_conteo_ok = 0
        v_conte_bad = 0

        #Tabla de Servicios por Tramos del Viaje
        route_service_object = self.env['tms.travel.route.service']

        for line in self.sol_ids:          
            #Obtener el id SOL y id Origen / Destino
            v_sale_order_line_id = line.id
            v_sol_orig_dist = line.orig_district_id
            v_sol_dest_dist = line.dest_district_id
            #raise ValidationError(_("dato: '%s'.") % (v_sale_order_line_id))

            v_sube = False
            v_baja = False
            v_continua = False

            for routes in travel_route_obj:
                v_route_id = routes.id
                v_route_orig_dist = routes.orig_district_id
                v_route_dest_dist = routes.dest_district_id

                if v_sube == False:
                    if v_sol_orig_dist == v_route_orig_dist:
                        v_sube = True

                if v_sube == True and v_baja == False:
                    if v_sol_dest_dist == v_route_dest_dist:
                        v_baja = True

                if v_sube == True and v_baja == True and v_continua == False:
                    #Si subio y bajo en el mismo Tramo
                    #Graba y sale del for
                    service_line_dict ={
                                  'travel_route_id':v_route_id,
                                  'sale_order_line_id':v_sale_order_line_id,
                                  'b_start_trip':True,
                                  'b_continue_trip':False,
                                  'b_end_trip':True,
                                  }
                    #raise ValidationError(_("dato: '%s'.") % (service_line_dict))
                    route_service_object.create(service_line_dict)
                    #self._cr.execute('insert into tms_travel_route_service'
                    #                '(sale_order_line_id, travel_route_id, b_start_trip, b_continue_trip, b_end_trip) values (%s,%s,%s,%s,%s)',
                    #                 (v_sale_order_line_id, v_route_id,True,False,True))
                    break
                elif v_sube == True and v_baja == False and v_continua == False:
                    #Solo Sube
                    #Graba y activamos el continuar
                    service_line_dict ={
                                  'travel_route_id':v_route_id,
                                  'sale_order_line_id':v_sale_order_line_id,
                                  'b_start_trip':True,
                                  'b_continue_trip':False,
                                  'b_end_trip':False,
                                  }
                    route_service_object.create(service_line_dict)
                    #self._cr.execute('insert into tms_travel_route_service'
                    #                '(sale_order_line_id, travel_route_id, b_start_trip, b_continue_trip, b_end_trip) values (%s,%s,%s,%s,%s)',
                    #                 (v_sale_order_line_id, v_route_id,True,False,False))
                    v_continua = True
                elif v_sube == True and v_baja == False and v_continua == True:
                    #Solo Continua
                    #Graba y continua
                    service_line_dict ={
                                  'travel_route_id':v_route_id,
                                  'sale_order_line_id':v_sale_order_line_id,
                                  'b_start_trip':False,
                                  'b_continue_trip':True,
                                  'b_end_trip':False,
                                  }
                    route_service_object.create(service_line_dict)
                    #self._cr.execute('insert into tms_travel_route_service'
                    #                '(sale_order_line_id, travel_route_id, b_start_trip, b_continue_trip, b_end_trip) values (%s,%s,%s,%s,%s)',
                    #                 (v_sale_order_line_id, v_route_id,False,True,False))
                elif v_sube == True and v_baja == True and v_continua == True:
                    #Solo Baja
                    #Graba y sale del for
                    service_line_dict ={
                                  'travel_route_id':v_route_id,
                                  'sale_order_line_id':v_sale_order_line_id,
                                  'b_start_trip':False,
                                  'b_continue_trip':False,
                                  'b_end_trip':True,
                                  }
                    route_service_object.create(service_line_dict)
                    #self._cr.execute('insert into tms_travel_route_service'
                    #                '(sale_order_line_id, travel_route_id, b_start_trip, b_continue_trip, b_end_trip) values (%s,%s,%s,%s,%s)',
                    #                 (v_sale_order_line_id, v_route_id,False,False,True))
                    break

            #valida si al final tuvo una subida y bajada, se debe grabar
            if v_sube == True and v_baja == True:
                #Se inserta los ids de SOL con el id del Viaje
                self._cr.execute('insert into sale_order_line_travel_rel'
                                '(sale_order_line_id, travel_id) values (%s,%s)',
                                (v_sale_order_line_id, v_travel_id))
                #actualizar el campo asignado en SOL
                sol_obj = self.env['sale.order.line'].search([('id', '=',v_sale_order_line_id)])
                update_sol = {'check_assigned': True}
                sol_obj.write(update_sol)
                #query = """UPDATE 
                #           sale_order_line SET check_assigned = True"""
                #query += " WHERE id = %s " % (v_sale_order_line_id)
                #self.env.cr.execute(query)
                v_conteo_ok = v_conteo_ok + 1 
            else:
                #Se elimina los ids de SOL de los tramos
                rs_obj = route_service_object.search([('sale_order_line_id', '=',v_sale_order_line_id)])
                rs_obj.unlink()
                #query = """DELETE 
                #            FROM tms_travel_route_service"""
                #query += " where sale_order_line_id = %s " % (v_sale_order_line_id)
                #self.env.cr.execute(query)
                v_conte_bad = v_conte_bad + 1 

        #Ini Mensaje
        v_msg = ("Se culminó el proceso de Asignación de Servicios a Tramos del Viaje.\n"
                "Procesados OK: %s \n"
                "Procesados BAD: %s" % (v_conteo_ok, v_conte_bad))
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message']= v_msg
        return {
            'name': 'Planificando Servicio(s)',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views':[(view.id,'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
            }
        #Fin Mensaje
        return True
