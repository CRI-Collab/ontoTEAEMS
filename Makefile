all:
	docker buildx build --platform linux/amd64 -t nherbaut/ontoteams:v1 --push . 
