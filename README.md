# ml-deutsche-bahn-delays
UniTartu Machine Learning project "Will my Deutsche Bahn arrive on time?"

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
6. Try running a terminal (in the top bar, choose Terminal -> New Terminal or command `> Terminal: Create New Terminal`). If it shows an error, close VSCode and open it again in this folder. It should show a warning about inheriting `conda` environments -- press `Allow`. Alternatively, if it doesn't work... Let us know :P

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