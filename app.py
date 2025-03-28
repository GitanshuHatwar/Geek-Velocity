from flask import Flask , jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/flask_database'

db = SQLAlchemy(app)

class Task(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/tasks')
def get_task():
    task = Task.query.all()
    tasks_list = [
        {
            "id": task.id,
            "title": task.title,
            "done": task.done
        } for task in task
    ]
    return jsonify({"tasks": tasks_list})

if __name__ == '__main__':
    app.run(debug=True)
 