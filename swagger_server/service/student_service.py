import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise EnvironmentError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client.school_db
students_collection = db.students
students_collection.create_index("student_id", unique=True)

def add(student=None):
    if student is None:
        return 'student data is required', 400

    last_student = students_collection.find_one(sort=[("student_id", -1)])
    next_student_id = 1 if last_student is None else last_student["student_id"] + 1

    student_dict = student.to_dict()
    student_dict["student_id"] = next_student_id

    try:
        result = students_collection.insert_one(student_dict)
    except DuplicateKeyError:
        return 'student ID already exists', 409

    # Convert ObjectId to string and return the student_id
    return next_student_id

def get_by_id(student_id=None, subject=None):
    if student_id is None:
        return 'student_id is required', 400

    student = students_collection.find_one({"student_id": student_id})
    if not student:
        return 'not found', 404

    student['_id'] = str(student['_id'])  # Convert ObjectId to string for JSON serialization
    return student

def delete(student_id=None):
    if student_id is None:
        return 'student_id is required', 400

    result = students_collection.delete_one({"student_id": student_id})
    if result.deleted_count == 0:
        return 'not found', 404
    return student_id
