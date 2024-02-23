# use a official python image
FROM python:3.11-alpine
# setting the working directory
WORKDIR /usr/src/app
# copy the requirements file to install depedencies
COPY requirements.txt .
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# create a not root user to run the app for improve the security, without superuser privileges
RUN adduser -D granada_general
# changing the default user
USER granada_general
# copy the code to the container and setting the user owner
COPY --chown=granada_general:granada_general . .
# expose the port for the app
EXPOSE 8043
