#!/usr/bin/env python3

from flask import Flask, request, render_template
import numpy as np
import matplotlib.pyplot as plt
from json import dumps
from sys import path
from imutils import paths
from html import escape

path.insert(0,'..')
path.append(CORRECT_PATH_OF_facebook_py)
from facebook import *

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/exhaust',methods = ['POST'])
def exhaust():
	name = request.form['username']
	print(name)
	impath=request.form['fileToUpload']
	print(impath)
	images = list(paths.list_images(impath))
	profile_link=validate_profile(name,images)
	return render_template("index.html",profurl=profile_link)

@app.route('/efficient',methods = ['POST'])
def efficient():
	email = request.form['Email']
	profs=get_links(email)
	return render_template("index.html",eprofurl=profs)

@app.route('/fbabout',methods = ['POST'])
def fbabout():
	fburl = request.form['fb']
	about=get_information(fburl)
	print(about)
	return escape(about).replace('\n','<br>').replace('\t','&emsp;&emsp;&emsp;')

if __name__ == '__main__':
	app.run(host='0.0.0.0',debug = True)