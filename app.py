from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/provider')
def provider():
    return render_template('provider.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')


#change app.run() to the following
app.run(debug=True)