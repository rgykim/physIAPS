#!/usr/bin/env python

### Physiological IAPS Log File Parsing Script
### Creator: Robert Kim
### Last Modifier: Robert Kim
### Version Date: 26 Jan 2017
### Python 2.7 

### Assumptions: 	Physiological IAPS log file output format is constant

import csv
import os
import re
import sys
import time

### opens sys.stdout in unbuffered mode
### print (sys.stdout.write()) operation is automatically flushed after each instance
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

### set home directory
home_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(home_dir)

def main():
	print "Script file directory: %s" % home_dir
	log_list = []

	for root, dirs, files in os.walk(home_dir):
	    for f in files:
	        if f.endswith('.log'):
	             log_list.append(os.path.join(root, f))

	if not log_list:
		sys.exit(	"EXITING OPERATION\n" + 
					"No log files were found in working directory.\n" + 
					"Please place the script file into the proper directory and try again."	)

	print "\nPsychoPy log files found in working directory:\n"

	for x in list(enumerate(log_list)):
		print "    ", 
		print (x[0], "/".join(x[1].strip("/").split('/')[1:]))
	print ""

	log_input = raw_input("Please enter the desired log file index (or multiple indices separated by spaces): ")

	if not log_input:
		sys.exit(	"EXITING OPERATION\n" + 
					"No log files were properly selected"	)

	log_index = log_input.split()
	log_index = [int(a) for a in log_index]

	if not all(n in range(len(log_list)) for n in log_index):
		sys.exit(	"EXITING OPERATION\n" +
					"INVALID ENTRY OF FILE INDICES"	)

	input_list = [log_list[n] for n in log_index]
	run_analysis(input_list)

	print "\nOPERATION COMPLETED " + time.strftime("%d %b %Y %H:%M:%S", time.localtime())

def analysis(in_file):
	with open(in_file, 'rb') as logfile:
		reader = csv.DictReader(logfile, delimiter = '\t', fieldnames = ('time', 'type', 'desc'))
		logs = list(reader)

	# for row in logs:
	# 	print sorted(row.values())

	t0 = 0.0
	for i, row in enumerate(logs):
		if "Keypress: space" in row['desc']:
			t0 = float(row['time'])
			break

	header = ['image', 'time', 'sequence']
	output = []
	check1, check2 = False, False

	for row in logs[i+1: ]:
		if "IAPS: image" in row['desc']:
			image = re.findall(r"'(.*?)'", row['desc'])[0]
			output = output + [[image]] + [[image]]
			check1 = True
			continue

		if "IAPS: autoDraw = True" in row['desc'] and check1:
			t_on = float(row['time']) - t0
			output[-2] = output[-2] + [t_on, "ON"]
			check2 = True
			continue

		if "IAPS: autoDraw = False" in row['desc'] and check1 and check2:
			t_off = float(row['time']) - t0
			output[-1] = output[-1] + [t_off, "OFF"]
			check1, check2 = False, False

	for row in output:
		print "\t%s: %s at %.4f" % (row[0], row[2], row[1])

	basename = os.path.basename(in_file)
	n = basename.index('.log')
	out_dir = "physIAPS_parsed_logs"
	out_file = os.path.join(out_dir, basename[ :n] + "_parsed.csv")

	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	with open(out_file, 'wb') as out_csv:
		writer = csv.writer(out_csv, delimiter = ',', quotechar = '"')
		writer.writerow(header)
		writer.writerows(output)

def run_analysis(arr):
	error_files = []
	for x in arr:
		try:
			print "\n::::: PARSING %s :::::" % x
			analysis(x)
		except KeyError: 
			print ">> ERROR READING " + x
			print ">> CHECK FILE CONSTRUCTION"
			error_files.append(x)

	if error_files:
		print "\n>> TOTAL OF %d INVALID FILES" % len(error_files)
		print ">> LIST OF FILES THAT THREW EXCEPTION:\n>>",
		print '\n>>'.join(error_files)

if __name__ == '__main__':
	main()