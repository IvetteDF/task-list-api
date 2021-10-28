from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        
        if sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        elif sort_query == "asc":
            tasks = Task.query.order_by(Task.title.asc())            
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : task.is_complete
            })
        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if title is None or description is None:
            return jsonify({"details" : "Invalid data"}), 400

        try: 
            completed_at = request_body["completed_at"]
        except KeyError:
            return jsonify({"details" : "Invalid data"}), 400

        new_task = Task(title=title, description=description, completed_at=completed_at)

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"task" : {
            "id" : new_task.task_id,
            "title" : new_task.title,
            "description" : new_task.description,
            "is_complete" : new_task.is_complete
        }}), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404
    
    if request.method == "GET":
        return {"task" : {
            "id" : task.task_id,
            "title" : task.title,
            "description" : task.description,
            "is_complete" : task.is_complete
        }}
    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]

        db.session.commit()

        return jsonify({"task" : {
            "id" : task.task_id,
            "title" : task.title,
            "description" : task.description,
            "is_complete" : task.is_complete
        }}), 200
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"details" : f'Task {task.task_id} "{task.title}" successfully deleted'})
