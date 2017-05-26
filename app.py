import os
import os.path as op
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.actions import action
from flask_admin.contrib import sqla


# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

STATUS_MAPPER = [
    (0, 'todo'),
    (1, '完成'),
]


class JobList(db.Model):
    __tablename__ = 'job_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, default='0')

    def __str__(self):
        return self.title


class TodoList(db.Model):
    __tablename__ = 'todo_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, default='0')

    def __str__(self):
        return self.title


# Flask views
@app.route('/')
def index():
    return redirect('/admin')


# Customized User model admin
class PostAdmin(sqla.ModelView):
    can_create = can_edit = can_delete = False

    column_list = ('id', 'title', 'text', 'status')
    column_choices = {
        'status': STATUS_MAPPER,
    }


class SuperPostAdmin(PostAdmin):
    can_create = can_edit = True

    column_list = ('title', 'text')
    column_choices = {}

    def get_query(self):
        return super(PostAdmin, self).get_query().filter(self.model.status == 0)

    @action('done', '完成')
    def action_done(self, ids):
        rs = self.model.query.filter(self.model.id.in_(map(int, ids))).all() 
        for x in rs:
            x.status = 1
        db.session.commit()


# Create admin
admin = Admin(app, name='job-list', template_mode='bootstrap3')

# Add views
admin.add_view(SuperPostAdmin(JobList, db.session, name='工作任务表', endpoint='job_list'))
admin.add_view(SuperPostAdmin(TodoList, db.session, name='个人计划表', endpoint='todo_list'))

category = '历史'
admin.add_view(PostAdmin(JobList, db.session, name='工作任务表', category=category))
admin.add_view(PostAdmin(TodoList, db.session, name='个人计划表', category=category))

if __name__ == '__main__':
    db.create_all()
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])

    # Start app
    app.run(port=8000, debug=True)

