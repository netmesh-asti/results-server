FROM nginx:1.23.0-alpine
LABEL maintainer="jeanjay.quitayen@asti.dost.gov.ph"

COPY ./nginx/* /etc/nginx/
COPY ./run.sh /run.sh

ENV APP_HOST=netmeshapp
ENV APP_PORT=9000

RUN apk add --no-cache openssl bash
RUN chmod +x /run.sh

VOLUME /vol/static
VOLUME /vol/www

CMD ["/run.sh"]
