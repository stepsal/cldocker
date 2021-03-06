#!/usr/bin/env python3

from lib.chainlink import ChainlinkNode
from lib.geth import Geth
from lib.parity import Parity
from lib.config import Config
from docker import APIClient
import signal, subprocess, sys, threading, time

def main():
	if sys.argv[1:]:
		command_controller(sys.argv[1:])
	else:
		setup()

def command_controller(*args):
	if args[0][0].lower() == "clean":
		clean()
	elif args[0][0].lower() == "pull":
		pull(args[0][1].lower())
	elif args[0][0].lower() == "start-cl":
		update_chainlink()
	elif args[0][0].lower() == "update-cl":
		update_chainlink()
	elif args[0][0].lower() == "stop-cl":
		stop_chainlink()
	elif args[0][0].lower() == "logs-cl":
		logs_chainlink()
	elif args[0][0].lower() == "restart-eth":
		restart_ethereum()
	elif args[0][0].lower() == "stop-eth":
		stop_ethereum()
	elif args[0][0].lower() == "logs-eth":
		logs_ethereum()
	elif args[0][0].lower() == "logs":
		logs_all()

def pull(image):
	cli = APIClient()
	if image.lower() == "chainlink":
		sys.stdout.write(cli.pull("smartcontract/chainlink", tag="latest"))
	elif image.lower() == "geth":
		sys.stdout.write(cli.pull("ethereum/client-go", tag="stable"))
	elif image.lower() == "parity":
		sys.stdout.write(cli.pull("parity/parity", tag="stable"))

def start_chainlink(host_port):
	return ChainlinkNode(host_port)

def update_chainlink():
	pull("chainlink")
	used_ports = []
	containers = []
	cli = APIClient()
	for container in cli.containers(filters={"ancestor":"smartcontract/chainlink","status":"running"}):
		used_ports.append(container["Ports"][1]["PublicPort"])
		containers.append(container)
	if len(used_ports) > 0:
		new_container = start_chainlink(sorted(used_ports)[-1] + 1)
		for container in containers:
			cli.kill(container["Id"])
	else:
		new_container = start_chainlink(6689)
	sys.stdout.write(new_container.container.name + "\n")

def stop_chainlink():
	cli = APIClient()
	for container in cli.containers(filters={"ancestor":"smartcontract/chainlink","status":"running"}):
		cli.kill(container["Id"])

def logs_chainlink():
	cli = APIClient()
	for container in cli.containers(filters={"ancestor":"smartcontract/chainlink","status":"running"}):
		logs(container)

def logs_ethereum():
	cli = APIClient()
	for container in cli.containers(filters={"name":"eth","status":"running"}):
		logs(container)

def logs_all():
	cli = APIClient()
	for container in cli.containers(filters={"status":"running"}):
		container = threading.Thread(target=logs, args=[container])
		container.daemon = True
		container.start()
	while True:
		time.sleep(1)

def logs(container):
	cli = APIClient()
	for byte in cli.logs(container, follow=True, stream=True, tail=100):
		sys.stdout.write(str(byte.decode()))

def fresh_start_ethereum(config):
	if config.client.lower() == "parity":
		eth_client = Parity(chain=config.chain.lower(), syncmode=config.syncmode.lower())
	elif config.client.lower() == "geth":
		eth_client = Geth(chain=config.chain.lower(), syncmode=config.syncmode.lower())
	return eth_client

def restart_ethereum():
	containers = []
	cli = APIClient()
	for container in cli.containers(filters={"name":"eth","status":"running"}):
		containers.append(container)
		cli.restart(container)
	if len(containers) > 0:
		return True
	else:
		return False

def stop_ethereum():
	cli = APIClient()
	for container in cli.containers(filters={"name":"eth","status":"running"}):
		cli.stop(container)

def clean():
	with open(".env.example") as base_env:
		env_example = base_env.read()
	with open(".env", "w") as new_env:
		new_env.write(env_example)

def setup():
	config = Config(defaults=input("Do you want all the defaults? (Local, Ropsten, Parity, Light) [Y]: ") or "Y")
	if config.defaults.lower() == "n":
		config.set_custom_fields()
	if config.eth:
		eth_client = fresh_start_ethereum(config)
		eth_ip = eth_client.get_ip()
		config.set_eth_ip(eth_ip)
	config.write_config()
	create_secrets()
	generate_certs()
	cl_client = start_chainlink(6689)

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

def sigint_handler(signum, frame):
	sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    main()