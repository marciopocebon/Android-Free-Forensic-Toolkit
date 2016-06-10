#!/usr/bin/env python

import apsw, getopt, os, io, sys, shutil, re, time, report.makehtml, pdb

def makereport(case, timeline):
	csslocation = os.path.join(case, "reports", "call-log", "report.css")
	reportlocation = os.path.join(case, "reports", "call-log", "report.html")
	reportname = "Call Log"
	reportfile = open(reportlocation, 'w')
	css = open(csslocation, 'w')
	makecss(css)
	css.close()
	report.makehtml.makehead(reportfile, reportname)
	report.makehtml.importnavbar(reportfile, case)
	report.makehtml.makemid(reportfile)
	maketable(reportfile, case)
	reportfile.close()
	if timeline == True:
		tlmake(case)

def maketable(report, case):
	reportdb = os.path.join(case, "extracted data", "call-log", "db", "contacts2.db")
	report_connection=apsw.Connection(reportdb)
	report_cursor1=report_connection.cursor()
	report_cursor2=report_connection.cursor()
	report_cursor3=report_connection.cursor()
	
	report.write("<table CELLPADDING=8 CELLSPACING=0 VALIGN=TOP>\n")
	report.write("</table>\n")
	report.write("<div class=\"ResultsTable\">\n")
	report.write("<table>\n")
	report.write("<tr class=\"title\"><td><b>Status</b></td><td><b>Name</b></td><td><b>Number</b></td><td><b>Date/Time</b></td><td><b>Duration</b></td></tr>\n")
	for row1 in report_cursor1.execute("SELECT _id FROM calls"):
		for entry in row1:						
			for row2 in report_cursor2.execute("SELECT type FROM calls where _id = " + str(entry)):
				for status in row2:
					if str(status) == '1':				
						typename = 'Incoming call'
						report.write("<TR class=\"incoming\">")
					elif str(status) == '2':
						typename = 'Outgoing call'
						report.write("<TR class=\"outgoing\">")
					elif str(status) == '3':
						typename = 'Missed call'
						report.write("<TR class=\"missed\">")
					else:
						typename = 'Unknown (' + str(status) + ')'
						report.write("<TR>")
					report.write("<TD>" + typename + "</TD>")
			for row2 in report_cursor2.execute("SELECT name FROM calls where _id = " + str(entry)):
				for name in row2:
					if str(name) == '' or str(name) == 'None':
						namestr = 'Unknown'
					else:
						namestr = str(name)
					report.write("<TD>" + namestr + "</TD>")
			for row2 in report_cursor2.execute("SELECT number FROM calls where _id = " + str(entry)):				
				for number in row2:
					if str(number) == '':
						num = 'Withheld Number'
					else:
						num = str(number)
					report.write("<TD>" + num + "</TD>")
			for row2 in report_cursor2.execute("SELECT datetime(date/1000,'unixepoch','localtime') as date FROM calls where _id = " + str(entry)):				
				for date in row2:
					report.write("<TD>" + str(date) + "</TD>")
			for row2 in report_cursor2.execute("SELECT duration FROM calls where _id = " + str(entry)):				
				for duration in row2:
					seconds = int(duration)
					minutes = seconds/60
					hours = minutes/60
					days = hours/24
					if typename == 'Missed call':
						statement = 'N/A'
					elif not days >= 1:
						if not hours >=1:
							if not minutes >=1:
								statement = str(seconds) + "s"
							else:
								minutesint = int(minutes)
								minutesfrac = minutes - minutesint
								
								seconds = minutesfrac * 60
								seconds = round(seconds)

								statement = str(minutesint) + 'm ' + str(seconds) +'s'
						else: 
							hoursint = int(hours)
							hoursfrac = hours-hoursint

							minutes	= hoursfrac * 60
							minutesint	= round(minutes)
							minutesfrac = minutes - minutesint
							
							seconds = minutesfrac * 60
							secondsint = round(seconds)
							

							statement = str(hoursint) + 'h ' + str(minutesint) + "m " + str(secondsint) + "s"
					else:
						daysint = int(days)
						daysfrac = days - daysint
						
						hours = daysfrac * 24
						hoursint = round(hours)
						hoursfrac = hours - hoursint

						minutes	= hoursfrac * 60
						minutesint	= round(minutes)
						minutesfrac = minutes - minutesint
							
						seconds = minutesfrac * 60
						secondsint = round(seconds)
							

						statement = str(daysint) + "d " + str(hoursint) + 'h ' + str(minutesint) + "m " + str(secondsint) + "s"

					report.write("<TD>" + statement + "</TD>")
				
			report.write("</TR>")
			
def tlmake(case):
	reportdb = os.path.join(case, "extracted data", "call-log", "db", "contacts2.db")
	report_connection=apsw.Connection(reportdb)
	report_cursor1=report_connection.cursor()
	report_cursor2=report_connection.cursor()
	report_cursor3=report_connection.cursor()

	tldb = os.path.join(case, "reports", "timeline.db")
	tl_connection=apsw.Connection(tldb)
	tloutput=io.StringIO()
	tl_cursor=tl_connection.cursor()
	
	for row1 in report_cursor1.execute("SELECT _id FROM calls"):
		for entry in row1:						
			for row2 in report_cursor2.execute("SELECT type FROM calls where _id = " + str(entry)):
				for status in row2:
					if str(status) == '1':				
						statusdesc = 'Recieved a call from '
					elif str(status) == '2':
						statusdesc = 'Made an outgoing call to '
					elif str(status) == '3':
						statusdesc = 'Missed a call from '
			for row2 in report_cursor2.execute("SELECT number FROM calls where _id = " + str(entry)):				
				for number in row2:
					if str(number) == '':
						numdesc = 'a withheld number'
					else:
						numdesc = str(number)
			for row2 in report_cursor2.execute("SELECT date FROM calls where _id = " + str(entry)):				
				for date in row2:
					tldate = date
			for row2 in report_cursor2.execute("SELECT duration FROM calls where _id = " + str(entry)):				
				for duration in row2:
					seconds = int(duration)
					minutes = seconds/60
					hours = minutes/60
					days = hours/24
					if str(status) == '3':
						statement = 'N/A'
					elif not days >= 1:
						if not hours >=1:
							if not minutes >=1:
								statement = str(seconds) + "s"
							else:
								minutesint = int(minutes)
								minutesfrac = minutes - minutesint
								
								seconds = minutesfrac * 60
								seconds = round(seconds)

								statement = str(minutesint) + 'm ' + str(seconds) +'s'
						else: 
							hoursint = int(hours)
							hoursfrac = hours-hoursint

							minutes	= hoursfrac * 60
							minutesint	= round(minutes)
							minutesfrac = minutes - minutesint
							
							seconds = minutesfrac * 60
							secondsint = round(seconds)
							

							statement = str(hoursint) + 'h ' + str(minutesint) + "m " + str(secondsint) + "s"
					else:
						daysint = int(days)
						daysfrac = days - daysint
						
						hours = daysfrac * 24
						hoursint = round(hours)
						hoursfrac = hours - hoursint

						minutes	= hoursfrac * 60
						minutesint	= round(minutes)
						minutesfrac = minutes - minutesint
							
						seconds = minutesfrac * 60
						secondsint = round(seconds)
							

						statement = str(daysint) + "d " + str(hoursint) + 'h ' + str(minutesint) + "m " + str(secondsint) + "s"

			if str(status) == '3':
				lengthdesc = ''
			else:
				lengthdesc = ' (' + statement + ')'
			message = statusdesc + numdesc + lengthdesc
			tldatestr = str(tldate)
			command = "INSERT INTO timeline VALUES(NULL, 'Call Log', '" + message + "', '" + tldatestr + "')"
			tl_cursor.execute(command)
				
			

def statementmin(minutes):
	minutesint = int(minutes)
	minutesfrac = minutes - minutesint
								
	seconds = minutesfrac * 60
	seconds = round(seconds)


def makecss(css):
	css.write(".ResultsTable {\n")
	css.write("margin:0px;padding:0px;\n")
	css.write("width:100%;\n")
	css.write("box-shadow: 10px 10px 5px #888888;\n")
	css.write("border:1px solid #000000;\n")
	css.write("\n")
	css.write("-moz-border-radius-bottomleft:5px;\n")
	css.write("-webkit-border-bottom-left-radius:5px;\n")
	css.write("border-bottom-left-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-bottomright:5px;\n")
	css.write("-webkit-border-bottom-right-radius:5px;\n")
	css.write("border-bottom-right-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-topright:5px;\n")
	css.write("-webkit-border-top-right-radius:5px;\n")
	css.write("border-top-right-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-topleft:5px;\n")
	css.write("-webkit-border-top-left-radius:5px;\n")
	css.write("border-top-left-radius:5px;\n")
	css.write("}.ResultsTable table{\n")
	css.write("border-collapse: collapse;\n")
	css.write("border-spacing: 0;\n")
	css.write("width:100%;\n")
	css.write("height:100%;\n")
	css.write("margin:0px;padding:0px;\n")
	css.write("}.ResultsTable tr:last-child td:last-child {\n")
	css.write("-moz-border-radius-bottomright:5px;\n")
	css.write("-webkit-border-bottom-right-radius:5px;\n")
	css.write("border-bottom-right-radius:5px;\n")
	css.write("}\n")
	css.write(".ResultsTable table tr:first-child td:first-child {\n")
	css.write("-moz-border-radius-topleft:5px;\n")
	css.write("-webkit-border-top-left-radius:5px;\n")
	css.write("border-top-left-radius:5px;\n")
	css.write("}\n")
	css.write(".ResultsTable table tr:first-child td:last-child {\n")
	css.write("-moz-border-radius-topright:5px;\n")
	css.write("-webkit-border-top-right-radius:5px;\n")
	css.write("border-top-right-radius:5px;\n")
	css.write("}.ResultsTable tr:last-child td:first-child{\n")
	css.write("-moz-border-radius-bottomleft:5px;\n")
	css.write("-webkit-border-bottom-left-radius:5px;\n")
	css.write("border-bottom-left-radius:5px;\n")
	css.write("}.ResultsTable tr:hover td{\n")
	css.write("\n")
	css.write("}\n")
	css.write(".ResultsTable tr.incoming{ background-color:#88FF88; }\n")
	css.write(".ResultsTable tr.outgoing { background-color:#8888FF; }\n")
	css.write(".ResultsTable tr.missed { background-color:#FF8888; }.ResultsTable td{\n")
	css.write("vertical-align:middle;\n")
	css.write("\n")
	css.write("\n")
	css.write("border:1px solid #000000;\n")
	css.write("border-width:0px 1px 1px 0px;\n")
	css.write("text-align:left;\n")
	css.write("padding:10px;\n")
	css.write("font-size:12px;\n")
	css.write("font-family:Arial;\n")
	css.write("font-weight:normal;\n")
	css.write("color:#000000;\n")
	css.write("}.ResultsTable tr:last-child td{\n")
	css.write("border-width:0px 1px 0px 0px;\n")
	css.write("}.ResultsTable tr td:last-child{\n")
	css.write("border-width:0px 0px 1px 0px;\n")
	css.write("}.ResultsTable tr:last-child td:last-child{\n")
	css.write("border-width:0px 0px 0px 0px;\n")
	css.write("}\n")
	css.write(".ResultsTable tr.title td{\n")
	css.write("background:-o-linear-gradient(bottom, #005fbf 5%, #003f7f 100%); background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #005fbf), color-stop(1, #003f7f) );\n")
	css.write("background:-moz-linear-gradient( center top, #005fbf 5%, #003f7f 100% );\n")
	css.write("filter:progid:DXImageTransform.Microsoft.gradient(startColorstr=\"#005fbf\", endColorstr=\"#003f7f\"); background: -o-linear-gradient(top,#005fbf,003f7f);\n")
	css.write("\n")
	css.write("background-color:#005fbf;\n")
	css.write("border:0px solid #000000;\n")
	css.write("text-align:center;\n")
	css.write("border-width:0px 0px 1px 1px;\n")
	css.write("font-size:14px;\n")
	css.write("font-family:Trebuchet MS;\n")
	css.write("font-weight:bold;\n")
	css.write("color:#ffffff;\n")
	css.write("}\n")
	css.write(".ResultsTable tr:first-child:hover td{\n")
	css.write("background:-o-linear-gradient(bottom, #005fbf 5%, #003f7f 100%); background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #005fbf), color-stop(1, #003f7f) );\n")
	css.write("background:-moz-linear-gradient( center top, #005fbf 5%, #003f7f 100% );\n")
	css.write("filter:progid:DXImageTransform.Microsoft.gradient(startColorstr=\"#005fbf\", endColorstr=\"#003f7f\"); background: -o-linear-gradient(top,#005fbf,003f7f);\n")
	css.write("\n")
	css.write("background-color:#005fbf;\n")
	css.write("}\n")
	css.write(".ResultsTable tr:first-child td:first-child{\n")
	css.write("border-width:0px 0px 1px 0px;\n")
	css.write("}\n")
	css.write(".ResultsTable tr:first-child td:last-child{\n")
	css.write("border-width:0px 0px 1px 1px;\n")
	css.write("}\n")
	css.write("\n")
	css.write(".SideBar {\n")
	css.write("margin:0px;padding:0px;\n")
	css.write("width:100%;\n")
	css.write("box-shadow: 10px 10px 5px #888888;\n")
	css.write("border:1px solid #000000;\n")
	css.write("\n")
	css.write("-moz-border-radius-bottomleft:5px;\n")
	css.write("-webkit-border-bottom-left-radius:5px;\n")
	css.write("border-bottom-left-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-bottomright:5px;\n")
	css.write("-webkit-border-bottom-right-radius:5px;\n")
	css.write("border-bottom-right-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-topright:5px;\n")
	css.write("-webkit-border-top-right-radius:5px;\n")
	css.write("border-top-right-radius:5px;\n")
	css.write("\n")
	css.write("-moz-border-radius-topleft:5px;\n")
	css.write("-webkit-border-top-left-radius:5px;\n")
	css.write("border-top-left-radius:5px;\n")
	css.write("}.SideBar table{\n")
	css.write("border-collapse: collapse;\n")
	css.write("border-spacing: 0;\n")
	css.write("width:100%;\n")
	css.write("height:100%;\n")
	css.write("margin:0px;padding:0px;\n")
	css.write("}.SideBar tr:last-child td:last-child {\n")
	css.write("-moz-border-radius-bottomright:5px;\n")
	css.write("-webkit-border-bottom-right-radius:5px;\n")
	css.write("border-bottom-right-radius:5px;\n")
	css.write("}\n")
	css.write(".SideBar table tr:first-child td:first-child {\n")
	css.write("-moz-border-radius-topleft:5px;\n")
	css.write("-webkit-border-top-left-radius:5px;\n")
	css.write("border-top-left-radius:5px;\n")
	css.write("}\n")
	css.write(".SideBar table tr:first-child td:last-child {\n")
	css.write("-moz-border-radius-topright:5px;\n")
	css.write("-webkit-border-top-right-radius:5px;\n")
	css.write("border-top-right-radius:5px;\n")
	css.write("}.SideBar tr:last-child td:first-child{\n")
	css.write("-moz-border-radius-bottomleft:5px;\n")
	css.write("-webkit-border-bottom-left-radius:5px;\n")
	css.write("border-bottom-left-radius:5px;\n")
	css.write("}.SideBar tr:hover td{\n")
	css.write("background-color:#ffffff;\n")
	css.write("\n")
	css.write("\n")
	css.write("}\n")
	css.write(".SideBar td{\n")
	css.write("vertical-align:middle;\n")
	css.write("\n")
	css.write("background-color:#c8ffff;\n")
	css.write("\n")
	css.write("border:1px solid #000000;\n")
	css.write("border-width:0px 1px 1px 0px;\n")
	css.write("text-align:left;\n")
	css.write("padding:9px;\n")
	css.write("font-size:12px;\n")
	css.write("font-family:Arial;\n")
	css.write("font-weight:normal;\n")
	css.write("color:#000000;\n")
	css.write("}.SideBar tr:last-child td{\n")
	css.write("border-width:0px 1px 0px 0px;\n")
	css.write("}.SideBar tr td:last-child{\n")
	css.write("border-width:0px 0px 1px 0px;\n")
	css.write("}.SideBar tr:last-child td:last-child{\n")
	css.write("border-width:0px 0px 0px 0px;\n")
	css.write("}\n")
	css.write(".SideBar tr:first-child td{\n")
	css.write("background:-o-linear-gradient(bottom, #5656ff 5%, #2b2b7f 100%); background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #5656ff), color-stop(1, #2b2b7f) );\n")
	css.write("background:-moz-linear-gradient( center top, #5656ff 5%, #2b2b7f 100% );\n")
	css.write("filter:progid:DXImageTransform.Microsoft.gradient(startColorstr=\"#5656ff\", endColorstr=\"#2b2b7f\"); background: -o-linear-gradient(top,#5656ff,2b2b7f);\n")
	css.write("\n")
	css.write("background-color:#5656ff;\n")
	css.write("border:0px solid #000000;\n")
	css.write("text-align:center;\n")
	css.write("border-width:0px 0px 1px 1px;\n")
	css.write("font-size:14px;\n")
	css.write("font-family:Arial;\n")
	css.write("font-weight:bold;\n")
	css.write("color:#ffffff;\n")
	css.write("}\n")
	css.write(".SideBar tr:first-child:hover td{\n")
	css.write("background:-o-linear-gradient(bottom, #5656ff 5%, #2b2b7f 100%); background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #5656ff), color-stop(1, #2b2b7f) );\n")
	css.write("background:-moz-linear-gradient( center top, #5656ff 5%, #2b2b7f 100% );\n")
	css.write("filter:progid:DXImageTransform.Microsoft.gradient(startColorstr=\"#5656ff\", endColorstr=\"#2b2b7f\"); background: -o-linear-gradient(top,#5656ff,2b2b7f);\n")
	css.write("\n")
	css.write("background-color:#5656ff;\n")
	css.write("}\n")
	css.write(".SideBar tr:first-child td:first-child{\n")
	css.write("border-width:0px 0px 1px 0px;\n")
	css.write("}\n")
	css.write(".SideBar tr:first-child td:last-child{\n")
	css.write("border-width:0px 0px 1px 1px;\n")
	css.write("}\n")
