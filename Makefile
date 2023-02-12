help:
	@echo "upgrade_packages						upgrades required packages and write them into requirements.in file"
	@echo "format						formats the whole source code with black formatter"
upgrade_packages:
	pip-compile -U requirements.txt --output-file requirements.in

format:
	black .

run:
	docker compose -f docker-compose-local.yml up --build

deploy_prod:
	docker-compose -f docker-compose-prod.yml up --build -d