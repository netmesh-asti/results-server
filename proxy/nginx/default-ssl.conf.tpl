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

    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    include     /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    include /etc/nginx/mime.types;

    location /static {
        alias /vol/static/portal_statics;
    }

    location /gis/staticfiles {
	alias /vol/static/staticfiles/staticfiles;
    } 

    location /portal/static {
        alias /vol/static;
    }

    location /portal {
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
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
