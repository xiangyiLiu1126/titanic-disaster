# Titanic Disaster Survival Prediction

This project sets up a complete development environment for analyzing the Titanic dataset using both **Python** and **R**.  
It includes Dockerized and local environments for reproducibility, ensuring the grader (or any user) can rebuild and run the analysis in just a few steps.

---

## Project Overview

The goal of this project is to predict passenger survivability on the Titanic dataset using logistic regression models in both Python and R.  
Each environment (Python and R) includes a standalone Dockerfile, dataset handling pipeline, and reproducible instructions.

Both versions:
- Load and clean the Titanic dataset (`train.csv` / `test.csv`)
- Build a logistic regression model
- Evaluate model accuracy on training and test data
- Print all processing and model results clearly to the terminal

---

## Folder Structure

```
titanic-disaster/
│
├── src/
│   ├── app/                      # Python source folder
│   │   ├── main.py               # Python training & prediction script
│   │   └── __init__.py
│   ├── r/                        # R source folder
│   │   ├── Dockerfile            # R environment build file
│   │   ├── install_packages.R    # R package installation script
│   │   └── titanic_main.R        # R training & prediction script
│   └── data/                     # Data folder (not pushed to GitHub)
│       ├── train.csv
│       └── test.csv
│
├── requirements.txt
├── Dockerfile                    # Python environment build file
├── .dockerignore
└── README.md                     # Instructions and documentation
```

**Note:** The `src/data/` folder should contain the Titanic datasets (`train.csv` and `test.csv`), but they should **not be committed to GitHub** (already listed in `.gitignore`).

---

## How to Run — Python Environment

### Option 1: Run Locally (without Docker)

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


If Docker pulls fail due to a proxy, you can run locally:
    Rscript src/r/titanic_main.R --mode all --data_dir src/data

   ```

3. **Place data files**
   ```
   src/data/
   ├── train.csv
   └── test.csv
   ```

4. **Run model training and summary**
   ```bash
   python src/app/main.py --mode check
   python src/app/main.py --mode summary
   ```

---

### Option 2: Run Using Docker

1. **Build the Docker image**
   ```bash
   docker build -t titanic-env -f Dockerfile .
   ```

2. **Run the container**
   ```bash
   docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-env \
   python -m app.main --mode all --data_dir /data
   ```

This command mounts your local `src/data/` folder into the container and executes all model steps inside the isolated Docker environment.

---

## How to Run — R Environment

### Step 1. Build the R Docker Image
```bash
docker build -f src/r/Dockerfile -t titanic-r:dev src/r
```

### Step 2. Run the R Container
```bash
docker run --rm -v "$(pwd)/src/data:/data:ro" titanic-r:dev \
Rscript /app/titanic_main.R --mode all --data_dir /data
```

This will:
- Install required R packages (using `install_packages.R`)
- Load and explore the dataset
- Train a logistic regression model
- Output accuracy metrics and summaries to the terminal

---

## Included R Packages

Installed automatically from `install_packages.R`:
```r
install.packages(c("readr", "dplyr", "tidyr", "stringr", "caret", "e1071"))
```

---

## Expected Output

Both Python and R environments print detailed progress logs, including:
- Data loading confirmation
- Cleaning or preprocessing steps
- Logistic regression training summary
- Accuracy scores for training and test sets

Example terminal output snippet:
```
Training set accuracy: 0.83
Test set accuracy: 0.79
Model coefficients printed successfully.
```

---

## Grading Notes (Important)

The grader can:
1. Clone this repository:
   ```bash
   git clone https://github.com/xiangyiLiu1126/titanic-disaster.git
   cd titanic-disaster
   ```
2. Download `train.csv` and `test.csv` from Kaggle:
   https://www.kaggle.com/competitions/titanic/data  
   Place both in `src/data/`.

3. Follow **either**:
   - Local Python setup  
   - Dockerized Python environment  
   - R Docker environment  

All configurations produce consistent results.  
No code editing or dependency installation is needed beyond the steps listed above.

---

## Summary

This repository provides a complete, reproducible environment for Titanic survival prediction analysis.  
Both Python and R pipelines are containerized, verified, and ready for grading — ensuring the project runs consistently across systems.

---

