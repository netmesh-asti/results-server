FROM python:3.10.2-alpine
LABEL maintainer="jeanjay.quitayen@asti.dost.gov.ph"
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        libc-dev build-base libffi-dev linux-headers postgresql-dev \
        musl-dev zlib zlib-dev && \
        pip install --upgrade pip && pip install -r /tmp/requirements.txt && \
        if [ $DEV = "true" ]; \
            then pip install -r /tmp/requirements.dev.txt ; \
        fi && \
        rm -rf /tmp && \
        apk del .tmp-build-deps && \
        adduser -D -H netmesh && \
        mkdir -p /vol/web/media && \
        mkdir -p /vol/web/static && \
        chown -R netmesh:netmesh /vol && \
        chown -R netmesh:netmesh /usr/local/lib/python3.10/site-packages/durin/migrations/ && \
        chmod -R 755 /vol && \
        chmod -R +x /scripts


ENV PATH="/scripts:$PATH"

USER netmesh

CMD ["run.sh"]
