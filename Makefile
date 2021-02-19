all: build run-dev clean

create-network:
	docker network create inferoxy

build:
	docker build . -t inferoxy:${INFEROXY_VERSION}
run-dev:
	docker run --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  -p 7787:7787 -p 7788:7788 \
	  --name inferoxy --rm \
	  --network inferoxy \
	  inferoxy:${INFEROXY_VERSION}

clean:
	docker rmi inferoxy:${INFEROXY_VERSION}
