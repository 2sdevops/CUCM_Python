
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'schema/AXLAPI.wsdl'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

#Criação do Server Subscriber
#Segue abaixo as informações para criar um Subscriber CUCM ou IM&Presence

Server = {
    'appServerType': 'CUCM Voice/Video',
    'name': 'CUCM Subscriber',
    'description': 'CUCM Subscriber #1',
    'ipAddress': '10.255.245.31'
}

# Execute the addApplicationServer to request
try:
    resp = service.addAplicationServer( Server )
except Fault as err:
    print('Zeep error: addAplicationServer: {err}'.format(err=err))
else:
    print('addAplicationServer response:')
    print(resp)
input('Press Enter para Criar')

#---------------------------------------------------------
#Criação do CM Group

CCMGroup = {
    'name': 'CCMGroup_1',
    'members': f'{ipaddress}'
}

#Execute the addCallManagerGroup to request
try:
    resp = service.addCallManagerGroup( CCMGroup )
except Fault as err:
    print('Zeep error: addCallManagerGroup: {err}'.format(err=err))
else:
    print('addCallManagerGroup:')
    print(resp)
input('Press Enter para Criar')

#--------------------------------------------------------

#Criação do Phone NTP Reference

NTPReference = {
    'ipAddress': '1.1.1.1',
    'description': 'NTP Site 1',
    'Mode': ''
}

#Execute the addPhoneNTP to request
try:
    resp = service.addPhoneNTP ( NTPReference )
except Fault as err:
    print('Zeep error: addPhoneNTP: {err}'.format(err=err))
else:
    print('addPhoneNTP:')
    print(resp)
input('Press Enter para Criar')

#----------------------------------------

#Criação do Date/Time Group

DateTime = {
    'name': 'DateTimeGroup_SP',
    'timeZone': 'America/Sao_Paulo',
    'separator': '/',
    'dateformat': 'D/M/Y',
    'timeFormat': '24-hour',
    'selectedPhoneNtpReference': '1.1.1.1'
}

#Execute the addDateTimeGroup to request
try:
    resp = service.addDateTimeGroup ( DateTime )
except Fault as err:
    print('Zeep error: addDateTimeGroup: {err}'.format(err=err))
else:
    print('addDateTimeGroup:')
    print(resp)
input('Press Enter para Criar')

#-------------------------------

#Execute the addRegion

Region = {
    'name': '2s_SP'
    'relatedRegions': 'Default',
    'defaultCodec': ''
}

#Execute the addRegion to request
try:
    resp = service.addRegion ( Region )
except Fault as err:
    print('Zeep error: addRegion: {err}'.format(err=err))
else:
    print('addRegion:')
    print(resp)
input('Press Enter para Criar')

#-------------------------------------

#Execute the addLocation

Location = {
    'name': '2s_SP',
    ''
}