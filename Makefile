.PHONY: build push run

DOCKER_IMAGE = eddy/ontoteams:v3

build:
	docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE) .

push:
	docker push $(DOCKER_IMAGE)

run:
	docker run -p 8501:8501 $(DOCKER_IMAGE)

all: build push