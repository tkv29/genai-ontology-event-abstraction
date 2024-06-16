# base image
FROM ubuntu:latest

# set environment variables
ENV PYTHONUNBUFFERED=1

# set working directory
ENV DockerHOME=/home/app/GOEA
RUN mkdir -p $DockerHOME 
WORKDIR $DockerHOME

# copy source files
COPY . $DockerHOME 

# expose port
EXPOSE 8000

# install dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

# start server  
CMD ["python3", "GOEA/manage.py", "runserver", "0.0.0.0:8000"]