# .py failiga on kaasas logifail logi.txt, milles on kuulutuste ID. Kui
# programm tööle panna, siis võrreldakse logifailis olevaid IDsid ning
# veebilehelt leitud IDsid. Kui veebilehel on uusi kuulutusi ehk IDsid,
# mida logifailis ei ole, siis kirjutatakse ID logifaili, avatakse
# selle IDga kuulutus, tehakse sellest pilt ning saadetakse e-mailiga.
# Seda tehakse nii kaua kuni veebilehel ei ole enam logifailiga
# võrreldes uusi kuulutusi ehk uusi IDsid.

from urllib.request import urlopen
import os
import threading
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def kuulutusePilt(id):      # avan kuulutuse veebilehe ja teen sellest pildi
    browser = webdriver.Firefox()
    browser.get("http://www.kv.ee/" + str(id))
    browser.save_screenshot(str(id) + ".jpg")
    browser.quit()

def saadaKiri(ImgFileName, id):     # saadan veebilehest tehtud pildi emailiga
    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Uus kuulutus: ID' + str(id)
    msg['From'] = 'programmeerimise.projekt@gmail.com'  # eraldi tehtud e-maili aadress, mis saadab pildi soovtud aadressile
    msg['To'] = 'andreas.nolvak@outlook.com'    # saaja emaili aadress (katsetamisel soovitan muuta, muidu saan mina uued kuulutused;))

    text = MIMEText("Info on kirjaga kaasas oleval pildil.")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com:587') # gmaili serveri aadress ja port
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('programmeerimise.projekt@gmail.com', 'l1hts4ltpr00v1m1s3ks') # eraldi tehtud e-maili konto andmed
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

def idLogisse():
    netileht = urlopen("http://www.kv.ee/?act=search.simple&company_id=237&page=1&orderby=cdwl&page_size=50&deal_type=2&dt_select=2&company_id_check=237&county=12&parish=450&price_min=&price_max=&price_type=1&rooms_min=&rooms_max=&area_min=&area_max=&floor_min=&floor_max=&keyword=")
    baidid = netileht.readlines()                   # veebist lugemisel annab käsk read() meile tavalise sõne asemel hunniku baite,
                                                # mis on vaja veel sõneks "dekodeerida" (seda tehakse alumises osas)
    netileht.close()

    if not os.path.isfile(os.getcwd() + "//logi.txt"):  # Kontrollin, kas logifail on olemas. Kui pole - teen selle.
        f = open("logi.txt", "w")
        f.close()

    logifail = open("logi.txt", "r+")                     # avan logifaili (lugemiseks) ning loen seal olevad kuulutuste id'd listi
    vaadatud_kuulutused = []
    sisu = logifail.readlines()
    for el in sisu:
        vaadatud_kuulutused.append(el.strip())
    logifail.close()

    logifail = logifail = open("logi.txt", "a")     # avan logifaili nii (mode = "a"), et kõiks mis sinna kirjutatakse, kirjutatakse lõppu

    x = 1
    for i in range(len(baidid)):
        baidid[i] = baidid[i].decode()
        if "object-type-apartment" in baidid[i] and "id=" in baidid[i]:         # <tr class="object-type-apartment" id= on unikaalne osa lehekülje tekstis, millele järgneb alati
            rida_juppideks = baidid[i].split("=")                               # kuulutuse id, kuulutust saab hiljem vaadata kv.ee/id (näiteks kv.ee/2289442)
            jutumärgid_ära = rida_juppideks[2].split('"')
            kuulutuse_id = jutumärgid_ära[1]
            if not kuulutuse_id in vaadatud_kuulutused:                         # kui logifailis ei ole leitud id'd, siis kirjutan selle sinna lõppu
                   logifail.write(kuulutuse_id + "\n")
                   kuulutusePilt(kuulutuse_id)                                  # teeb logifaili kirjutatud kuulutusest pildi
                   saadaKiri(str(kuulutuse_id)+".jpg", kuulutuse_id)            # saadab tehtud pildi e-mailiga
    logifail.close()
    
def kordus():
    threading.Timer(1800, kordus).start()    # funktsioon idLogisse käivitub iga 30 minuti tagant ehk iga 30 minuti tagant kontrollitakse, kas uusi kuulutusi on tekkinud
    idLogisse()

kordus()
    
