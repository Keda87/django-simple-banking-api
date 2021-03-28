help:
	@echo ''
	@echo 'Usage: make [TARGET]'
	@echo 'Targets:'
	@echo '  build    	build docker images'
	@echo '  start    	Start banking system service'
	@echo '  stop     	Stop banking system service'
	@echo '  test     	test banking system service'
	@echo '  help     	this text'

build:
	docker-compose build

start:
	@echo "Starting banking system service..."
	docker-compose up -d

	@echo "Creating the bank database and performing migrations..."
	$(eval create_db=$(docker-compose exec bank_db createdb --username=postgres db_banking))
	@if [ '$(create_db)' != '' ]; then echo 'DB already exists'; fi;
	docker-compose exec bank_api python manage.py migrate
	docker-compose exec bank_api python manage.py collectstatic
	@echo "Done"

stop:
	docker-compose down

test:
	docker-compose exec bank_api python manage.py test --keepdb