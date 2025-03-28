from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/Flask_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):  # ✅ Corrected 'Model' capitalization
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/tasks')
def get_task():
    tasks = Task.query.all()  # ✅ Renamed 'task' to 'tasks'
    tasks_list = [
        {
            "id": t.id,
            "title": t.title,
            "done": t.done
        } for t in tasks  # ✅ Fixed iteration
    ]
    return jsonify({"tasks": tasks_list})

if __name__ == '__main__':
    app.run(debug=True)
