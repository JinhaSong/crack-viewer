FROM muhanit/crack-site:latest

ENV LC_ALL=C.UTF-8

ENV DJANGO_SUPERUSER_USERNAME root
ENV DJANGO_SUPERUSER_EMAIL none@none.com
ENV DJANGO_SUPERUSER_PASSWORD password

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

RUN chmod -R a+w /workspace

EXPOSE 8000
