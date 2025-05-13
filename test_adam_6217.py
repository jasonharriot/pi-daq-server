import adam6217

if __name__ == '__main__':
	adam1 = adam6217.ADAM6217('192.168.2.153')

	try:
		values = adam1.get_values()
	except:
		print(f'Error fetching values. Check connection?')
		exit(-1)

	#values = {
	#	'0': (pow(16, 4)-1),
	#	'1': int((pow(16, 4)-1)/2),
	#	'2': 0
	#}

	print(values)

	voltages = adam1.convert_to_voltages(values)
	print(voltages)

	currents = adam1.convert_to_currents(values)
	print(currents)
