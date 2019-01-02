#!/usr/bin/env python3

from lib.chainlink import ChainlinkNode
from lib.geth import Geth
from lib.parity import Parity
from lib.config import Config
import subprocess

def main():
	config = Config(defaults=input("Do you want all the defaults? (Local, Ropsten, Parity, Light) [Y]: ") or "Y")
	if config.defaults.lower() == "n":
		config.set_custom_fields()
	if config.eth:
		if config.client.lower() == "parity":
			eth_client = Parity(chain=config.chain.lower(), syncmode=config.syncmode.lower())
		elif config.client.lower() == "geth":
			eth_client = Geth(chain=config.chain.lower(), syncmode=config.syncmode.lower())
		eth_ip = eth_client.get_ip()
		config.set_eth_ip(eth_ip)
	config.write_config()
	create_secrets()
	generate_certs()
	cl_client = ChainlinkNode(chain=config.chain.lower())

def generate_certs():
	subprocess.call((
		'openssl', 'req', '-x509', '-out', 'chainlink/tls/server.crt',  '-keyout', 'chainlink/tls/server.key', 
		'-newkey', 'rsa:2048', '-nodes', '-sha256', '-subj', '/CN=localhost', '-extensions', 'EXT', '-config', 'cert.cfg'
	))

def create_secrets():
	create_wallet_password()
	create_api_account()

def create_wallet_password():
	with open("chainlink/.password", "w") as password_file:
		password_file.write(input("Enter a wallet password: ") + "\n")

def create_api_account():
	create_api_email()
	create_api_password()
	
def create_api_email():
	with open("chainlink/.api", "w") as api_file:
		api_file.write(input("Enter an API email: ") + "\n")

def create_api_password():
	with open("chainlink/.api", "a") as api_file:
		api_file.write(input("Enter an API password: ") + "\n")

if __name__ == '__main__':
    main()