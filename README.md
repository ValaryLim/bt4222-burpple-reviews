# Burpple+

This project aims to use text mining and machine learning methods to provide a better rating and aggregation system on food review websites, so that users can better decide where to dine at. The scope of this project includes: (1) building and applying aspect-based sentiment analysis on textual reviews; (2) providing overall and aspect-based ratings for restaurants; and (3) devising a scoring system that weighs reviews by recency. We scrapped data from the [Burpple food reviews site](https://www.burpple.com/sg) for our project, and our final application can be accessed from this [link](https://burpple-plus.herokuapp.com).

Our project pipeline is as follows:

[![project-pipeline.png](https://i.postimg.cc/661jSCWN/project-pipeline.png)](https://postimg.cc/CdksnBnv)

## Getting Started
This project uses Python 3.8 and Jupyter Notebook. Upon cloning this repository into your local machine, run the following command to install all relevant packages.
```bash
pip install -r requirements.txt
```

## Files
Our project pipeline (from scraping to scoring) can be triggered by calling ```python main.py``` in the root directory. The following table contains a brief description of the other files and folders.
| Folder / File | Description |
| - | - |
| **data_analysis.ipynb** | A sample notebook showing how our aspect-based sentiment analysis data can be used for downstream applications to analyse restaurant performance. |
| **scraping** | Folder containing code and scripts to trigger data scraping from the Burpple website. |
| **rules** | Folder containing `rule_mining.ipynb`, used to test rules for aspect identification. | 
| **modelling** | Folder containing jupyter notebooks used for topic modelling, aspect identification, sentiment analysis (VADER, LR, SVM, NB, RF, BERT, FastText, Stacking) and model explainability (LIME). |
| **utils** | Folder containing python files for preprocessing, postprocessing, rule mining and scoring used in our final pipeline. |
| **dashboard** | Folder containing code used to build our final application on Python Dash. |


## Application Demo


## Built With


## Authors
- Aw Xin Min - [Github](https://github.com/awxinmin)
- Lai Yan Jean -  [Github](https://github.com/laiyanjean)
- Lee Jun Hui Sean - [Github](https://github.com/seansljh)
- Risa Lim Ning - [Github](https://github.com/risalim)
- Valary Lim Wan Qian - [Github](https://github.com/ValaryLim)
