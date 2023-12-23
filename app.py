from flask import Flask, render_template, request

app = Flask(__name__, template_folder='static/html', static_folder='static')

@app.route('/resume')
def resume_page():
    # 我的html路径为static\html\index.html
    return render_template('resume_index.html')

@app.route('/')
def homepage():
    # 我的html路径为static\html\index.html
    return render_template('home_index.html')

@app.route('/passages')
def passages_page():
    # 我的html路径为static\html\index.html
    return render_template('passages_index.html')

@app.route('/others')
def others_page():
    # 我的html路径为static\html\index.html
    return render_template('others_index.html')

if __name__ == '__main__':
    app.run(port=5000)
