import requests
import xml.etree.ElementTree as ET
import base64

import adam

class ADAM6217(adam.ADAM):	#Inherits the generic ADAM class. Provides methods for analog voltage and current input. Output not yet implemented.
	def __init__(self, ipaddress):
		super().__init__(ipaddress)

		self.adc_current_scale = 20	#Maximum scale of measured current. Must match configuration on the ADAM module.
		self.adc_voltage_scale = 150 #Maximum scale of measured voltage. Must match configuration on the ADAM module.

		#print(f'An ADAM-6217 object has been created.')

	def get_values(self):	#Get raw ADC values.
		x = requests.get(self.analog_input_url, headers = self.headers)

		print(f'Received status code {x.status_code}')

		tree = ET.fromstring(x.content)
		
		values = {}
		
		for child in tree:
			id = int(child.find('ID').text)
			hexvalue = child.find('VALUE').text

			value = int(hexvalue, 16)
			
			if not id is None and not value is None:
				values[id] = value
			
		return values

	def convert_to_voltage(self, value):	#Convert ADC value to a voltage
		maxSymbol = (pow(16, 4))-1
		voltage = self.adc_voltage_scale*(value - int(maxSymbol/2))/int(maxSymbol/2)
		return voltage

	def convert_to_current(self, value):	#Convert ADC value to a current
		maxSymbol = (pow(16, 4))-1
		current = self.adc_current_scale*(value - int(maxSymbol/2))/int(maxSymbol/2)
		return current

	def convert_to_voltages(self, values):	#Convert set of values to voltages
		voltages = {}

		for id, value in values.items():
			voltage = self.convert_to_voltage(value)
			if not id is None and not voltage is None:
				voltages[id] = voltage
			
		return voltages

	def convert_to_currents(self, values):	#Convert set of values to currents
		currents = {}

		for id, value in values.items():
			current = self.convert_to_current(value)
			if not id is None and not current is None:
				currents[id] = current

		return currents