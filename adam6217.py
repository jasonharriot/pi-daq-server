import requests
import xml.etree.ElementTree as ET
import base64

import adam

class ADAM6217(adam.ADAM):	#Inherits the generic ADAM class. Provides methods for analog voltage and current input. Output not yet implemented.
	def __init__(self, ipaddress):
		super().__init__(ipaddress)
		
		#print(f'An ADAM-6217 object has been created.')