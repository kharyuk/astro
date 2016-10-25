import xlwt
import csv

style_string = "font: bold on"
style = xlwt.easyxf(style_string)

wb = xlwt.Workbook()
ws = wb.add_sheet(sheetname)
for k in len(cells):
	ws.write(0, k, cells[k], style=style)
with open(fnm, 'rb') as csvfile:
	fid = csv.reader(csvfile)
	for rowx, row in enumerate(fid):
		for colx, value in enumerate(row):
			ws.write(rowx+1, colx, value)
			
			
wb.save(result_filename)
