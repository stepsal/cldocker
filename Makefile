install:
	pip3 install --user -r requirements.txt

setup:
	python3 main.py

clean:
	python3 main.py clean

pull-cl:
	python3 main.py pull chainlink

pull-geth:
	python3 main.py pull geth

pull-parity:
	python3 main.py pull parity

restart-eth:
	python3 main.py restart-eth

stop-eth:
	python3 main.py stop-eth

start-cl:
	python3 main.py start-cl

update-cl:
	python3 main.py update-cl

stop-cl:
	python3 main.py stop-cl

test:
	py.test tests -v

.PHONY: install setup clean pull-chainlink pull-geth pull-parity restart-eth start-cl update-cl test