import requests
import xml.etree.ElementTree as ET
import base64

class ADAM6200:    #Provides a generic class for accessing an ADAM-6200 series module over the network. Only ADAM-6217 implements this class so far. Others not yet implemented.
    def __init__(self, ip_address, username='root', password='00000000'):
        self.ip_address = ip_address
        self.username = username
        self.password = password

        self.url = f'http://{self.ip_address}'

        self.analog_input_url = f'http://{self.ip_address}/analoginput/all/value'

        self.analog_input_range_url = f'http://{self.ip_address}/analoginput/all/range'

        self.user_agent = r'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

        self.authstring = base64.b64encode(f'{self.username}:{self.password}'.encode('ascii')).decode('utf-8')

        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.authstring}'}

        self.ranges = {}

        self.test_get()    #Updates ranges for first time.

        #print(f'A generic ADAM object has been created. Ta-da!')

    def test_get(self):    #Will print some status code information.
        print(f'Testing connection to ADAM @ {self.ip_address}.')

        general_error=False

        for url in [self.url, self.analog_input_url, self.analog_input_range_url]:
            try:
                x = requests.get(url, headers=self.headers)

                if not x.status_code == 200:
                    print(f'Error: {url} -> response code: {x.status_code}.')
                    general_error=True

                

            except:
                raise Exception(f'Exception occured while querying {self.ip_address}.')

        if general_error:
            raise Exception(f'Got a non-200 response code from at least one URL.')


        try:
            self.update_ranges()

        except:
            raise Exception(f'Failed to update ranges.')

        try:
            self.get_values()

        except:
            raise Exception(f'Failed to get values.')

        if not general_error:
            print(f'Self-test completed successfully.')

        return

        

        

    def update_ranges(self):
        x = requests.get(self.analog_input_range_url, headers = self.headers)

        #print(f'Received status code {x.status_code}')

        tree = ET.fromstring(x.content)
        
        for child in tree:
            id = int(child.find('ID').text)

            if id is None:
                continue

            #hexvalue = child.find('VALUE').text
            #value = int(hexvalue, 16)

            range_id = int(child.find('RANGE').text)

            range_name = child.find('NAME').text

            range_min = int(child.find('MIN').text)

            range_max = int(child.find('MAX').text)

            range_unit = child.find('UNIT').text
            
            self.ranges[id] = {
                'id': range_id,
                'name': range_name,
                'min': range_min,
                'max': range_max,
                'unit': range_unit
            }

    def get_raw_values(self):    #Get raw ADC values.
        x = requests.get(self.analog_input_url, headers = self.headers)

        #print(f'Received status code {x.status_code}')

        tree = ET.fromstring(x.content)
        
        raw_values = {}
        
        for child in tree:
            id = int(child.find('ID').text)
            hexvalue = child.find('VALUE').text

            value = int(hexvalue, 16)
            
            if not id is None and not value is None:
                raw_values[id] = value
            
        return raw_values

    def get_values(self):    #Get current or voltage values scaled to their appropriate units
        if self.ranges is None:
            raise Exception('No range data. Cannot convert values.')

        raw_values = self.get_raw_values()

        min_symbol = 0    #Min raw value ADC will produce.
        max_symbol = (pow(16, 4))-1    #Max raw value ADC will produce.

        values = {}

        for id, raw_value in raw_values.items():
            if not id in self.ranges:
                raise Exception(f'Missing range data for channel ID {id}. Raw value: {raw_value}.')

            r = self.ranges[id]

            value = (raw_value - min_symbol) * (r['max'] - r['min']) / (max_symbol - min_symbol) + r['min']

            values[id] = value

        return values
