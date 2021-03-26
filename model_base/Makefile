all: build

build:
	cp -r shared_modules_link shared_modules && docker build . -t registry.visionhub.ru/models/base:v4 -f Dockerfile$(ARCH) && rm -rf ./shared_modules
