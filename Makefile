help:
	@echo "upgrade_packages						upgrades required packages and write them into requirements.in file"
	@echo "format						formats the whole source code with black formatter"
upgrade_packages:
	pip-compile -U requirements.txt --output-file requirements.in

format:
	black .