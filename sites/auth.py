from flask import render_template, request, flash, url_for, redirect, session, make_response
from werkzeug.security import check_password_hash

from utilities.global_vars import app, mongo

@app.route('/signout')
def signout():
    session.pop('email')
    flash("Successfully sign out. Waiting for your next visit!", "success")
    return render_template('auth.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == "GET":
        return render_template('auth.html')
    else:
        email = request.form['email']
        passwd = request.form['pass']

        query = mongo.db.users.find_one({"email": email})
        if query is not None and 'password' in query:
            hash_passwd = query['password']
            if check_password_hash(hash_passwd, passwd):
                # Generate new session ID
                # Note: Flask already handles one special session cookie per user and signs it cryptographically.
                # I. e., we just need to set the username of the current user in the session,
                # the other things (prevent from giving the same session to the users, encrypt the sessionID, store
                # the session on the server and so on) Flask will handle for us!
                session['email'] = email
                return redirect(url_for('feed'))

        # Else no match in database
        flash('Wrong e-mail or password!', 'warning')
        return render_template('auth.html')


