docker build -t action:latest -e DATABASE_URL=$DATABASE_URL \
	-e DEBUG=$DEBUG \
	-e SECRET_KEY=$SECRET_KEY .