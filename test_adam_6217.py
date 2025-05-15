import adam6200

if __name__ == '__main__':
	adam1 = adam6200.ADAM6200('192.168.1.10')

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

	print(adam1.ranges)
