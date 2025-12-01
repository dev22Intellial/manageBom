from django.core.management.base import BaseCommand
from bom.models import BOMItem
import re

class Command(BaseCommand):
    help = 'Imports a BOM file'

    def handle(self, *args, **options):
        # For now, we are using the OCR text from the bom.pdf.
        # In the future, this can be extended to parse different file formats.
        ocr_text = """
Reference designators,Quantity,Identified MPN,Identified manufacturer
A1,1,PRO-OB-440,Proant AB
C1 C3 C9,3,GRM188R60J475KE19D,Murata
C2,1,8.75116E+11,WVorth Elektronik
C4,1,GRM188R61E105KA12D,Murata
C5 C11 C13 C19 C20 C21 C22 C23 C24 C25 C26 C27 C28,13,GCJ188R71C104KA01D,"Murata Electronics North America"
C14 C15 C29 C30,4,GCM1885C1H101JA16D,Murata
C17 C18,2,GPC0402101,Generic part
C31,1,GCM188R72A102KA37D,Murata
C32 C33 C34,3,GPC0603101,Generic part
D1 D2 D3 D4 D14,5,CRS08,Toshiba
D5 D6 D7 D8 D9 D10 D11 D12 D13,9,sk6812MINI,"Shenzhen Fedy Technology"
J1,1,"SDDC 1,5/ 2-PV-3,5",Phoenix Contact
J2 J3,2,79578211,Wurth
J4,1,M40-3100545R,Harwin
L1,1,74438335068,"WVorth Elektronik"
L2,1,744784115A,Wurth
L3,1,74479777310A,"Wurth Elektronik"
L4,1,GPR040210K,Generic part
LDR1,1,NSL-19M51,Luna
Q1 Q2,2,NSVBC850CLT1G,"ON Semiconductor"
R1 R3 R11,3,MCWR06X4991FTL,Multicomp
R2 R8 R9,3,CRCW060310KOFKTABC,Vishay
R4 R5 R10,3,GPR06033M3,Generic part
R6 R7,2,CRCW0603100KFKTABC,Vishay
S1,1,SQ-MIN-200,SignalQuest
SW1 SW2 SW3,3,KSC621JLFS,C&K
U1,1,TPS61025DRCR,"Texas Instrument"
U2,1,nRF52832-QFAA-R7,"Nordic Semiconductor"
U3,1,AL-61SP05SA,Ekulit
"""
        lines = ocr_text.strip().split('\n')
        for line in lines[1:]:
            # Simple CSV parsing, might need to be more robust
            parts = line.split(',')
            if len(parts) == 4:
                BOMItem.objects.create(
                    reference_designators=parts[0],
                    quantity=int(parts[1]),
                    identified_mpn=parts[2],
                    identified_manufacturer=parts[3],
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported BOM data.'))
