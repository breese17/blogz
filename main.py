from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:blogz2@localhost:8889/blogz2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= '8an@8a$4m3'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titles = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id= db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, titles, body, owner):
        self.titles = titles
        self.body= body
        self.owner=owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs=db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username=username
        self.password= password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'list']
    if request.endpoint not in allowed_routes and 'username' not in session: 
        return redirect('/login')




@app.route ('/login', methods= ['POST', 'GET'])
def login():
    if request.method =='POST':
        username=request.form['username']
        password =request.form['password']
        user= User.query.filter_by (username=username).first()
        if user and user.password== password:
            session['username']= username
            flash("Logged in")
            user_page = '/user?id=' + str(user.id)
            return redirect (user_page)#create user page)
        else:
            flash("Password is incorrect or the user does not exist", 'error')

     
    return render_template('login.html')

@app.route ('/register', methods =['POST', 'GET'])
def register():
    if request.method =='POST':
        username=request.form['username']
        password =request.form['password']
        verify = request.form['verify']
        #validate password
        existing_user= User.query.filter_by (username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']= username
            user_page = '/user?id=' + str(new_user.id) 
            return redirect (user_page)
            
        else: 
            flash("You already have an account, please login", 'error')
            return redirect ('/login') 


    return render_template('register.html')

@app.route ('/logout')
def logout():
    del session['username']
    return redirect ('/blog')

@app.route ('/')
def reg_user():
    user_list = User.query.all()
    return render_template('display_users.html', user_list=user_list)

@app.route('/newpost', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        new_entry_title = request.form['titles']
        new_entry_body = request.form['body']
        owner=User.query.filter_by(username=session['username']).first()
        new_entry = Blog(new_entry_title, new_entry_body, owner)
        db.session.add(new_entry)
        db.session.commit()
        new_blog = '/new?id=' + str(new_entry.id)
        return redirect (new_blog)

    else:
        return render_template('blog_entry.html', title= 'Add your blog below')        


@app.route('/blog')
def list():
    listing= Blog.query.all()
    
        
    return render_template('display_blogs.html', listing=listing)
    
       
@app.route('/new')
def single_post():
    entry_id = request.args.get('id')
    if (entry_id):
        entry = Blog.query.get(entry_id)
        
        return render_template('new_blog.html', title="Blog Entry", entry=entry)

@app.route('/user')
def single_user():
    entry_id = request.args.get('id')
    if (entry_id):
        user_account= User.query.get(entry_id)
        user_blogs=Blog.query.filter_by(owner=user_account)

        return render_template('user.html', title="Blog List", user_blogs=user_blogs, user_account=user_account)








if __name__ == '__main__':
    app.run()