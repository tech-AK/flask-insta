import datetime
import os

from bson import ObjectId
from flask import render_template, session, redirect, url_for, abort, request

import config
from utilities.global_vars import app, mongo
from utilities.image_upload import handleImageUpload
from utilities.login import login_required


class Post:
    def __init__(self, name, author_profile_pic, time, text, pic):
        self.name = name
        self.author_profile_pic = author_profile_pic
        self.time = time
        self.text = text
        self.pic = pic

@app.route('/delete/<string:id>', methods=['DELETE'])
@login_required
def delete(id):
    post = mongo.db.posts.find_one({"_id": ObjectId(id)})

    if 'email' in post:
        if post['email'] == session['email']:
            # user can delete it as it is his own post
            if post['pic']:
                # delete picture first
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post['pic']))
                # then delete database entry
                mongo.db.posts.delete_one({"_id": ObjectId(id)})
    return redirect(location=url_for('feed'))

@app.route('/feed', methods=['GET', 'POST'])
def feed():
    if request.method == "GET":
        #this find query matches every entries and gives the last posts to the user
        posts = mongo.db.posts.find({}).sort("time",-1).limit(config.NUMBER_OF_SHOWN_POSTS)

        email = ""
        if 'email' in session:
            email = session['email']

        #data = mongo.db.users.find_one({"email": session['email']})
        return render_template('feed.html', posts=posts, email=email)

    else:
        text = request.form['text']

        # Check if with image file is everything okay and process image file
        img_filename = handleImageUpload(request=request, img_required=False)

        #Get user data
        if 'email' not in session:
            abort(401)

        email = session['email']
        userdata = mongo.db.users.find_one({"email": email})

        mongo.db.posts.insert_one({"name": userdata['fullname'], "email": email, "author_profile_pic": userdata['pic_file_name'], "time": datetime.datetime.now(), "display_time": datetime.datetime.now().strftime('%d.%m.%Y %H:%M'), "text": text, "pic": img_filename})


        return redirect(url_for('feed'))