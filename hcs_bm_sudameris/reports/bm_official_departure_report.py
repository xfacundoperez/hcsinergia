from odoo import models


class BMOfficialDepartureReport(models.AbstractModel):
    _name = 'report.hcs_bm_sudameris.bm_official_departure_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Desvinculados')
        # Fila 0
        sheet.write(0, 0, 'Desvinculación Asalariados', workbook.add_format({
            'font_size': 18,
            'bold': True,
            'italic': True,
            'font_color': '#969696'})) # Desvinculación Asalariados
        # Formato Rojo con letras blancas
        header_format = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'bg_color': "#ff0000",
            'font_color': '#ffffff'})        
        # Fila 1
        sheet.write(1, 0, 'Sucursal:', header_format)
        sheet.write(1, 1, '', header_format)
        sheet.write(1, 2, '', header_format)
        sheet.write(1, 3, '', header_format)
        sheet.write(1, 4, '', header_format)
        sheet.write(1, 5, '', header_format)
        sheet.write(1, 6, '', header_format)
        sheet.write(1, 7, '', header_format)
        sheet.write(1, 8, '', header_format)
        # Fila 2
        sheet.write(2, 0, 'Cuenta:', header_format)
        sheet.write(2, 1, '', header_format)
        sheet.write(2, 2, '', header_format)
        sheet.write(2, 3, '', header_format)
        sheet.write(2, 4, '', header_format)
        sheet.write(2, 5, '', header_format)
        sheet.write(2, 6, '', header_format)
        sheet.write(2, 7, '', header_format)
        sheet.write(2, 8, '', header_format)
        # Fila 3
        sheet.write(3, 0, 'COD SUC', header_format)
        sheet.write(3, 1, 'SUCURSAL', header_format)
        sheet.write(3, 2, 'CUENTA', header_format)
        sheet.write(3, 3, 'C.I. N°', header_format)
        sheet.write(3, 4, 'Motivo desvinculación', header_format)
        sheet.write(3, 5, 'Fecha Incorporación', header_format)
        sheet.write(3, 6, 'Fecha Desvinculación', header_format)
        sheet.write(3, 7, 'Monto total Liquidación', header_format)
        sheet.write(3, 8, 'Monto del Aguinaldo correspondiente, protegido en base al Decreto Nro 5651/2010', header_format)
        # Por cada desvinculado, agrego más filas
        line_format = workbook.add_format({
            'font_size': 14,
            'align': 'vcenter',
            'bold': True
            })
        _line = 4
        for obj in lines:
            sheet.write(_line, 0, obj.branch_number, line_format)
            sheet.write(_line, 1, '?', line_format)
            sheet.write(_line, 2, obj.account_number, line_format)
            sheet.write(_line, 3, obj.identification_id, line_format)
            sheet.write(_line, 4, obj.departured.departure_reason or '', line_format)
            sheet.write(_line, 5, obj.departured.departure_end or '', line_format)
            sheet.write(_line, 6, obj.departured.departure_start or '', line_format)
            sheet.write(_line, 7, obj.gross_salary, line_format)
            sheet.write(_line, 8, obj.gross_salary / 2, line_format)
            _line = _line + 1
