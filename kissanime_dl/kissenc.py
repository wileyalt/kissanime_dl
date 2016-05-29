# -*- coding: utf-8 -*-
# Wiley Yu

try:
	from pkcs7 import PKCS7Encoder
except ImportError:
	from .pkcs7 import PKCS7Encoder

#from Crypto.Protocol import KDF
from Crypto.Cipher import AES

def kissenc(raw_str):
	jj = raw_str.decode('base64')
	k = '\xa5\xe8\xd2\xe9\xc1r\x1a\xe0\xe8J\xd6`\xc4r\xc1\xf3'
	l = '\x8a\xb7\x1f\xb3J\xa4t\xe3,\x08:\xca\xc7jLD'
	i = AES.new(l, AES.MODE_CBC, k)
	filled = i.decrypt(jj)
	pkc = PKCS7Encoder()
	
	return pkc.decode(filled)

