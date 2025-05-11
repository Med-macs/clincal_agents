### To Run

`.env` with GOOGLE_API_KEY in root folder

Remove conflicting packages from the Kaggle base environment.

```

pip uninstall -qqy kfp jupyterlab libpysal thinc spacy fastai ydata-profiling google-cloud-bigquery google-generativeai
```
Install langgraph and the packages used


```
pip install -qU 'langgraph==0.3.21' 'langchain-google-genai==2.1.2' 'langgraph-prebuilt==0.1.7'
```

```
uvicorn app.main:app --reload
```

