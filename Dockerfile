FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p /var/www/html/media
RUN mkdir /var/www/html/static
RUN mkdir /npm_build
RUN apt update && apt dist-upgrade -y
RUN apt install curl git -y
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash -
RUN git clone --single-branch --branch frontend https://github.com/Aninstance/simple-photo-management.git /npm_build
WORKDIR  /npm_build/public
RUN apt install npm -y
RUN npm install --save
RUN npm run build:docker
RUN cp -a build/. /var/www/html/static/
RUN cp -a /var/www/html/static/static/. /var/www/html/static/
RUN rm -rf /var/www/html/static/static
WORKDIR /npm_build
COPY spm.conf /etc/nginx/conf.d/
COPY nginx.conf /etc/nginx/
WORKDIR /
RUN rm -rf /npm_build
EXPOSE 80