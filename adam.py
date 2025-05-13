import requests
import xml.etree.ElementTree as ET
import base64

class ADAM:	#Provides a generic class for accessing an ADAM module over the network. Only ADAM-6217 implements this class so far. Others not yet implemented.
	def __init__(self, ipaddress, username='root', password='00000000'):
		self.ipaddress = ipaddress
		self.username = username
		self.password = password

		self.analog_input_url = f'http://{self.ipaddress}/analoginput/all/value'

		self.user_agent = r'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

		self.authstring = base64.b64encode(f'{self.username}:{self.password}'.encode('ascii')).decode('utf-8')

		self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
			'Authorization': f'Basic {self.authstring}'}

		#print(f'A generic ADAM object has been created. Ta-da!')

	def test_get(self):
		x = requests.get(self.analog_input_url, headers=self.headers)

		if not x.status_code == 200:
			print(f'Response code was not a 200 OK. You may need to set the password variable.')