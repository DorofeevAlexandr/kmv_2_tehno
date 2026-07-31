FROM postgres:16-alpine
RUN rm -rf /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN echo "Europe/Moscow" > /etc/timezone
COPY lines_database.sql /docker-entrypoint-initdb.d/lines_database.sql
