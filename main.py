import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from instagrapi import Client

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to log in to Instagram
def instagram_login(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        return cl
    except Exception as e:
        return str(e)

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        choice = request.form['choice']
        haters_name = request.form['haters_name']
        delay = int(request.form['delay'])

        # Handle file upload
        if 'message_file' not in request.files:
            flash("No file uploaded!")
            return redirect(request.url)
        file = request.files['message_file']
        if file.filename == '':
            flash("No selected file!")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read messages from file
        try:
            with open(filepath, 'r') as f:
                messages = [line.strip() for line in f.readlines()]
        except Exception as e:
            flash(f"Error reading message file: {e}")
            return redirect(request.url)

        # Login to Instagram
        cl = instagram_login(username, password)
        if isinstance(cl, str):  # If login failed
            flash(f"Login failed: {cl}")
            return redirect(request.url)

        # Messaging logic with looping
        if choice == 'inbox':
            target_username = request.form['target_username']
            try:
                user_id = cl.user_id_from_username(target_username)
                while True:  # Infinite loop
                    for message in messages:
                        full_message = f"{haters_name} {message}"
                        cl.direct_send(full_message, [user_id])
                        time.sleep(delay)
                flash("Messages sent successfully to inbox!")
            except Exception as e:
                flash(f"Error sending messages: {e}")
        elif choice == 'group':
            thread_id = request.form['thread_id']
            try:
                while True:  # Infinite loop
                    for message in messages:
                        full_message = f"{haters_name} {message}"
                        cl.direct_send(full_message, thread_ids=[thread_id])
                        time.sleep(delay)
                flash("Messages sent successfully to group!")
            except Exception as e:
                flash(f"Error sending messages to group: {e}")
        else:
            flash("Invalid choice!")
        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
