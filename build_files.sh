#!/bin/bash
echo "BUILD START"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
#python3 -m nltk.downloader punkt averaged_perceptron_tagger stopwords wordnet
python3 manage.py collectstatic --noinput --clear
mkdir "public/static"
mv staticfiles public/static
echo "BUILD END"