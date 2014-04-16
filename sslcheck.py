import socket, pprint, M2Crypto, OpenSSL, datetime,json,time

FIXDATE = datetime.datetime(2014, 4, 7, 19, 21, 29, 0)

def writeData(jdata):
	
	try:
		f = open("data.js", "w")
		try:
			f.write("var data = " + jdata + ";") #readeable js
		finally:
			f.close()
	except IOError:
		pass
	try:
		f = open("data.json", "w")
		try:
			f.write(jdata) # Write json
		finally:
			f.close()
	except IOError:
		pass

def now():
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return st

urls = {'Bancard':'www.bancard.com.py',
		'BCP': 'www.bcp.gov.py',
		'CitiBank': 'citidirect-eb.citicorp.com',
		'Banco de la Nacion Argentina':'secure.bna.com.py',
		'Sudameris':'www.sudamerisbank.com.py',
		'Vision': 'secure.visionbanco.com',
		'Familiar': 'www.familiar.com.py',
		'Continental': 'www.bancontinental.com.py',
		'Atlas':'secure.atlas.com.py',
		'GNB':'serviciostsapy.bancognb.com',
		'Itau':'www.secure.itau.com.py',
		'BBVA':'www.bbva.com.py',
		'Bancop':'www.bancop.com.py',
		'BNF':'www.bnf.gov.py',
		'Itapua':'www.bancoitapua.com.py',
		'Amambay':'www.bancoamambay.com.py',
		'Procard':'www.procard.com.py',
		'Regional':'www.secure.bancoregional.com.py'
		}

noSSL = ('Vision','Continental') #No usa OpenSSL
nosureSSL =('Itau','CitiBank','GNB','BNF', 'Bancard','BCP') #Quizas usen, no se puede asegurar

for u in urls.items():
	print u[0], ' ', u[1]

a = []

for u in urls.items():
	print u
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#print "-------- ", sock.gettimeout()
	#sock.setblocking(1)
	cxt = M2Crypto.SSL.Context()
	cxt.set_verify(M2Crypto.SSL.verify_none, depth=1)
	#M2Crypto.SSL.Connection.clientPostConnectionCheck = None
	try:
		
		c = M2Crypto.SSL.Connection(cxt, sock)
		c.setblocking(1)
		c.connect((str(u[1]), 443))
		print c.get_version()
		
		cert = c.get_peer_cert()
		certDate = cert.get_not_before().get_datetime() 
		print certDate
		if certDate.replace(tzinfo=None)< FIXDATE:
			if u[0] in noSSL:
				a.append(dict(banco=u[0], url=u[1], cert_date=str(certDate.replace(tzinfo=None)), seg=-1))
				print "SEGURO"
			elif u[0] in nosureSSL:
				a.append(dict(banco=u[0], url=u[1], cert_date=str(certDate.replace(tzinfo=None)), seg=3))
				print "No se puede saber si se usa OpenSSL"
			else:
				a.append(dict(banco=u[0], url=u[1], cert_date=str(certDate.replace(tzinfo=None)), seg=1))
				print "Falta renovar el Certificado"
		else:
			a.append(dict(banco=u[0], url=u[1], cert_date=str(certDate.replace(tzinfo=None)), seg=0))
			print " SEGURO"
	except Exception as e:
		print str(e)
		a.append(dict(banco=u[0], url=u[1], cert_date=0, seg="Error: No se pudo comprobar"))
		pass
	
a.sort()
a.insert(0,{'timestamp':now()})
jdata = json.dumps(a, indent=2, sort_keys=True)
print jdata
writeData(jdata)