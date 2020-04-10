FROM nginx:latest

RUN apt-get -y update
RUN apt-get -y install nginx-extras vim

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
