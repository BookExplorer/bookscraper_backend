FROM postgres:latest
ENV POSTGRES_PASSWORD=mysecretpassword
ENV POSTGRES_USER=myuser
ENV POSTGRES_DB=bookmap_db
EXPOSE 5432

