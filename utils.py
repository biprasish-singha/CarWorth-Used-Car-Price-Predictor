# Import the required libraries
import pandas as pd
import numpy as np
import re

# Create a dictionary to fetch the variants of all car brands
brand_variant_rules = {
    'Honda': [r'\bVX\s+CVT\b', r'\bZX\s+CVT\b', r'\bV\s+CVT\b', r'\bS\s+CVT\b', r'\bSV\s+CVT\b', r'\bVX\b', r'\bGXI\b',
              r'\bZX\b', r'\bSV\b', r'\bELEGANCE\b', r'\bEXI\b', r'\bEX\b', r'\bSX\b', r'\bS\b\s*\(\s*O\s*\)', r'\bV\b', 
              r'\bE\b', r'\bX\b', r'\bS\b', r'\bINSPIRE\b', r'\bV6\b', r'\bHYBRID\b', r'\bVTI\-L\b', r'\b2WD\b', r'\b4WD\b',
              r'\bANNIVERSARY\b', r'\bEXCLUSIVE\b', r'\bPRIVILEGE\b', r'\bCORPORATE\b', r'\bSPORT\b', r'\bRVI\b',
              r'\bACTIVE\b', r'\bBASIC\b', r'\bSELECT\b', r'\bRS\s+OPTION\b', r'\bRS\b'],
    
    'Toyota': [r'\bZX\s+AT\b', r'\bVX\s+AT\b', r'\bGX\s+AT\b', r'\bG\s+AT\b', r'\bV\s+AT\b', r'\bZX\b', r'\bVX\b', 
               r'\bGX\b', r'\bGD\b', r'\bG\b', r'\bV\b', r'\bJ\b', r'\bE\b', r'\bVXD\b', r'\bVIP\b', r'\bVD\b', 
               r'\bZ\b', r'\bG\b', r'\bS\b', r'\bVL\b', r'\b4X4\b', r'\b4X2\b', r'\b4WD\b', r'\b2WD\b', r'\bMS\b',
               r'\bVXD\b', r'\bVIP\b', r'\bVD\b', r'\bZ\b', r'\bG\b', r'\bS\b', r'\bMID\b', r'\bPREMIUM\b', r'\bPS\b',
               r'\bHIGH\b', r'\b[A-Z][0-9]\b', r'\bAE\b', r'\bDX\b', r'\bDG\b', r'\bGL\b', r'\bDGL\b', r'\bJS\b', 
               r'\bSPORT\b', r'\bEXECUTIVE LOUNGE\b'],
    
    'Volkswagen': [r'\bGT\s+TSI\b', r'\bGT\s+TDI\b', r'\bHIGHLINE\s+PLUS\b', r'\bCOMFORTLINE\b', r'\bHIGHLINE\b', 
                   r'\bTRENDLINE\b', r'\bGT\b\s*\bPLUS\b', r'\bGT\b', r'\bTOPLINE\b', r'\bSPORT\b'],
    
    'Maruti Suzuki': [r'\bZXI\s*PLUS\b', r'\bZXI\b\s*\+', r'\bVXI\s+OPTIONAL\b', r'\bVDI\s+OPTIONAL\b', 
                      r'\bALPHA\s*PLUS\b', r'\bALPHA\b', r'\bZETA\b', r'\bDELTA\b', r'\bSIGMA\b', 
                      r'\bZXI\b.*?\(\s*O\s*\)', r'\bBASE\b', r'\bH2\b', r'\bSTANDARD\b', r'\bHTR\b', r'\bFLEXI\b',
                      r'\bZXI\b', r'\bVXI\b\s*\bPLUS\b\s*\(\s*O\s*\)', r'\bSTD\b\s*\(\s*O\s*\)', 
                      r'\bVXI\b\s*\+\s*\(\s*O\s*\)', r'\bVXI\b\s*\+', r'\bVXI\b\s*\bPLUS\b', r'\bKING\b',
                      r'\bZDI\b\s*\+', r'\bZDI\b\s*PLUS', r'\bRS\b', r'\bCARGO\b', r'\bCLASSIC\b',
                      r'\bVXI\b.*?\(\s*O\s*\)', r'\bVXI\b', r'\bLXI\s*\(\s*O\s*\)', r'\bLXI\b.*?\(\s*O\s*\)', 
                      r'\bLXI\b\s*O', r'\bLXI\b', r'\bZDI\b\s*\(\s*O\s*\)', r'\bZDI\b', r'\bVDI\b\s*\(\s*O\s*\)',
                      r'\bVDI\b', r'\bLDI\b', r'\bLX\b', r'\bTOUR\s+S\b', r'\bTOUR\b', r'\bVX\b',
                      r'\bLX\b', r'\bS\b', r'\bE\s+STD\b', r'\bAC\b\s*\(\s*O\s*\)', r'\bAC\b', r'\bSTD\b', r'\bE\b'],
    
    'BMW': [r'\bM\d{1,3}[A-Z]*\b', r'\b\d{3}[A-Z]{1,3}\b', r'\d+\.\d+\s*[A-Z]{1,2}', 
            r'\bXDRIVE\d{1,2}[A-Z]*\b', r'\bCOMPETITION\b', r'\bXDRIVE\s*\d+[A-Z]+\b',
            r'\bSDRIVE\s*\d{1,2}[A-Z]*\b', r'\bM\s+SPORT\b', r'\bSPORTX\s+PLUS\b', r'\bLUXURY\s+LINE\b', 
            r'\bSPOERTLINE\b', r'\bEXCLUSIVE\b'],
    
    'Ford': [r'\bTITANIUM\s*PLUS\b', r'\bTITANIUM\b\s*\+', r'\bTITANIUM\b', r'\bTREND\s+PLUS\b', r'\bTREND\b\s*\+', 
             r'\bTREND\b', r'\bAMBIENTE\b', r'\bSPORTS\b', r'\bLXI\b', r'\bZXI\b', r'\bEXI\b', r'\bS\b', r'\bV8\b', 
             r'\bCLXI\b', r'\bTITATINIUM\b', r'\bPLATINUM\b', r'\bSIGNATURE\b', r'\bTHUNDER\b', r'\bSE\b', 
             r'\b4X2\b', r'\b4X4\b', r'\bHURRICANE\b', r'\bSXI\b', r'\bSTYLE\b', r'\bFLAIR\b'],
    
    'KIA': [r'\bGTX\s+PLUS\b', r'\bHTX\s+PLUS\b', r'\bHTK\s+PLUS\b', r'\bGTX\s*\(\s*O\s*\)', r'\bHTX\+\b', 
            r'\bHTK\+\b', r'\bLUXURY\s*\(O\)\b', r'\bGTX\+\b', r'\bLUXURY\s+PLUS\b', r'\bLIMOUSINE\b', 
            r'\bLUXURY\b', r'\bHTE\b', r'\bGTK\b', r'\bGTX\b', r'\bHTX\b', r'\bHTK\b', r'\bPREMIUM\b', 
            r'\bPRESTIGE\b\s+\bPLUS\b', r'\bPRESTIGE\b', r'\bX\b'],
    
    'Mercedes-Benz': [r'\bAMG\s+[A-Z]*\d+\b', r'\b[A-Z]{1,3}\s*\d{2,3}[A-Z]*\b', r'\bMAYBACH\b', r'\bELEGANCE\b', 
                      r'\bCLASSIC\b', r'\bKOMPRESSOR\b', r'\bURBAN SPORT\b', r'\bSPORT\b', r'\bCLASSIC\b', 
                      r'STYLE\b', r'\bBLUE\sEFFICIENCY\b', r'\bK\b'],
    
    'Hyundai': [r'\bSX\b.*?\(\s*O\s*\)', r'\bSX\s*\(O\)\b', r'\bSX\s+OPTIONAL\b', r'\bSPORTZ\s+PLUS\b', 
                r'\bASTA\s+OPTIONAL\b', r'\bERA\b\s*\+', r'\bSX\b\s*\+', r'\bMAGNA\b.*?\+', r'\bPRIME\b.*?T\+',
                r'\bPLATINUM\b\s*\(O\)', r'\bSIGNATURE\b\s*\(O\)', r'\bD[\s-]*LITE\s*\+?', r'\bGL\s+PLUS\b', 
                r'\bPLATINUM\b', r'\bSIGNATURE\b', r'\bSPORTS\b', r'\bGLS\b', r'\bPRESTIGE\s*\(O\)\b', 
                r'\bSPOTZ\b', r'\bPRIME\s+T\b', r'\bPRIME\s+T\s*\+\b', r'\bPRIME\b', r'\bBASE\b', 
                r'\bSX\b\s*\bPLUS\b', r'\bGL\b\s*\(O\)', r'\bGL\b', r'\b2WD\b', r'\bMAGNA\b\s*\bPLUS\b',
                r'\bPRIME\s+1\.?2\s+T\b', r'\bN6\b', r'\bN8\b', r'\bASTA\b.*?\(O\)', r'\bE\b\s*\+?\s*\+', 
                r'\bERA\s+EXECUTIVE\b', r'\bERA\s*\+\b', r'\bSPORTZ\b.*?\(\s*O\s*\)', r'\bE\b\s*PLUS',
                r'\bMAGNA\s*\+\b', r'\bS\s*\(\s*O\s*\)', r'\bASTA\b', r'\bSPORTZ\b', r'\bMAGNA\b\s*\(\s*O\s*\)', 
                r'\bMAGNA\b', r'\bERA\b', r'\bSX\b', r'\bEX\b', r'\bS\b\s*\+', r'\bS\b', r'\bEXECUTIVE\b', 
                r'\bGLE\b', r'\bPRESTIGE\b', r'\bGVS\b', r'\bPREMIUM\b', r'\b4WD\b', r'\b4X4\b', r'\b4X2\b', 
                r'\bLS\b', r'\bLE\b', r'\bXE\b', r'\bXG\b', r'\bXK\b', r'\bXL\b', r'\bXO\b', r'\bXP\b', r'\bXS\b',
                r'\bE\b', r'\bLP\b', r'\b\d\.\d\s*GDI\b', r'\bCRDI\b', r'\bI\b', r'\bT\b'],
    
    'Audi': [r'\b\d{2}\s*TDI\b', r'\b\d{2}\s*TFSI\b', r'\bPREMIUM\s+PLUS\b', r'\bTECHNOLOGY\b', r'\bPREMIUM\b', 
             r'\bSPORTBACK\b', r'\bTFSI\b', r'\bTDI\b', r'\bFSI\b', r'\bSTANDARD\b', r'\bS\b', r'\bCOUPE\b', 
             r'\bTFSIQ\b'],
    
    'Renault': [r'\bRXZ\s+OPTIONAL\b', r'\bRXT\s+OPTIONAL\b', r'\bIRON\b\s*\bMAN\b', 
                r'\bRXZ\s*[\d\.]*\s*\(\s*O\s*\)', r'\bRXL\b.*?\(O\)', r'\bRXT\b.*?\(O\)', 
                r'\bRXS\b.*?\(O\)', r'\bRXZ\b.*?\(O\)', r'\bRXT\s*[\d\.]*\s*\(\s*O\s*\)', r'\bRX\s*L\b',
                r'\bRXL\b.*?\bOPT\b', r'\bRXS\b.*?\bOPT\b', r'\bGLE\b', r'\bGLS\b', r'\bGLX\b', r'\bDLE\b', 
                r'\bDLS\b', r'\bDLX\b', r'\bPLATINE\b', r'\bADVENTURE\b', r'\bE\d\b'
                r'\bRXL\b', r'\bRXE\b', r'\bRXT\b.*?\bOPT\b', r'\bRXZ\b.*?\bOPT\b',
                r'\bSTD\b', r'\bRXS\b', r'\bCLIMBER\b.*?\(O\)', r'\bCLIMBER\b', r'\bRXZ\b', r'\bRXT\b'],
    
    'MG': [r'\bSAVVY\s+PRO\b', r'\bSHARP\s+PRO\b', r'\bSMART\s+PRO\b', r'\bEXCLUSIVE\s+PRO\b', r'\bEXCLUSIVE\b', 
           r'\bSAVVY\b', r'\bSHARP\b', r'\bSMART\b', r'\bSUPER\b', r'\bSTYLE\b', r'\bSHINE\b', r'\bBLACKSTORM\b', 
           r'\bSELECT\b'],
    
    'Volvo': [r'\bB[3-6]\b', r'\bD[3-5]\b', r'\bT[4-8]\b', r'\bRECHARGE\b', r'\bINSCRIPTION\b', r'\bMOMENTUM\b', 
              r'\bR-DESIGN\b'],
    
    'Skoda': [r'\bLAURIN\s+AND\s+KLEMENT\b', r'\bSTYLE\s+PLUS\b', r'\bMONTE\s+CARLO\b', r'\bELEGANCE\b',
              r'\bAMBITION\b', r'\bACTIVE\b', r'\bSTYLE\b', r'\bL\s*AND\s*K\b', r'\bL&K\b', r'\bLK\b', r'\bRS\b', 
              r'\bL\s*&\s*K\b', r'\bL\s+K\b', r'\bAMBIENTE\b', r'\bCLASSIC\b', r'\bLAURIN KLEMENT\b', 
              r'\bRIDER\s*PLUS\b', r'\bRIDER\b', r'\bONYX\b', r'\bLEISURE\b', r'\bSPORTLINE\b', r'\bLAURIN & KLEMENT\b'],
    
    'Tata': [r'\bXZ\+\s+DARK\b', r'\bXZ\s+PLUS\b', r'\bXZ\+\b', r'\bXZA\b\s*PLUS\s*\(HS\)', r'\bAQUA\b', r'\bEGLS\b',
             r'\bXZA\b\s*PLUS\s*\(O\)', r'\bXZA\s+PLUS\b', r'\bCREATIVE\b\s*\bPLUS\b', r'\bDLG\b', r'\bDLS\b', r'\bELX\b',
             r'\bPURE\s+PLUS\s+S\b', r'\bXZA\s*\+\b', r'\bFEARLESS\s*\+', r'\bFEARLESS\b\s*\bPLUS\b', r'\bXT\b\s*\bPLUS\b',
             r'\bLXI\b', r'\bSE\b', r'\bADVENTURE\b', r'\bNRG\b', r'\bACCOMPLISHED\b', r'\bFEARLESS\b', r'\bGLS\b',
             r'\bXZ\b\s*\bPLUS\b\s*\(\s*O\s*\)', r'\bXZ\b\s*\bPLUS\b\s*\(\s*HS\s*\)', r'\bPURE\b', r'\bEGLX\b', r'\bGLX\b',
             r'\bXZ\b\s*\(\s*O\s*\)', r'\bXZ\b\s*PLUS\s*\(HS\)', r'\bXZ\b\s*PLUS\s*\(O\)', r'\bXZ\b', r'\bEVX\b'
             r'\bXM\b\s*PLUS\s*\bSUNROOF\b', r'\bXM\b\s*\bSUNROOF\b', r'\bGX\b', r'\bPLEASURE\b', r'\bPRIDE\b', 
             r'\bXM\b', r'\bXE\b', r'\bXT\b\s*\(\s*O\s*\)', r'\bXT\b', r'\bXMA\b', r'\bXTA\b', r'\bTERRA\b',
             r'\bXMS\b', r'\bXZA\b', r'\bKRAZ\b', r'\bCREATIVE\b', r'\bLS\b', r'\bEX\b', r'\bLX\b', r'\bVX\b', 
             r'\bAURA\b', r'\bELAN\b', r'\bCX\b', r'\bGOLD\b', r'\bWIZZ\b', r'\bSTD\b', r'\bPREMIO\b', r'\bCLASSIC\b'],
    
    'Mahindra': [r'\bAX7\s+LUXURY\b', r'\bAX7\s+L\b', r'\bMX\b', r'\bW11\b', r'\bAX\s*7\b', r'\bAX\s*5\b', 
                 r'\bAX\s*3\b', r'\bW10\b', r'\bW9\b', r'\bW8\b\s*\(\s*O\s*\)', r'\bW8\b', r'\bW7\b', r'\bW6\b', 
                 r'\bW5\b', r'\bW4\b', r'\bB6\b\s*\(\s*O\s*\)', r'\bGRAND\b', r'\bB4\b', r'\bDI\b', r'\bSLE\b',
                 r'\bAX\s*7\b', r'\bM2\b', r'\bRX7\b', r'\bK2\b\s*\+', r'\bK2\b', r'\bE6\b', r'\bK4\b', r'\bK6\b', 
                 r'\bCRDE\s+4X4\b', r'\bN\s*10\b', r'\bW10\b', r'\bS10\b', r'\bS11\b', r'\bT10\b', r'\bZ8\b', 
                 r'\bB6\b\s*\(\*O\*\)', r'\bB6\b', r'\bVLX\b', r'\bSLX\b', r'\bZLX\b', r'\bW6\b', r'\bS6\b', 
                 r'\bS5\b', r'\bT8\b', r'\bK8\b', r'\bLX\b', r'\bXL9\b', r'\bN\d\b', r'\b[A-Z]\s*[0-9]{1,2}\b', 
                 r'\bCRDE\b'],
    
    'Mini': [r'\bJOHN\s+COOPER\s+WORKS\b', r'\bCOOPER\b.*?\bD\b', r'\bCOOPER\b.*?\bD\b', r'\bCOOPER\b', r'\bJCW\b', 
             r'\bD\b', r'\bS\b', r'\bONE\b'],
    
    'Land Rover': [r'\bAUTOBIOGRAPHY\b', r'\bFIRST\s+EDITION\b', r'\bR-DYNAMIC\s+HSE\b', r'\bR-DYNAMIC\s+SE\b', 
                   r'\bR-DYNAMIC\s+S\b', r'\bDYNAMIC\s+HSE\b', r'\bDYNAMIC\s+SE\b', r'\bDYNAMIC\b', 
                   r'\bHSE\b', r'\bSE\b', r'\bPURE\b', r'\bTDV6\b', r'\b[A-Z]\d{3}\b', r'\bS\b'],
    
    'Jeep': [r'\bMODEL\s+S\b', r'\bTRAILHAWK\b', r'\bLIMITED\s+PLUS\b', r'\bLONGITUDE\s+PLUS\b', 
             r'\bSPORT\s+PLUS\b', r'\bSPORT\b', r'\bLIMITED\s*\(\s*O\s*\)', r'\bLIMITED\b',
             r'\bLONGITUDE\s*\(\s*O\s*\)', r'\bLONGITUDE\b', r'\bRUBICON\b', r'\b\dX\d\b'],
    
    'Chevrolet': [r'\bLTZ\s+OPTIONAL\b', r'\bLT\s+OPTIONAL\b', r'\bLTZ\b', r'\bLT\b', r'\bLS\b', r'\bPS\b', 
                  r'\bXTREME\b', r'\bELITE\b', r'\bBASE\b', r'\bTCDI\b', r'\bE\b'],
    
    'Jaguar': [r'\bR-DYNAMIC\s+HSE\b', r'\bR-DYNAMIC\s+SE\b', r'\bPORTFOLIO\b', r'\bPRESTIGE\b', r'\bPURE\b', 
               r'\bR-SPORT\b', r'\bLUXURY\b', r'\bEXECUTIVE\b', r'\bULTIMATE\b', r'\bS\b', r'\bR\b'],
    
    'Fiat': [r'\bEMOTION\s+PACK\b', r'\bEMOTION\b', r'\bDYNAMIC\b', r'\bACTIVE\b', r'\bSPORT\b', r'\bT\s*JET\b', 
             r'\bT\s*JET\s*PLUS\b', r'\bMULTIJET\b', r'\bELX\b', r'\bSLX\b', r'\bSDE\b', r'\bADVANCED\b'],
    
    'Aston Martin': [r'\bAMR\b', r'\bVANTAGE\b', r'\bVOLANTE\b'],
    
    'Porsche': [r'\bTURBO\s+S\b', r'\bCARRERA\s+4S\b', r'\bCARRERA\s+S\b', r'\bCARRERA\b', r'\bGTS\b', 
                r'\bTURBO\b', r'\bBOXSTER\b', r'\bPLATINUM\b', r'\bSTANDARD\b', r'\bS\b'],
    
    'Nissan': [r'\bXV\s+PREMIUM\b', r'\bXL\s+OPTIONAL\b', r'\bXL\b\s*O', r'\bCOMFORT\b', r'\bXV\b', r'\bXL\b', 
               r'\bXE\b'],
    
    'Force': [r'\bEXTREME\b', r'\bEXPLORER\b', r'\bXPLORER\b', r'\bEXPEDITION\b', r'\bXPEDITION\b', r'\b4X2\b', 
              r'\bEX\b', r'\bSX\b', r'\bCLASSIC\b'],
    
    'Mitsubishi': [r'\bSELECT\s+PLUS\b', r'\bSELECT\b', r'\bSPORTS\b', r'\bSPORT\b', r'\bSPIRIT\b', r'\bGLS\b', r'\bGL\b', 
                   r'\bGLXI\b', r'\bLEI\b', r'\bLXD\b', r'\bLX\b', r'\bSFX\b'],
    
    'Lexus': [r'\bF\s+SPORT\b', r'\bLUXURY\b', r'\bEXQUISITE\b', r'\bURBAN\b', r'\b\d{3}[A-Z]\b'],
    
    'Isuzu': [r'\bPRESTIGE\b', r'\bHIGH\s+LANDER\b', r'\bV-CROSS\b', r'\bS\s+CAB\b', r'\bS\s+CAB\b', r'\b\dWD\b',
              r'\bHIGH\b', r'\b\dX\d\b'],
    
    'Datsun': [r'\bT\s+OPTIONAL\b', r'\bA\s+OPTIONAL\b', r'\bT\b\s*\(\s*O\s*\)', r'\bA\b\s*\(\s*O\s*\)', 
               r'\bT\b', r'\bA\b', r'\bD\b', r'\bS\b', r'\bD1\b', r'\bNXT\b', r'\bGOLD\b', r'\bSPORT\b', r'\bSV\b', 
               r'\bREMIX\b'],
    
    'Ambassador': [r'\bGRAND\b', r'\bCLASSIC\b', r'\bNOVA\b'],
    
    'Rolls-Royce': [r'\bBLACK\s+BADGE\b', r'\bEXTENDED\s+WHEELBASE\b', r'\bEWB\b'],
    
    'ICML': [r'\bWINNER\b', r'\bEXTREME\b', r'\bCRDI\b'],
    
    'Bajaj': [r'\bRE60\b', r'\bQUTE\b'],
    
    'Opel': [r'\bSAIL\b', r'\bCLUB\b', r'\bGLS\b', r'\bGL\b', r'\bELITE\b'],
    
    'Ashok leyland': [r'\bLUXURY\b', r'\bSTANDARD\b', r'\bLE\b', r'\bV8\b'],
    
    'Bentley': [r'\bSPEED\s+EDITION\b', r'\bFIRST\s+EDITION\b', r'\bAZURE\b', r'\bMULLINER\b', r'\bSPEED\b', 
                r'\bV8\b', r'\bW12\b'],
    
    'Ssangyong': [r'\bRX7\b', r'\bRX6\b', r'\bRX5\b'],
    
    'Maserati': [r'\bTROFEO\b', r'\bGRANSPORT\b', r'\bGRANLUSSO\b', r'\bMODENA\b', r'\bGT\b'],
    
    'Citroen': [r'\bSHINE\s+DUAL\s+TONE\b', r'\bFEEL\s+DUAL\s+TONE\b', r'\bSHINE\b', r'\bFEEL\b', r'\bLIVE\b'],
    
    'Lamborghini': [r'\bPERFORMANTE\b', r'\bTECNICA\b', r'\bEVO\b', r'\bS\b'],
    
    'Hummer': [r'\bH1\b', r'\bH2\b', r'\bH3\b'],

    'Ferrari': [r'\bSPIDER\b', r'\bV8\b']
}

# Create a function to extract the variants
def extract_variant(title, brand):
    if pd.isna(title) or pd.isna(brand):
        return pd.NA
    title = str(title).upper().strip()
    brand = str(brand).strip()
    patterns = brand_variant_rules.get(brand, [])
    for pattern in patterns:
        match = re.search(pattern, title, flags=re.IGNORECASE)
        if match:
            if match.lastindex:
                return match.group(1).upper()
            return match.group(0).upper().strip()
    return pd.NA


# Create a function for Variant and Model normalization
def normalize_variant(name):
    if pd.isna(name):
        return pd.NA
    name = str(name).upper().strip()
    name = re.sub(r'\s+', ' ', name) # Remove extra spaces
    name = re.sub(r'\(\s*([A-Za-z])\s*\)', r'(\1)', name) # Normalize spaces inside brackets
    name = re.sub(r'\b\d+(\.\d+)?L\b', '', name) # Remove the trailing engine capacity
    name = re.sub(r'\b\d+\.\d+\b', '', name) # Remove the trailing decimal figures
    name = re.sub(r'\s+', ' ', name).strip() # Remove extra spaces created after replacements
    name = re.sub(r'\s*\(\s*O\s*\)\s*$', '(O)', name) # Normalize variants ending with (O)
    name = re.sub(r'\s+(PETROL|DIESEL|CNG|AMT|MT)\s*', '', name) # Remove Petrol, Diesel or CNG withing variant name
    name = re.sub(r'PLUS', '+', name) # Replace plus with +
    name = re.sub(r'\b([A-Z]+)\s+\+', r'\1+', name) # Remove the space between variant and plus sign
    name = re.sub(r'\b([A-Z]+)\b.*?\(\s*O\s*\)', r'\1(O)', name) # Remove anything between variant and (O)
    return name


# State Mapping
state_mapping = {'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam', 'BR': 'Bihar', 
                 'CG': 'Chhattisgarh', 'CT': 'Chhattisgarh', 'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana', 
                 'HP': 'Himachal Pradesh', 'JH': 'Jharkhand', 'KA': 'Karnataka', 'KL': 'Kerala', 
                 'MP': 'Madhya Pradesh', 'MH': 'Maharashtra', 'MN': 'Manipur', 'ML': 'Meghalaya', 'MZ': 'Mizoram', 
                 'NL': 'Nagaland', 'OD': 'Odisha', 'OR': 'Odisha', 'PB': 'Punjab', 'RJ': 'Rajasthan', 
                 'SK': 'Sikkim', 'TN': 'Tamil Nadu', 'TS': 'Telangana', 'TG': 'Telangana', 'TR': 'Tripura', 
                 'UK': 'Uttarakhand', 'UP': 'Uttar Pradesh', 'WB': 'West Bengal', 'AN': 'Andaman and Nicobar',
                 'CH': 'Chandigarh', 'DN': 'Dadra and Nagar Haveli', 'DD': 'Daman and Diu', 'DL': 'Delhi', 
                 'JK': 'Jammu and Kashmir', 'LA': 'Ladakh', 'LD': 'Lakshadweep', 'PY': 'Puducherry'}

# Create a function to fetch the State from the vehichle registration number
def get_state_name(reg_no):
    state_code = (reg_no.astype('string').str.strip().str[:2].str.upper())
    return state_code.map(state_mapping)

# Create a mapping for ownership
owner_mapping = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5}

# Define function to apply the ownership mapping
def get_no_of_owners(ownership_text):
    no_of_owners = ownership_text.astype('string').str.lower().str.strip()
    return no_of_owners.map(owner_mapping)
    

# Define the columns for final datframe
final_columns = ['brand', 'model', 'variant', 'body_type', 'make_year', 'state', 'km_driven', 'transmission', 
                 'previous_owners', 'fuel_type', 'engine_capacity_cc', 'seats', 'exterior_color', 'length', 
                 'width', 'height', 'wheel_base', 'front_tread', 'rear_tread', 'kerb_weight', 'gear_box', 
                 'drive_type', 'steering_type', 'turning_radius', 'front_brake_type', 'rear_brake_type', 
                 'boot_space', 'fuel_supply_system', 'alloy_wheel_size', 'max_power_delivered', 'max_power_at', 
                 'max_torque_delivered', 'max_torque_at', 'price']

# Prepare the final dataset
def get_final_dataset(df):
    df = df.reindex(columns=final_columns)
    return df


# Function to check consistency of a categorical feature at brand + model level and returns only the models having more than one unique value
def check_inconsistency(df, column):
    result = df.groupby(['brand', 'model'])[column].agg(count = lambda x: x.nunique(dropna=True), 
                                                        values = lambda x: list(x.dropna().unique())).reset_index()
    return result[result['count']>1].sort_values(['brand', 'model']).reset_index(drop=True)

# Function to fill the missing values of the categorical features
def fill_missing_values(df, column):
    df[column] = df.groupby(['brand', 'model'])[column].transform(lambda x: x.fillna(x.mode().iloc[0] 
                                                                                     if not x.mode().empty 
                                                                                     else pd.NA))
    