ecr_arn=129033205317.dkr.ecr.eu-west-2.amazonaws.com
ecr_name=c11-poseidon-api
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $ecr_arn
docker build --platform linux/amd64 -t $ecr_name .
docker tag $ecr_name:latest $ecr_arn/$ecr_name:latest
docker push $ecr_arn/$ecr_name:latest