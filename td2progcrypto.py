# -*- coding: utf-8 -*-
"""TD2ProgCrypto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QM0h4Po_ikoDWM_jrM-Wh4Y7KamjQOo0

Créer un entier aléatoire pouvant servir
de seed à un wallet de façon sécurisée
"""

import secrets
rand_numb=secrets.randbits(128)

rand_numb

bin(rand_numb)

hex_rand_num = hex(rand_numb)
private_key = hex_rand_num[2:]
private_key

import hashlib
m = hashlib.sha256()
m.update(bytes.fromhex(private_key))
res = m.digest()
res

hexRes = res.hex()
hexRes

checksum = hexRes[0]
checksum

full_private_key = str(private_key) + checksum
full_private_key

"""Représenter cette seed en binaire et le
découper en lot de 11 bits
"""

binKey = bin(int(full_private_key, 16))[2:].zfill(132)
binKey

def splitBinKey(binKey):
  tab = []
  start = 0
  stop = 11

  for i in range(0,12):
    tab.append(binKey[start:stop])
    start += 11
    stop += 11

  return tab


def splitBinKey2(new_key):
  subList = [new_key[n:n+11] for n in range(0, len(new_key), 11)]

  return subList


splitKey = splitBinKey(binKey)
splitKey

"""Attribuer à chaque lot un mot selon la
liste BIP 39 et afficher la seed en
mnémonique
"""

def convertToDecimal(binTab):
  intTab = []

  for i in range(0, len(binTab)):
    b = splitKey[i] # binary
    h = f'{int(b, 2):X}' # convert to hex
    i = int(h, 16) # convert to int
    intTab.append(i) # add to the table

  return intTab

intKey = convertToDecimal(splitKey)
intKey

with open('seedWords.txt',"r",encoding="utf-8") as f:
  word_list = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
  word_list = [x.strip() for x in word_list]

len(word_list)

mnemonic = []
for itm in intKey:
  mnemonic.append(word_list[itm])

mnemonic

seedPhrase = ''

for elem in mnemonic:
  seedPhrase += elem + ' '

seedPhrase = seedPhrase[:-1] # suppression de l'espace en trop

seedPhrase

"""Permettre l’import d’une seed
mnémonique
"""

# Executez la cellule pour importer votre seed

# word_list : liste des 2048 mots
def mnemonique_to_dec(word_list):
  imported_seed = input('Collez votre seed mnémonique ici: ')
  imported_seed = imported_seed.split(' ')
  decimal_list=[]
  for itm in imported_seed:
    for i in range(0,len(word_list)):
      if itm == word_list[i]:
        decimal_list.append(i)
  return decimal_list

decList = mnemonique_to_dec(word_list)

print(decList)

def decToBinList(dec_list):
  binL = []

  for elem in dec_list:
    binL.append(bin(int(elem))[2:])

  return binL

binList = decToBinList(decList)

print(binList)

def completeBin(bin_list):
  new_list=[]
  for itm in bin_list:
    res =''
    i=11-len(itm)
    for j in range(0,i):
      res+='0'
    res+=itm
    new_list.append(res) 
  return new_list

complete_binList = completeBin(binList)

print(complete_binList)

"""Extraction private key et chain code"""

mnemonic = seedPhrase
salt = "mnemonic"
iterations = 2048
keyLength = 64

seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode(), salt.encode(), iterations, keyLength)

hexSeed = seed.hex()
hexSeed

master_privateKey = hexSeed[:keyLength]
chainCode = hexSeed[keyLength:]

print(master_privateKey)
print(chainCode)

"""Extraction de la master public key

"""

pip install ecdsa

import ecdsa.util

def get_point_pubkey(point):
 if point.y() & 1:
  key = '03' + '%064x' % point.x()
 else:
  key = '02' + '%064x' % point.x()
 return key

def getPublicKey(masterPrivateKey):
  _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
  _r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
  _b = 0x0000000000000000000000000000000000000000000000000000000000000007
  _a = 0x0000000000000000000000000000000000000000000000000000000000000000
  _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
  _Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

  curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
  generator = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)
  point = generator * int(masterPrivateKey, 16)
  
  return get_point_pubkey(point)

master_publicKey = getPublicKey(master_privateKey)
master_publicKey

"""Générer une clé enfant"""

import hmac

def genererCleEnfant(index=0):
  orderOfCurve = 115792089237316195423570985008687907852837564279074904382605163141518161494337 # ordre de la courbe connu

  data = master_publicKey + str(index)
  key = chainCode

  ckd = hmac.new(bytes.fromhex(key), data.encode('utf-8'), hashlib.sha512).hexdigest()

  newChainCode = ckd[64:]

  childPrivateKey = int(ckd[:64] + master_publicKey, 16) % orderOfCurve
  childPrivateKey = hex(childPrivateKey)[2:]

  return newChainCode, childPrivateKey

childChainCode, childPrivateKey = genererCleEnfant()

print('child ChainCode :', childChainCode)
print('child Private Key :', childPrivateKey)
print('child Public Key :', getPublicKey(childPrivateKey))

"""Génerer une clé enfant à partir d'un indice N

"""

i = input('Veuillez entrer l\'indice de générationde la clé enfant (entre 0 et 2147483647)')

childChainCode, childPrivateKey = genererCleEnfant(i)
print('Génération d\'une clé enfant à l\'indice', i)
print('child ChainCode :', childChainCode)
print('child Private Key :', childPrivateKey)
print('child Public Key :', getPublicKey(childPrivateKey))

"""# Générer un enfant à l'index N à la dérication M avec l'aide de la librairie bip32.py"""

!pip install bip32
from bip32 import BIP32, HARDENED_INDEX
bip32seed = BIP32.from_seed(bytes.fromhex(hexSeed))

N = input('Index N: ')
M = input('Dérication M: ')

pubKey = bip32seed.get_extended_pubkey_from_path("m/"+M+"/"+N)

print('Public Key of '+N+' child at derivation '+M+' : '+str(pubKey[1].hex()))

privKey = bip32seed.get_extended_privkey_from_path("m/"+M+"/"+N)

print('Private Key of '+N+' child at derivation '+M+' : '+str(privKey[1].hex()))