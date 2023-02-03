help:
	@echo "upgrade_packages						upgrades required packages and write them into requirements.in file"

upgrade_packages:
	pip-compile -U requirements.txt --output-file requirements.in