# Import libraries
import requests
import PyPDF2
from bs4 import BeautifulSoup

  
url_list = [
"http://frequencyplansatellites.altervista.org/ABS.html",
"http://frequencyplansatellites.altervista.org/AlcomSat.html",
"http://frequencyplansatellites.altervista.org/Angosat.html",
"http://frequencyplansatellites.altervista.org/Apstar.html",
"http://frequencyplansatellites.altervista.org/Arabsat.html",
"http://frequencyplansatellites.altervista.org/ARSAT.html",
"http://frequencyplansatellites.altervista.org/Asiasat.html",
"http://frequencyplansatellites.altervista.org/Azerspace.html",
"http://frequencyplansatellites.altervista.org/Bank_Rakyat_Indonesia.html",
"http://frequencyplansatellites.altervista.org/Belintersat.html",
"http://frequencyplansatellites.altervista.org/Bsat.html",
"http://frequencyplansatellites.altervista.org/BTRC.html",
"http://frequencyplansatellites.altervista.org/BulSatCom.html",
"http://frequencyplansatellites.altervista.org/ChinaSat.html",
"http://frequencyplansatellites.altervista.org/CongoSat.html",
"http://frequencyplansatellites.altervista.org/Deutsche_Telekom.html",
"http://frequencyplansatellites.altervista.org/DirecTV.html",
"http://frequencyplansatellites.altervista.org/DLR.html",
"http://frequencyplansatellites.altervista.org/Echostar.html",
"http://frequencyplansatellites.altervista.org/Embratel.html",
"http://frequencyplansatellites.altervista.org/Eutelsat.html",
"http://frequencyplansatellites.altervista.org/GapSat.html",
"http://frequencyplansatellites.altervista.org/Yamal.html",
"http://frequencyplansatellites.altervista.org/Global_IP.html",
"http://frequencyplansatellites.altervista.org/GTE.html",
"http://frequencyplansatellites.altervista.org/Hellas_Sat.html",
"http://frequencyplansatellites.altervista.org/Hispasat.html",
"http://frequencyplansatellites.altervista.org/Hylas.html",
"http://frequencyplansatellites.altervista.org/ictQatar.html",
"http://frequencyplansatellites.altervista.org/Inmarsat.html",
"http://frequencyplansatellites.altervista.org/Insat.html",
"http://frequencyplansatellites.altervista.org/Intelsat.html",
"http://frequencyplansatellites.altervista.org/JAXA.html",
"http://frequencyplansatellites.altervista.org/JcSat.html",
"http://frequencyplansatellites.altervista.org/Kazsat.html",
"http://frequencyplansatellites.altervista.org/Koreasat.html",
"http://frequencyplansatellites.altervista.org/LaoSat.html",
"http://frequencyplansatellites.altervista.org/Lybid.html",
"http://frequencyplansatellites.altervista.org/Measat.html",
"http://frequencyplansatellites.altervista.org/Nahuelsat.html",
"http://frequencyplansatellites.altervista.org/NBN.html",
"http://frequencyplansatellites.altervista.org/NicaSat.html",
"http://frequencyplansatellites.altervista.org/NigComSat.html",
"http://frequencyplansatellites.altervista.org/Nilesat.html",
"http://frequencyplansatellites.altervista.org/NSAB.html",
"http://frequencyplansatellites.altervista.org/Olympus.html",
"http://frequencyplansatellites.altervista.org/Optus.html",
"http://frequencyplansatellites.altervista.org/Paksat.html",
"http://frequencyplansatellites.altervista.org/Palapa.html",
"http://frequencyplansatellites.altervista.org/PT_Pasifik_Satelit_Nusantara.html",
"http://frequencyplansatellites.altervista.org/Rascom.html",
"http://frequencyplansatellites.altervista.org/Royal_Group_of_Cambodia.html",
"http://frequencyplansatellites.altervista.org/RSCC.html",
"http://frequencyplansatellites.altervista.org/Satcom.html",
"http://frequencyplansatellites.altervista.org/SatMex.html",
"http://frequencyplansatellites.altervista.org/SBS.html",
"http://frequencyplansatellites.altervista.org/SES.html",
"http://frequencyplansatellites.altervista.org/Sinosat.html",
"http://frequencyplansatellites.altervista.org/Sirius_Satellite_Radio.html",
"http://frequencyplansatellites.altervista.org/Amos.html",
"http://frequencyplansatellites.altervista.org/Spaceway.html",
"http://frequencyplansatellites.altervista.org/ST.html",
"http://frequencyplansatellites.altervista.org/Superbird.html",
"http://frequencyplansatellites.altervista.org/SupremeSat.html",
"http://frequencyplansatellites.altervista.org/Telecom.html",
"http://frequencyplansatellites.altervista.org/Telenor.html",
"http://frequencyplansatellites.altervista.org/Telesat.html",
"http://frequencyplansatellites.altervista.org/Thaicom.html",
"http://frequencyplansatellites.altervista.org/Tupac_Katari.html",
"http://frequencyplansatellites.altervista.org/Turkmensat.html",
"http://frequencyplansatellites.altervista.org/Turksat.html",
"http://frequencyplansatellites.altervista.org/Venesat.html",
"http://frequencyplansatellites.altervista.org/Viasat.html",
"http://frequencyplansatellites.altervista.org/Vinasat.html",
"http://frequencyplansatellites.altervista.org/Wild_Blue.html",
"http://frequencyplansatellites.altervista.org/XM-Radio.html",
"http://frequencyplansatellites.altervista.org/Yahsat.html"]


for url in url_list:
    # Requests URL and get response object
    response = requests.get(url)

    # Parse text obtained
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all hyperlinks present on webpage
    links = soup.find_all('a')



    # From all links check for pdf link and
    # if present download file
    i = 0+i
    for link in links:
        if ('.pdf' in link.get('href', [])):

            print("Downloading file: ", i)

            # Get response object for link
            response = requests.get(link.get('href'))

            # Write content in pdf file
            pdf = open("pdf"+str(i)+".pdf", 'wb')
            pdf.write(response.content)
            pdf.close()
            i += 1
