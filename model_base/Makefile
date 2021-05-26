all: build

build:
	cp -rL ./shared_modules_link ./shared_modules && docker build . -t registry.visionhub.ru/models/base:v5 && rm -rf ./shared_modules
