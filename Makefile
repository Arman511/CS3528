REPOSITORY_OWNER=arman511
IMAGE_NAME=cs3528_alpha
TAG=latest

build:
	docker build -t $(REPOSITORY_OWNER)/$(IMAGE_NAME):$(TAG) .

push: build
	docker push $(REPOSITORY_OWNER)/$(IMAGE_NAME):$(TAG)

all: build push
