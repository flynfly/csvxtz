"""
This class creates an instance of the Trigno base. Put your key and license here.
"""
import clr
clr.AddReference("D://python/Example-Applications/Python/resources/DelsysAPI")
clr.AddReference("System.Collections")

from Aero import AeroPy

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABLU7awHwKPzN/aHIvj1Gf4mfpTE0HId20xnVN5aBP2Mo475fj00dx1byLYwnyLs2PEhr+Q7tQggMvp/YQtPsQPM="
license = "<License>"\
          "<Id>2417b07c-802b-4542-acee-0d772cdc0c91</Id>"\
          "<Type>Standard</Type>"\
          "<Quantity>10</Quantity>"\
          "<LicenseAttributes>"\
          "<Attribute name='Software'></Attribute>"\
          "</LicenseAttributes>"\
          "<ProductFeatures>"\
          "<Feature name='Sales'>True</Feature>"\
          "<Feature name='Billing'>False</Feature>"\
          "</ProductFeatures>"\
          "<Customer>"\
          "<Name>Song Xu</Name>"\
          "<Email>1286906532@qq.com</Email>"\
          "</Customer>"\
          "<Expiration>Sat, 26 Apr 2031 04:00:00 GMT</Expiration>"\
          "<Signature>MEUCIQCl2aMPQbHBv14J3k2RNfPYnB5yPnU81EMfcbpv6q0tIgIgBP5DO5EaB1jYozk6DOZaASfm/uJG3Oie8foAGGYIhEs=</Signature>"\
          "</License>"\

class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()