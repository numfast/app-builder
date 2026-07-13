APP     := calc
VERSION := 1.0.0

.PHONY: run package test clean

run:
	python -m framework_builder run full.toml

package:
	python -m framework_builder package full.toml releases/$(APP)-full-v$(VERSION).zip
	python -m framework_builder package lite.toml releases/$(APP)-lite-v$(VERSION).zip

test:
	python -m framework_builder run lite.toml

clean:
	rm -rf __pycache__/
	rm -rf src/*/__pycache__/
	rm -rf src/*/_lib/__pycache__/
	rm -f releases/*.zip
