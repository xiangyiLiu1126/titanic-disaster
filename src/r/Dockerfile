# Base R image
FROM rocker/r-base:4.3.3

# System libs often needed by CRAN packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev libssl-dev libxml2-dev \
 && rm -rf /var/lib/apt/lists/*

# Workdir inside the image
WORKDIR /app

# Install R packages
COPY install_packages.R /app/install_packages.R
RUN Rscript /app/install_packages.R

# App code
COPY titanic_main.R /app/titanic_main.R

# Default command (you can override in `docker run`)
CMD ["Rscript","/app/titanic_main.R","--mode","all","--data_dir","/data"]

