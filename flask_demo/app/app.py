#初始化，创建一个程序实例，程序实例是Flask类的对象
from flask import Flask,render_template,session,redirect,url_for,flash
from flask import request
from threading import Thread
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Shell
import os
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
class NameForm(Form):
    name=StringField('What is your name?',validators=[Required()])
    submit=SubmitField('Submit')

#from flask_script import Manager
#需要传入__name__，作用是为了确定资源所在的路径
basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
manager=Manager(app)
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)
bootstrap=Bootstrap(app)
moment=Moment(app)
app.config['SECRET_KEY']='hard to guess string'
app.config['MAIL_SERVER']='smtp.163.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX']='[Flasky]'
app.config['FLASKY_MAIL_SENDER']='Flasky Admin <flasky@example.com>'
app.config['FLASKY_ADMIN']=os.environ.get('FLASKY_ADMIN')
def send_email(to,subject,template,**kwargs):
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)
class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
# 定义路由及视图函数
#通过装饰器实现的
@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user=User(username=form.name.data)
            db.session.add(user)
            session['known']=False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','main/new_user',user=user)
        else:
            session['known']=True
        session['name']=form.name.data
        form.name.data=''
        return redirect((url_for('index')))
    #user_agent=request.headers.get('User-Agent')
    #return '<p>Your browser is %s</p>'% user_agent#返回响应可以有三个参数第二
#个是状态码，第三个是由首部组成的字典
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))
@app.route('/user/<name>')
def user(name):
    #return '<h1>Hello,%s!</h1>'% name
    return render_template('user.html', name=name)
@app.errorhandler(404)
def page_not_fonud(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def page_not_fonud(e):
    return render_template('500.html'), 500

#为shell命令添加一个上下文
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))
#启动程序

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

if __name__ == '__main__':
    manager.run()

