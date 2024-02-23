# use a official node image
FROM node:18-alpine
# setting the working directory
WORKDIR /usr/src/app
# copy the requirements file to install depedencies
COPY ./granada-front/package.json ./granada-front/package-lock.json ./
# install dependencies
RUN npm install
# create a not root user to run the app for improve the security, without superuser privileges
RUN adduser -D granada_frontend
# changing the default user
USER granada_frontend
# copy the code to the container and setting the user owner
COPY --chown=granada_frontend:granada_frontend ./granada-front .
# expose the port for the app
EXPOSE 3000
