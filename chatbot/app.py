import os
from flask import Flask, render_template, request, redirect, url_for, g
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_gtts import gtts
#wtf forms
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
#chatterbot
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement
#werkuzeug
from werkzeug.security import generate_password_hash, check_password_hash
import re
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thissecret'
gtts(app)

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))

english_bot = ChatBot("Chatterbot",
	storage_adapter='chatterbot.storage.SQLStorageAdapter',

    logic_adapters=[
    		"chatterbot.logic.BestMatch",
            
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter',
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            
            'input_text': 'Help me!',

            'output_text': 'Ok, here is a link: http://chatterbot.rtfd.org'
        },
         {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90
        }

    ],
   database='./db.sqlite3',
	trainer='chatterbot.trainers.ListTrainer')	

for knowledeg in os.listdir('base'):
	BotMemory = open('base/'+ knowledeg, 'r', encoding="utf8").readlines()

 
english_bot.set_trainer(ChatterBotCorpusTrainer)
# english_bot.train("chatterbot.corpus.english")

english_bot.set_trainer(ListTrainer)




new_bot = ChatBot("Chatterbotbot")
# english_bot.train(BotMemory)
# logic_adapters=[
 
#         {
#         	'import_path' : 'chatterbot.logic.LowConfidenceAdapter'
#         	# 'threshold' : 0.50,
#         	# 'default_response' : 'I am sorry, but I do not understand.'
#         }

#     ]

      	# {'import_path' : 'chatterbot.logic.MathematicalEvaluation'},
        # {'import_path' : 'chatterbot.logic.TimeLogicAdapter'},
        # {'import_path' : 'chatterbot.logic.UnitConversion'},




@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#login
class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('remember me')

#register
class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

#trainer
class TrainForm(FlaskForm):
	possQuestion = StringField('possQuestion', validators=[InputRequired(), Length(min=4, max=2500)], render_kw={"placeholder": "Please Enter Training Data"})
	possReponse = StringField('possReponse', validators=[InputRequired(), Length(min=4, max=2500)], render_kw={"placeholder": "Please Enter Training Response"})

#start of conversation
class StartConv(FlaskForm):
	startPhrase = StringField('startPhrase', validators=[InputRequired(), Length(min=4, max=2500)], render_kw={"placeholder": "Please Enter the starting phrase"})

#end conversation
class EndConv(FlaskForm):
	endPhrase = StringField('endPhrase', validators=[InputRequired(), Length(min=4, max=2500)], render_kw={"placeholder": "Please Enter the ending phrase"})

#homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/services')
def services():
	return render_template('services.html')

# @app.route('/chat')
# def chat():
# 	return render_template('chat.html')	

@app.route('/contact')
def contact():
	return render_template('contact.html')	

#login function
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h1>Invalid User details</h1>'
		#return '<h1>' + form.username.data + '  ' +  form.password.data +'</h1>'

	return render_template('login.html', form=form)


#sign up function
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username = form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(new_user)
		db.session.commit()

		return '<h1>New user has been created</h1>'
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

	return render_template('signup.html', form=form)

#
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
	
	
	
	return render_template('chat.html',startMessage="test", name=current_user.username)



#
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	
	form2 = StartConv(request.form, prefix="form2")
	form3 = EndConv(request.form, prefix="form3")
	form = TrainForm()
	
	g.x = form2.startPhrase.data
	if form.validate_on_submit():
		while True:
			input_statement = Statement(form.possQuestion.data)

			correct_response = Statement(form.possReponse.data)
			english_bot.learn_response(correct_response, input_statement)
			
		
	
	if form2.validate_on_submit():
		x = form2.startPhrase.data

	if form3.validate_on_submit():
		y = form3.endPhrase.data
			
	return render_template('dashboard.html', x= form2.startPhrase.data, y = form3.endPhrase.data, name=current_user.username, form=form, form2=form2, form3=form3)

#chatbotresponse
@app.route("/get")
def get_bot_response():

	dashboard()
	userText = request.args.get('msg')
	output =  str(english_bot.get_response(userText))
	if "bye" in userText.strip():
		output = "Thanks for contacting us, good bye"
	
	if "google" in userText.strip():
		search= userText.split("google")[1]
		google= "http://www.google.co.uk/search?q="
		
		search_result = google + search	
		output = '<i>Sorry that I could not help but heres a google solution:</i> <a href="'+search_result+'">'+search_result+'</a>'


	return output

#newchatbot
def get_newbot_response():
    userText = request.args.get('msg')
    return str(new_bot.get_response(userText))

#chatlearn
# @app.route('/dashboard', methods=['GET', 'POST'])
# def get_learn_response():
# 	form = TrainForm() 

# 	return render_template('dashboard', form=form)
# 	if form.validate_on_submit():
#     		userText = form.possReponse

# return render_template('dashboard', form=form)
    # trainedResponse = request.args.get('trained')	

    # input_statement = Statement(userText)
    # correct_response = 


    # bot.learn_response(correct_response, input_statement)
    # return str(english_bot.get_response(userText))


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))


#launch app
if __name__ == "__main__":
    app.run(debug=True)
