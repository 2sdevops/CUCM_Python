
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

# Create an object with the new SIP Profile
sip_profile = {
    'name': 'Sip_Profile_Test',
    'description': 'SIP Profile Test',
    'defaultTelephonyEventPayloadType': '101',
    'enableOutboundOptionsPing': 'true',
    'optionsPingIntervalWhenStatusOk': '60',
    'optionsPingIntervalWhenStatusNotOK': '120',
    'sipOptionsRetryCount': '6',
    'sipOptionsRetryTimer': '500',
    'sipBandwidthModifier': 'TIAS and AS',
    'redirectByApplication': 'false',
    'meetmeServiceUri': 'x-cisco-serviceuri-meetme',
    'ringing180': 'false',
    'timerInvite': '180',
    'timerRegisterDelta': '5',
    'timerRegister': '3600',
    'timerT1': '500',
    'timerT2': '4000',
    'retryInvite': '6',
    'retrynotInvite': '10',
    'startMediaPort': '16384',
    'stopMediaPort': '32766',
    'startVideoPort': '0',
    'stopVideoPort': '0',
    'callpickupListUri': 'x-cisco-serviceuri-opickup',
    'callpickupGroupUri': 'x-cisco-serviceuri-gpickup',
    'meetmeServiceUrl': 'x-cisco-serviceuri-meetme',
    'userInfo': 'None',
    'dtmfDbLevel': 'Nominal',
    'callHoldRingback': 'Off',
    'anonymousCallBlock': 'Off',
    'callerIdBlock': 'Off',
    'dndControl': 'User',
    'telnetLevel': 'Disabled',
    'timerKeepAlive': '120',
    'timerSubscribe': '120',
    'timeSubscriberDelta': '5',
    'maxRedirects': '70',
    'timeOffHookFirstDigit': '15000',
    'callForwardUri': 'x-cisco-serviceuri-cfwdall',
    'abbreviateDialUri': 'x-cisco-serviceuri-abbrdial',
    'confJoinEnable': 'true',
    'rfc2543Hold': 'false',
    'semiAttendedTransfer': 'true',
    'enableVad': 'false',
    'stutterMsgWaiting': 'false',
    'callStats': 'false',
    't38Invite': 'false',
    'faxInvite': 'false',
    'rerouteIncomingRequest': 'Never',
    'enableAnatForEarlyOfferCalls': 'false',
    'rsvpOverSip': 'Local RSVP',
    'fallbackToLocalRsvp': 'true',
    'sipRe11XxEnabled': 'Disabled',
    'gClear': 'Disabled',
    'sendRecvSDPInMidCallInvite': 'false',
    'userAgentServerHeaderInfo': 'Send Unified CM Version Information as User-Agent Header',
    'dialStringInterpretation': 'Phone number consists of characters 0-9, *, #, and + (others treated as URI addresses)',
    'callingLineIdentification': 'Default',
    'sipSessionRefreshMethod': 'Invite',
    'cucmVersionInSipHeader': 'Major',
    'confidentialAccessLevelHeaders': 'Disabled',
    'earlyOfferSuppVoiceCall': 'Best Effort (no MTP inserted)'
}


# Execute the AddSipProfile request
try:
    resp = service.addSipProfile( sip_profile )
except Fault as err:
    print('Zeep error: addSipProfile: {err}'.format( err = err ) )
else:
    print( 'addSipProfile response:' )
    print( resp )
input( 'Press Enter to Continue' )