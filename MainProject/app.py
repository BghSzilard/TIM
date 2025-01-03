from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os;
import pandas as pd;
import json

app = Flask(__name__)
data_file = 'D:\\Master\\TIM\\DawProject\\users.xlsx'

saved_announcements = []

@app.route('/save-announcement/<int:announcement_id>', methods=['POST'])
def save_announcement(announcement_id):
    global saved_announcements  # Use the global variable

    if announcement_id not in saved_announcements:
        saved_announcements.append(announcement_id)

    return redirect(url_for('announcements'))


def getData():
    df = pd.read_excel(data_file)
    return df

def email_exists(email):
    df = getData()
    if df.empty:
        return False
    return email in df['email'].values


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email, password = data['email'], data['password']
    
    if email_exists(email):
         return jsonify({"status": "error", "message": "Email already registered"})

    # Append new user to the Excel file
    new_user = pd.DataFrame([[email, password]], columns=['email', 'password'])
    if os.path.exists(data_file):
        df = pd.read_excel(data_file)
        df = df._append(new_user, ignore_index=True)
    else:
        df = new_user
    df.to_excel(data_file, index=False)

    return jsonify({"status": "success", "message": "User registered successfully"})

def get_password_for_email(email):
    df = pd.read_excel(data_file)

    # Find the row with the given email and return the corresponding password
    user_row = df[df['email'] == email]
    if not user_row.empty:
        return user_row.iloc[0]['password']
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def goToRegister():
    return render_template('register.html')

@app.route('/announcements', methods=['GET', 'POST'])
def goToAnnouncements():
    # Read the filter options from the form submission
    category_filter = request.args.get('categorySelect')
    type_filter = request.args.get('typeSelect')
    price_range_filter = request.args.get('priceRange')

    # Load announcements data from JSON
    with open('D:\\Master\\TIM\\DawProject\\announcements.json') as file:
        all_announcements = json.load(file)

    # Filter the announcements based on the filter options provided
    filtered_announcements = all_announcements
    if category_filter:
        filtered_announcements = [ann for ann in filtered_announcements if ann['real_estate']['category'].lower() == category_filter.lower()]
    if type_filter:
        filtered_announcements = [ann for ann in filtered_announcements if ann['type'].lower() == type_filter.lower()]
    if price_range_filter:
        # Assuming price_range_filter is a string like "100000-200000"
        low_price, high_price = map(int, price_range_filter.split('-'))
        filtered_announcements = [ann for ann in filtered_announcements if low_price <= ann['price'] <= high_price]

    return render_template('announcements.html', announcements=filtered_announcements)

@app.route('/login')
def goToLogin():
    if 'logged_in' in session:
        return redirect(url_for('my_account'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            if get_password_for_email(email) == password:
                session['logged_in'] = True
                return redirect(url_for('my_account'))
            else:
                return 'Login Failed'
        else:
            return 'Missing email or password'
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    global saved_announcements
    saved_announcements = []
    return redirect(url_for('login'))

@app.route('/my-account', methods=['GET', 'POST'])
def my_account():
    global saved_announcements  # Use the global variable

    with open('D:\\Master\\TIM\\DawProject\\announcements.json') as file:
        all_announcements = json.load(file)

    saved_announcements_data = []

    for announcement_id in saved_announcements:
        announcement = next((ann for ann in all_announcements if ann['id'] == announcement_id), None)
        if announcement:
            saved_announcements_data.append(announcement)

    return render_template('myAccount.html', saved_announcements=saved_announcements_data)


@app.route('/save', methods=['POST'])
def save_text():
    data = request.json
    file_path = os.path.join('C:/Users/sziba/Desktop/DawProject', 'user_input.txt')
    with open(file_path, 'w') as file:
        file.write(data['text'])
    return jsonify({"status": "success"})

@app.route('/announcements')
def announcements():
    with open('path/to/announcements.json') as file:
        announcements = json.load(file)
    return render_template('announcements.html', announcements=announcements)

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'

    app.run(debug=True, port=8080)