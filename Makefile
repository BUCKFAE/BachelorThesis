test:
	docker-compose build
	docker-compose run --rm showdown

shell:
	docker-compose build
	docker-compose run --entrypoint /bin/bash --rm showdown 

