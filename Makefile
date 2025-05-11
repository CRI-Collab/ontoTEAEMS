all:
	docker buildx build --platform linux/amd64 -t eddy/ontoteams:v1 --push . 