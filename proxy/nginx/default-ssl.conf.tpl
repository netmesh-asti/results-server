server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        return 301  https://$host$request_uri;
    }



}

server {
    listen      443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    client_max_body_size 100M;
    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    include     /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    include /etc/nginx/mime.types;

    location /static/css/ {
        alias /vol/static/portal_statics/css/;
    }

    location /static/js/ {
        alias /vol/static/portal_statics/js/;
    }

    location /static/static/ {
        alias /vol/static/portal_statics/static/;
    }

    location /static/media/ {
        alias /vol/static/portal_statics/media/;
    }

    location /static/build/ {
        alias /vol/static/portal_statics/build/;
    }

    location /static/proxy/ {
        alias /vol/static/portal_statics/proxy/;
    }

    location /static/www/ {
        alias /vol/static/portal_statics/www/;
    }

    location /static/geo {
       alias /vol/static/darius_statics/static/geo;
    }
    location /static/geo/results {
       alias /vol/static/darius_statics/static/geo/results;
    }
    location /static/css {
       alias /vol/static/darius_statics/static/css;
    }
    location /static/js {
       alias /vol/static/darius_statics/static/js;
    }
    location /static/scripts {
       alias /vol/static/darius_statics/static/scripts;
     }

    location /portal/static {
        alias /vol/static;
    }

    location /portal {
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        fastcgi_temp_file_write_size 10m;
        fastcgi_busy_buffers_size 512k;
        fastcgi_buffer_size 512k;
        fastcgi_buffers 16 512k;
    }

    location /gis {

	proxy_pass http://portal:3000;
    }

    location / {
        index index.html;
        try_files $uri /index.html$is_args$args =404;
	# proxy_pass http://portal:3000;
	# index index.html
	# proxy_set_header Host portal;
        # client_max_body_size 30M;
    }
    
}
