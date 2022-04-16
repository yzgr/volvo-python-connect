import requests
import json
import logging
import os
import inspect

class NightGuard:

    __volvo_uri = None
    __token = None
    __vcc_key = None
    __operation_id = None
    __api_session = None
    __api_resp = None
    __waiting = False
    __vin = None
    __services = None

    def __init__(self, vin) -> None:
        """Python class to connect to the Volvo API available under https://developer.volvocars.com/

        Args:
            vin (str): VIN of your Volvo.  This class currently just supports one car

        """
        logging.basicConfig(format='[%(levelname)s %(asctime)s]:\t%(message)s', datefmt='%Y-%m-%d%Y %H:%M:%S', encoding='utf-8', level=logging.DEBUG)

        file = 'service_params.json'
        if os.path.exists(file):
            json_file = open(file)
            json_conf = json.load(json_file)
        else:
            exit()

        self.__token = 'Bearer ' + json_conf['TOKEN_CONNECTED']
        self.__vcc_key = json_conf['VCC_KEY_PRINARY']
        self.__volvo_uri = json_conf['URI']
        self.__services = json_conf['SERVICES']
        self.__api_session = requests.Session()
        self.__set_gobal_headers()

        if self.__validate_vin(vin.upper()):
            self.__vin = vin.upper()
        else:
            print('The given VIN ({}) does not match the APIs VIN, please check your VIN.'.format(vin))
            exit()


    def __validate_vin(self, vin):
        '''
        Check if the given VIN matches one of the VIN if the car list response
        '''
        resp = self.__get('/', self.get_service_data())
        for data in self.__api_resp['data']:
            logging.debug('VIN check: %s = %s', vin.upper(), data['vin'])
            return True if data['vin'] == vin.upper() else False


    def details(self):
        '''
        Provides details about the vehicle such as model, model-year etc.
        '''
        vehicle = self.__get('/{}'.format(self.__vin), self.get_service_data('details'))
        if vehicle:
            v_data = vehicle['data']
            print('Model:\t{} ({})'.format(v_data['descriptions']['model'], v_data['modelYear']))
            return vehicle
        else:
            logging.warn("No car info found")
            return False

    def __print_json(self, json_str, indent=False):
        for k, v in json_str.items():
            if type(v) is str:
                print("\t{}: {}".format(k, v))
            elif isinstance(v, dict):
                print("{}: ".format(k))
                self.__print_json(v)


    def environment(self, print=False):
        '''
        Environment Values such as external temperature collected by means of Vehicle sensors
        '''
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def brakes(self, print=False):
        """Vehicle\'s Latest Brake Status Values like brake fluid level

        Each service returns a value and a timestamp 
        "serviceStatus": {"brakeFluid": "[VERY_LOW|LOW NORMAL|HIGH|VERY_HIGH]", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}

        Returns:
            str: JSON

        Example:
            {"brakeFluid": {"value": "NORMAL", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def diagnostics(self, print=False):
        """Vehicle\'s Latest Diagnostic Values
        * serviceStatus [NORMAL, ALMOST_TIME_FOR_SERVICE, TIME_FOR_SERVICE, TIME_EXCEEDED]
        * serviceTrigger [CALENDAR_TIME, ECM, DISTANCE, ENGINE_HOURS]
        * engineHoursToService
        * kmToService
        * monthsToService
        * monthsToService

        Each service returns a value and a timestamp 
        "serviceStatus": {"value": "NORMAL", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}

        Returns:
            str: JSON

        Example:
            {"serviceStatus": {"value": "NORMAL", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "serviceTrigger": {"value": "CALENDAR_TIME", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "engineHoursToService": {"value": "616", "unit": "hours", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "kmToService": {"value": "28836", "unit": "kilometers", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "monthsToService": {"value": "10", "unit": "months", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "serviceType": {"value": "KEYOUT", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}, "washerFluidLevel": {"value": "NORMAL", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ"}}
            "YYYY-MM-DDTHH:MM:SS.SSSZ" }
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def doors(self, print=False):
        """Vehicle's Door and Lock Status Values
        * carLocked [LOCKED, UNLOCKED]
        * frontLeft [OPEN, CLOSED]
        * frontRight [OPEN, CLOSED]
        * rearLeft [OPEN, CLOSED]
        * rearRight [OPEN, CLOSED]
        * tailGate [OPEN, CLOSED]
        * hood [OPEN, CLOSED]

        Each door returns a value and a timestamp 
        'carLocked': {'value': '[LOCKED, UNLOCKED]|[OPEN, CLOSED]', 'timestamp': '2020-11-19T21:23:24.424Z'}

        Returns:
            str: JSON

        Example:
            {'carLocked': {'value': 'LOCKED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'frontLeft': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'frontRight': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'hood': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'rearLeft': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'rearRight': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'tailGate': {'value': 'CLOSED', 'timestamp': '2020-11-19T21:23:24.424Z'}}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def engine(self, print=False):
        """Vehicle's Latest Engine Diagnostic Values such as engine-coolant-level, oil level etc.
        
        * engineRunning [RUNNING, STOPPED]
        * oilPressure
        * engineCoolantLevel
        * oilLevel
        * engineCoolantTemp
        
        Each service returns a value and a timestamp 
        'engineRunning': {'value': '[RUNNING|STOPPED]', 'timestamp': '2020-11-19T21:23:24.424Z'


        ToDo:
            get missing values

        Returns:
            str: JSON

        Example:
            {'engineRunning': {'value': 'STOPPED', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'oilPressure': {'value': 'NORMAL', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'engineCoolantLevel': {'value': 'NORMAL', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'oilLevel': {'value': 'NORMAL', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'engineCoolantTemp': {'value': '66', 'unit': 'celsius', 'timestamp': '2020-11-19T21:23:24.424Z'}}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def fuel(self, print=False):
        """Vehicle\'s Latest Fuel Amount in Liters

        Returns:
            str: JSON

        Example:
            {"fuelAmount": {"value": "45", "unit": "liters", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ" }
        """
        return self.__make_info_call('fuel')
    
    def odometer(self, print=False):
        """Vehicle's latest odometer value in kilometers

        Returns:
            str: JSON

        Example:
            {"odometer": {"value": "1174", "unit": "kilometers", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ" }
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def statistics(self, print=False):
        """Vehicle's Latest Statistics such as average-speed, trip-meters
        * averageFuelConsumption [Always liters]
        * averageSpeed [Always kilometers_per_hour]
        * tripMeter1 [Always kilometers]
        * tripMeter2 [Always kilometers]

        Each diagnostic returns a value, unit and a timestamp 
        'averageFuelConsumption': {'value': '5.4', 'unit': 'liters_per_100_kilometers', 'timestamp': '2020-11-19T21:23:24.424Z'}

        Returns:
            str: JSON

        Example:
            {'averageFuelConsumption': {'value': '5.4', 'unit': 'liters_per_100_kilometers', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'averageSpeed': {'value': '35', 'unit': 'kilometers_per_hour', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'tripMeter1': {'value': '1174', 'unit': 'kilometers', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'tripMeter2': {'value': '16', 'unit': 'kilometers', 'timestamp': '2020-11-19T21:23:24.424Z'}, 'distanceToEmpty': {'value': '9', 'unit': 'kilometers', 'timestamp': '2020-11-19T21:23:24.424Z'}}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def tyres(self, print=False):
        """Vehicle's Latest Tyre Pressure Values
        * frontLeft
        * frontRight
        * rearLeft
        * rearRight

        Each tyre returns a value and a timestamp 
        "frontLeft": { "value": "LOW|NORMAL|HIGH|LOWSOFT|LOWHARD|NOSENSOR|SYSTEMFAULT", "timestamp": "YYYY-MM-DDTHH:MM:SS.SSSZ" }

        Returns:
            str: JSON

        Example:
            {'frontLeft': {'value': 'NORMAL', 'timestamp': "YYYY-MM-DDTHH:MM:SS.SSSZ"}, 'frontRight': {'value': 'NORMAL', 'timestamp': "YYYY-MM-DDTHH:MM:SS.SSSZ"}, 'rearLeft': {'value': 'NORMAL', 'timestamp': "YYYY-MM-DDTHH:MM:SS.SSSZ"}, 'rearRight': {'value': 'NORMAL', 'timestamp': "YYYY-MM-DDTHH:MM:SS.SSSZ"}}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def warnings(self, print=False):
        """Vehicle's Latest Warning Values like bulb failure

        Returns:
            str: _description_
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if print:
            self.__print_json(r)
        else:
            return r
    
    def windows(self, print=False, action=None) -> str:
        """Vehicle's Latest Window Status Values
        * frontLeft
        * frontRight
        * rearLeft
        * rearRight

        Each window returns the status and a timestamp 
        "frontLeft": { "value": "CLOSED|OPEN", "timestamp": 1599996619 }

        Returns: 
            str: JSON

        Example:
            {"status": 0,"operationId": "string","data": {"frontLeft": { "value": "string", "timestamp": 1599996619 },"frontRight": {"value": "string","timestamp": 1599996619},"rearLeft": { "value": "string", "timestamp": 1599996619 },"rearRight": { "value": "string", "timestamp": 1599996619 }}}
        """
        self_name = inspect.stack()[0][3]
        r = self.__make_info_call(self_name)
        if action == "open":
            self.__make_action_call("lock");
        if print:
            self.__print_json(r)
        else:
            return r


    def __make_info_call(self, endpoint='') -> str:
        vehicle = None
        content = self.get_service_data(endpoint)
        if content:
            vehicle = self.__get('/{}/{}'.format(self.__vin, endpoint), header_access = content)
            if vehicle:
                logging.debug(vehicle['data'])
                return vehicle
            else:
                logging.warn("No car info for {} found".format(endpoint))
                return None       

    def __make_action_call(self, endpoint='') -> str:
        vehicle = None
        content = self.get_service_data(endpoint)
        accept = self.get_service_data('commands/' + endpoint)
        if content:
            vehicle = self.__post('/{}/{}'.format(self.__vin, endpoint), content_type = content, header_accept = accept)
            if vehicle:
                logging.debug(vehicle['data'])
                return vehicle
            else:
                logging.warn("No car info for {} found".format(endpoint))
                return None      


    def __get(self, endpoint: str, header_access: str) -> str:
        """Wrapper for GET request

        Args:
            endpoint (str): URI endpoint
            header_access (str): service

        Returns:
            str: JSON
        """
        return self.__api_call(endpoint = endpoint, header_accept = header_access, method = 'get')


    def __post(self, endpoint, content_type, header_accept) -> str:
        """Wrapper for POST request

        Args:
            endpoint (str): URI endpoint
            content_type (str): header Content-Type 
            header_accept (str): header ACCEPT 

        Returns:
            str: JSON
        """
        return self.__api_call(endpoint = endpoint, content_type = content_type, header_accept = header_accept, method = 'post')


    def __api_call(self, endpoint, header_accept, method, content_type=None) -> str:
        """
        Send a POST or GET request with required header

        Args:
            endpoint (str): URI endpoint
            content_type (str): ACCESS
            header_accept (str): lock unlock open close
            method (str): GET|POST

        Returns:
            str: JSON
        """
        api_resp = None

        if method == 'get':
            h = {'accept': header_accept, 'Authorization': self.__token, 'vcc-api-key': self.__vcc_key}
            api_resp = self.__api_session.get(url = self.__volvo_uri + endpoint, headers = h)
            self.__api_resp = json.loads(api_resp.content)
        elif method == 'post':
            h = {'content-Type': content_type, 'accept': header_accept, 'Authorization': self.__token, 'vcc-api-key': self.__vcc_key}
            api_resp = self.__api_session.post(url = self.__volvo_uri + endpoint, headers = h)
        else:
            print('Method {method} is not supported!')

        if self.__api_resp and self.__response_handling():
            return self.__api_resp
        else:
            return False


    def __set_gobal_headers(self) -> None:
        self.__api_session.headers.update({
            'Authorization': self.__token,
            'vcc-api-key': self.__vcc_key
        })


    def __set_opt_id(self, key:str) -> None:
        """Set key value pair for operationId

        Args:
            key (str): Type of service
        """
        self.__operation_id[key] = self.__api_resp['operationId']

    def __response_handling(self) -> bool:
        """Analyze the API response for 200,202, and > 400.  
        If the return is a 202 it means the request was not compleated and 
        a 2nd request needs to be send with the operationId to complete the request.

        Returns:
            bool: If response is 200 or 202 True else False
        """
        success = False
        if self.__api_resp['status'] == 200:
            success = True
            self.__waiting = False
        elif self.__api_resp['status'] == 202:
            logging.info("Status: {}, Message: {}".format(self.__api_resp['status'], self.__api_resp['error']['description']))
            success = True
            self.__waiting = False
        else:
            logging.error("Status: {}, Message: {}".format(self.__api_resp['status'], self.__api_resp['error']['description']))
            exit()
        return success


    def set_unit(self, unit = 'metric') -> None:
        """Set mesurment unit, default unit is metric

        Args:
            unit (str, optional): _description_. Defaults to 'metric'.

        Raises:
            ValueError: If unit is not metric or imperial 
        """
        units  = ['imperial', 'metric']
        if unit.lower() not in units:
            raise ValueError("Invalid unit type. Expected one of: %s", unit.lower())
        
        self.__unit = unit.lower()


    def __C2F(self, value:str) -> float:
        """Convert C into F

        Args:
            value (str): Celsius value

        Returns:
            float: Celsius or Fahrenheit value
        """
        return value if self.__unit == 'imperial' else (value * 9/5) + 32

        
    def __getKm2Miles(self, value:float) -> float:
        """Convert kilometers into miles

        Args:
            value (float): Kilometer value

        Returns:
            float: Kilometer or Miles value
        """
        return value if self.__unit == 'imperial' else value/1.609


    def get_service_data(self, endpoint='') -> str:
        """Match the URI endpoint name to its corresponding ACCESS (GET) and CONTENT-TYPE (POST)

        Args:
            endpoint (str, optional): _description_. Defaults to '' =>  vehiclelist.

        Returns:
            str: application/vnd.volvocars.api.connected-vehicle.XXXXXXXXXXX.v1+json
        """
        for k, v in self.__services.items():
            for vv in v:
                if endpoint == vv:
                    return k
        
        return None


wd = NightGuard(vin='YV4952NA4F120DEMO')
wd.set_unit('imperial')
d = wd.windows(True, action="open")
