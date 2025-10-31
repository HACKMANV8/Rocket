FROM mysql:8.0

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/
COPY kaggle_data/*.csv /docker-entrypoint-initdb.d/data/

# Set permissions
RUN chmod -R 755 /docker-entrypoint-initdb.d/