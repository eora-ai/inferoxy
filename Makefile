all: build run-dev clean

create-network:
	docker network create inferoxy

build:
	docker build . -t registry.visionhub.ru/inferoxy:${INFEROXY_VERSION} -f Dockerfile$(ARCH)
run-in:
	docker run --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  -p 7787:7787 -p 7788:7788 \
	  --name inferoxy --rm \
	  --network inferoxy \
	  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
	  -it \
	  --entrypoint="$(ENTRYPOINT)" \
	  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION} \
	  $(COMMAND)

run-dev:
	docker run --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  -p 7787:7787 -p 7788:7788 -p 8000:8000 -p 8698:8698\
	  --name inferoxy --rm \
	  --network inferoxy \
	  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
	  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}

clean:
	docker rmi registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}

push:
	docker push registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}

generate-grpc-protos:
	make build
	rm -rf grpc_bridge/protos/
	docker run -d --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
		--name inferoxy-generator --rm \
		  --network inferoxy \
		  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
		  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}
	sleep 3
	docker cp inferoxy-generator:/app/grpc_bridge/protos ./grpc_bridge/protos
	docker stop inferoxy-generator

end-to-end-testing:
	make build
	docker run -d --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
		  --name inferoxy-${INFEROXY_CONTAINER_SUFFIX} --rm \
		  --network inferoxy \
		  -v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
		  registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}
	sleep 3
	make run-testing-container
	docker stop inferoxy-${INFEROXY_CONTAINER_SUFFIX}

run-testing-container:
	docker build testing_container testing_container:${TESTING_CONTAINER_VERSION}
	docker run -d --env-file .env.dev -v /var/run/docker.sock:/var/run/docker.sock \
	  --name inferoxy-testing-${INFEROXY_CONTAINER_SUFFIX} --rm \
	  --networ inferoxy \
	  testing_container:${TESTING_CONTAINER_VERSION} | tee public/inferoxy-end-to-end-report.txt


	  
	
