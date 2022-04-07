FROM python:3.10.2-alpine
LABEL DOST-ASTI SSED

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	libc-dev linux-headers postgresql-dev
RUN apk add build-base
RUN apk add libffi-dev

RUN apk add --no-cache \
			--upgrade \
		geos \
		proj \
		gdal \
		binutils \
	&& ln -s /usr/lib/libproj.so.15 /usr/lib/libproj.so \
	&& ln -s /usr/lib/libgdal.so.20 /usr/lib/libgdal.so \
	&& ln -s /usr/lib/libgeos_c.so.1 /usr/lib/libgeos_c.so

RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D netmesh
USER netmesh
