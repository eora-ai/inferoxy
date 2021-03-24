all: build run-dev clean

create-network:
	docker network create inferoxy

build:
	docker build . -t registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}
run-in:
	docker run --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  -p 7787:7787 -p 7788:7788 \
	  --name inferoxy --rm \
	  --network inferoxy \
	  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
	  -it \
	  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION} \
		  $(COMMAND)
run-dev:
	docker run --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  -p 7787:7787 -p 7788:7788 -p 8000:8000\
	  --name inferoxy --rm \
	  --network inferoxy \
	  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
	  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}

clean:
	docker rmi registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}

push:
	docker push registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}
