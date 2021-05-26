all: build

build:
	cp -rL ./shared_modules_link ./shared_modules && docker build . -t registry.visionhub.ru/models/base:v5 && rm -rf ./shared_modules

build_mac_m1:
	cp -r ./shared_modules_link ./shared_modules && docker build . -t registry.visionhub.ru/models/base:v5 -f Dockerfile.aarm64 && rm -rf ./shared_modules
