#初始化，创建一个程序实例，程序实例是Flask类的对象
from flask import Flask,render_template
from flask import request
from flask_bootstrap import Bootstrap
#from flask_script import Manager
#需要传入__name__，作用是为了确定资源所在的路径
app = Flask(__name__)
#manager=Manager(app)
bootstrap=Bootstrap(app)
# 定义路由及视图函数
#通过装饰器实现的
@app.route('/')
def index():
    #user_agent=request.headers.get('User-Agent')
    #return '<p>Your browser is %s</p>'% user_agent#返回响应可以有三个参数第二
#个是状态码，第三个是由首部组成的字典
    return render_template('index.html')
@app.route('/user/<name>')
def user(name):
    #return '<h1>Hello,%s!</h1>'% name
    return render_template('user.html', name=name)
#启动程序
if __name__ == '__main__':
    #manager.run()
    app.run(debug=True)
