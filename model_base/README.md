# Base-container for cv-models

All containers with CV-models must be based on it


## How to build and push

There are Makefile that simplify this problem. You can run the following command to build base image.
```bash
make build
```

Also there are build command for mac with m1.
```bash
make build_mac_m1
```

To push base model to the registry you can use the following command:
```bash
docker push registry.visionhub.ru/models/base:v5
```
If you want to push to different registry:
```bash
docker tag registry.visionhub.ru/models/base:v5 public.registry.visionhub.ru/models/base:v5
docker push public.registry.visionhub.ru/models/base:v5
```
