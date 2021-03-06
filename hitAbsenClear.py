import requests
from bs4 import BeautifulSoup
import re, threading, time, sys, datetime

# Update this JSON if you have new courses

# NOTOP:
# If True, jika tidak ada diatas, Dia akan mencari kebawah pada list topic, lalu mengambil url nya, karna yg berada di list topic urlnya selalu berubah ubah
# If False, Absen berada di atas, dia akan langsung mengambil url nya, dan langsung melakukan absen
jsnArrMapel = [
	{'nmmapel':'bindo', 'notop':True, 'url':'https://elearning.pnj.ac.id/course/view.php?id=5383'},
	{'nmmapel':'aljabar', 'notop':False, 'url':'https://elearning.pnj.ac.id/mod/attendance/view.php?id=92213'},
]
for k,x in enumerate(jsnArrMapel): print(f"{k+1}. {x['nmmapel']}")
try:
	tmpIdx = input("Pilih Mapel: ")
	tmpJsn = jsnArrMapel[int(tmpIdx)-1]
	
	mapel = tmpJsn['nmmapel']
	urlAbsen = tmpJsn['url']
	noTop = tmpJsn['notop']
except Exception as e:
	print("[ERROr]",e)
	sys.exit(0)

rq = requests.Session()
url = "https://elearning.pnj.ac.id/login/index.php"
hit = rq.get(url)
html = BeautifulSoup(hit.content, "html.parser")

tokenlogin = html.find("input", {'name':'logintoken'})['value']
print("[MAPEL] :", mapel)
print(tokenlogin)

# Fill your identity
jsn = {
	"anchor": '',
	"logintoken": tokenlogin,
	"username": "-- YOUR NIM --", # <-- change this
	"password": "-- YOUR PASSWORD --", # <-- change this
	"rememberusername": "0"
}

# Proses Login
urlLogin = "https://elearning.pnj.ac.id/login/index.php"
hitLogin = rq.post(urlLogin, jsn)
htmlLogin = BeautifulSoup(hitLogin.content, "html.parser")
print("[SUKSES LOGIN] -> ", hitLogin.status_code, htmlLogin.find("a", {'id':'usermenu'}).text )
print(hitLogin.headers)
print(hitLogin.cookies)

if noTop:
	hit = rq.get(urlAbsen)
	htmlNoTop = BeautifulSoup(hit.content, "html.parser")
	aNoTop = htmlNoTop.find_all("a")
	for x in aNoTop:
		# Cari Url Absen paling akhir, yg mengibaratkan tgl sekarang
		if str(x['href']).upper().find('attend'.upper()) > -1: urlAbsen = x['href']
print("[INFO] Found URL Absen",urlAbsen)

hitAbsen = rq.get(urlAbsen)
html = BeautifulSoup(hitAbsen.content, "html.parser")
linknya = html.find_all(href=True)
urlSubmitAtte = ""
for x in linknya:
	if str(x['href']).find("sessid") > -1: urlSubmitAtte = x['href']
print(urlSubmitAtte)

tmpurlsubmit = urlSubmitAtte.split("?")[1]
tmpurlsubmit = tmpurlsubmit.split("&")
sessid = tmpurlsubmit[0].split("=")[1]
sesskey = tmpurlsubmit[1].split("=")[1]
print(f"{sessid} {sesskey}")

hitUrlSubmitAtte = rq.get(urlSubmitAtte)
html = BeautifulSoup(hitUrlSubmitAtte.content, "html.parser")
urlHadir = "https://elearning.pnj.ac.id/mod/attendance/attendance.php"
frm = html.find("form", {'action':urlHadir})
hidden = frm.find_all("input", {'type':'hidden'})

# Cari Radio dengan label Hadir
jsn = {}
for x in hidden: jsn[x['name']] = x['value']
label = frm.find_all("label", {'class':'form-check-inline'})
radio = ""
for x in label:
	if str(x.text).find("Hadir") > -1 : radio = x; break

rd = radio.find("input", {'type':'radio'})
jsn['status'] = rd['value']
print(jsn)

# Absen deh
posthadir = rq.post(urlHadir, jsn)
# IF kode == 200 maka berhasil
print(posthadir)
print(posthadir.status_code)
logFile = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
# Buat HTML untuk log file
with open(f"LogFile{logFile}.html", "w") as f: f.write(str(posthadir.content))