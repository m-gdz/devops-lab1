import os
from pymongo import MongoClient, errors

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise EnvironmentError("MONGO_URI environment variable not set")

try:
    client = MongoClient(MONGO_URI)
    db = client.school_db
    students_collection = db.students
    students_collection.create_index("student_id", unique=True)
except errors.ConnectionFailure:
    raise Exception("Database connection failed. Unable to connect to MongoDB.")

def add(student=None):
    if student is None:
        return 'student data is required', 400

    try:
        last_student = students_collection.find_one(sort=[("student_id", -1)])
        next_student_id = 1 if last_student is None else last_student["student_id"] + 1

        student_dict = student.to_dict()
        student_dict["student_id"] = next_student_id

        try:
            result = students_collection.insert_one(student_dict)
        except errors.DuplicateKeyError:
            return 'student ID already exists', 409

        return next_student_id

    except (errors.ServerSelectionTimeoutError, errors.NetworkTimeout):
        return 'Database connection failed', 503

def get_by_id(student_id=None, subject=None):
    if student_id is None:
        return 'student_id is required', 400

    try:
        student = students_collection.find_one({"student_id": student_id})
        if not student:
            return 'not found', 404

        student['_id'] = str(student['_id'])
        return student

    except (errors.ServerSelectionTimeoutError, errors.NetworkTimeout):
        return 'Database connection failed', 503

def delete(student_id=None):
    if student_id is None:
        return 'student_id is required', 400

    try:
        result = students_collection.delete_one({"student_id": student_id})
        if result.deleted_count == 0:
            return 'not found', 404
        return student_id

    except (errors.ServerSelectionTimeoutError, errors.NetworkTimeout):
        return 'Database connection failed', 503
