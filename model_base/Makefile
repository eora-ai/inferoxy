all: copy build delete

copy:
	cp -r ../shared_modules ./shared_modules

build:
	docker build . -t registry.visionhub.ru/models/base:v4

delete:
	rm -rf ./shared_modules
