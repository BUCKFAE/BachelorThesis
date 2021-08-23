test:
	docker build -t test-image . 
	docker container run --rm --name test-container test-image