# Will my Deutsche Bahn arrive on time?
UniTartu Machine Learning project "Will my Deutsche Bahn arrive on time?"

Based on the `deutsche-bahn-db-delays` Kaggle dataset available [here](http://www.kaggle.com/datasets/nokkyu/deutsche-bahn-db-delays/).

# Repository Structure
At the end of the project, the repository was restructured.
## `data/` - files related to data exploration and preprocessing
- `lines/` - code and data for fixing the line mapping for the dataset:
	- `correct_line_mapping.csv` - correct line mapping.
	- `mapping.ipynb` - a notebook file for creating `correct_line_mapping.csv`.
- `data_cleanup_and_qna.ipynb` - one part of the file for cleaning up and answering questions about the data.
- `data_description.md` - the data description copied from [Kaggle](http://www.kaggle.com/datasets/nokkyu/deutsche-bahn-db-delays/).
- `data_exploration.md` - one part of the file for data exploration.
- `data_questions.md` - a set of questions about the data to better direct data exploration.
- `put_connections_here.txt` - a file with instructions and a link to Google Drive that contains `connections_v3.csv`, the final dataset used for modelling. 
- `put_DBtrainlines_here.txt` - a file with instructions for downloading the dataset from [Kaggle](http://www.kaggle.com/datasets/nokkyu/deutsche-bahn-db-delays/).
- `train_line_reconstruction_example.ipynb` - an example of train line reconstruction -- cross-matching all the stops on a line to append the data from all stops to all the other stops.
- `train_line_reconstruction.ipynb` - notebook to apply to `DBtrainlines.csv` to get `connections_v3.csv`. Fixes line numbering and cross-matches the various stops on a line.

## `modelling/`
- `model_selection.ipynb` - initial exploration and thoughts for selecting a model for this task.
- `model_training.ipynb` - previously named `gradient_boost.py`; the code for training the XGBoost models. Outputs `model{t}.json`, where `t` is the target prediction threshold.

## `web-application/`
- `backend/` - backend for the web application, including but not limited to:
	- `services/model_client.py` - loading the model from files.
	- `services/lookup.py` - looking up data about the lines.
	- `services/model{5,10,15,20,25,30}.json` - model files used for prediction.
	- `API.md` - a description for the backend API.
	- `app.py` - initializes a Python Flask server for predictions.
- `frontend/` - frontend web application code for visual interaction with the model, including but not limited to:
	- `index.html` - simple locally hosted website to interact with the model.
- `README.md` - initial requirements for the back- and frontend.

## Other files
- `environment.yml` - a base file for creating a Conda environment.
- `Intermediate Scoping Notes.md` - a notes file used for deciding the scope and direction of the project after data processing.
- `LICENSE` - an MIT license.
- `README.md` - the file you're reading right now.



---

# Quick Start Guide
0. Make sure that you have the following: [Python](https://www.python.org/downloads/), [(mini)conda](https://www.anaconda.com/docs/getting-started/miniconda/install), [Visual Studio Code](https://code.visualstudio.com/download), [Git](https://git-scm.com/downloads).
1. Download the Deutsche Bahn dataset into `data/DBtrainrides.csv`. This should be possible using [this download link](https://www.kaggle.com/api/v1/datasets/download/nokkyu/deutsche-bahn-db-delays). Alternatively, here's a `curl` script that downloads it into `USER/Downloads`:
```bash
curl -L -o ~/Downloads/deutsche-bahn-db-delays.zip\
  https://www.kaggle.com/api/v1/datasets/download/nokkyu/deutsche-bahn-db-delays
```
2. Create the work environment based on the section [Work Environment](#work-environment).

**On Windows**: Ensure that you have Git Bash, which comes with [Git](https://git-scm.com/downloads). Change Visual Studio Code terminal to Git Bash. Should be doable using [this simple guide](https://stackoverflow.com/questions/44435697/change-the-default-terminal-in-visual-studio-code).

# Work Environment
We will use a (mini)conda enviroment.

There are 2 options for creating the virtual environment:

## Option 1: let VSCode handle it (recommended)
When you've opened this folder in Visual Studio Code, it will likely ask you to choose your Python environment. If not, then:

1. Press `Ctrl+Shift+P` or type `>` into the search in the top bar.
2. Type `Create Environment`, choose `Python: Create Environment`.
3. Choose `conda`.
4. Choose the latest Python version (mine was `3.11`).
5. VSCode will create a `.conda` path that will not be synced to GitHub. 
6. Try running a terminal (in the top bar, choose Terminal -> New Terminal or command `> Terminal: Create New Terminal`). If it shows an error, close VSCode and open it again in this folder. It should show a warning about inheriting `conda` environments -- press `Allow`.

## Option 2: create it manually
To create it (needs to only be done once), run
```bash
conda env create -f environment.yaml
```

Then, **every time that the terminal is used**, make sure that `conda` is using the correct enviroment:
```bash
conda activate ml-db-delays
```

Additionally, you need to check that Jupyter inside VSCode is using the `ml-db-delays` kernel.