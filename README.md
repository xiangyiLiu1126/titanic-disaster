

#  Titanic Disaster Survival Prediction

This project sets up the development environment for analyzing the Titanic dataset.  
It includes a clean folder structure, virtual environment setup, dependency management, and a Dockerfile for containerized execution.  
The goal is to prepare a reproducible environment that verifies and loads the Titanic data for further analysis in future parts of the project.

---

##  Environment Setup and How to Run

This project provides two ways to set up and run the environment: **local (virtual environment)** and **Docker**.  
Please follow one of the methods below.

---

###  Option 1: Run Locally (Recommended if Docker not available)

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
    ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
    ```
3.**Download the Titanic dataset from Kaggle and place both files inside**
    ```bash
    src/data/
    train.csv
    test.csv
    ```
4. **Run the environment check and summary**
    ```bash
    python src/app/main.py --mode check
    python src/app/main.py --mode summary
    ```
## Run the R container

Build and run (from repo root):
    docker build -f src/r/Dockerfile -t titanic-r:dev src/r
    docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-r:dev

Or specific modes:
    docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-r:dev \
      Rscript /app/titanic_main.R --mode summary --data_dir /data
    docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-r:dev \
      Rscript /app/titanic_main.R --mode train --data_dir /data
    docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-r:dev \
      Rscript /app/titanic_main.R --mode predict --data_dir /data

If Docker pulls fail due to a proxy, you can run locally:
    Rscript src/r/titanic_main.R --mode all --data_dir src/data
