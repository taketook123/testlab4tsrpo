from labproject1 import app, db
from flask import Flask, request, jsonify
import uuid
from labproject1.serializers import UserSchema, CategorySchema, RecordSchema, UserCategorySchema
from labproject1.models import User, Category, Record, UserCategory
from flask_jwt_extended import JWTManager, jwt_required
from flask_jwt_extended import create_access_token, jwt_required, verify_jwt_in_request
from passlib.hash import pbkdf2_sha256
from datetime import datetime

jwt = JWTManager(app)

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/healthcheck')
def healthcheck_page():
    cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    response = {
        "status": "succes",
        "message": "Code of response: 200",
        "current_date": cur_date    
    }
    return jsonify(response)



# auth
@app.route('/user/auth', methods=['POST'])
def post_user():
    data = request.get_json()

    user_schema = UserSchema()
    try:
        user_name = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    new_user = User(name=user_name["name"], password=pbkdf2_sha256.hash(user_name["password"]))
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

    #print(new_user.id)

        user_data = {
                'id': new_user.id,
                'name': new_user.name,
            }
    
        return jsonify(user_data), 200

@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()

    user_schema = UserSchema()
    try:
        user_name = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    with app.app_context():
        user_to_login = User.query.filter_by(name=user_name["name"]).first()

        if user_to_login and pbkdf2_sha256.verify(user_name["password"], user_to_login.password):
            access_token = create_access_token(identity=user_to_login.id)
            return jsonify({"message": "succes login", "token": access_token}), 200
        else:
            return jsonify({"message": "unsucces login"}), 200



# need token
@app.route('/user/<int:user_id>', methods=['GET', 'DELETE'])
@jwt_required()
def delete_user(user_id):
    if request.method == "DELETE":
        with app.app_context():
            user_to_delete = User.query.filter_by(id=user_id).first()

            if user_to_delete:
                db.session.delete(user_to_delete)
                db.session.commit()
                db.session.close()
                return jsonify({'message': f'User {user_id} deleted'}), 200
            else:
                return jsonify({'error': f'User {user_id} not found'}), 404
    else:
        with app.app_context():
            user_to_show = User.query.filter_by(id=user_id).first()

            if user_to_show:
                user_data = {
                    'id': user_to_show.id,
                    'name': user_to_show.name
                }
                return jsonify(user_data), 200
            else:
                return jsonify({'error': f'User {user_id} not found'}), 404
        


@app.route('/users', methods=['GET'])
def get_users():
    res = {}
    with app.app_context():
        for i in User.query.all():
            res[i.id] = {"id": i.id, "name": i.name}
    return res


@app.route('/category', methods=['POST', 'GET'])
def getpost_category():
    if request.method == 'GET':
        res = {}
        with app.app_context():
            for i in Category.query.all():
                res[i.id] = {"id": i.id, "name": i.name}
        return res 
    else:
        # jwt_required
        jwt_claims = verify_jwt_in_request()

        if jwt_claims is None:
            return jsonify({'error': 'invalid token'}), 400
        else:
            data = request.get_json()
            cat_schema = CategorySchema()
            try:
                cat_name = cat_schema.load(data)
            except ValidationError as err:
                return jsonify({'error': err.messages}), 400

            new_cat = Category(name=cat_name["name"])
            with app.app_context():
                db.session.add(new_cat)
                db.session.commit()

                cat_data = {
                    "id": new_cat.id,
                    "name": new_cat.name
                }

                return jsonify(cat_data), 200

@app.route('/category/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_cat(cat_id):
    with app.app_context():
        cat_to_delete = Category.query.filter_by(id=cat_id).first()

        if cat_to_delete:
            db.session.delete(cat_to_delete)
            db.session.commit()
            db.session.close()
            return jsonify({'message': f'Category {cat_id} deleted'}), 200
        else:
            return jsonify({'error': f'Category {cat_id} not found'}), 404


@app.route('/records', methods=['GET'])
def get_all_records():
    res = {}
    with app.app_context():
        for i in Record.query.all():
            res[i.id] = {
                "id": i.id,
                "user_id": i.user_id,
                "cat_id": i.category_id,
                "sum": i.sum,
                "created_at": i.created_at
            }
    return res

@app.route('/record', methods=['GET'])
def get_by_id():
    data = request.get_json()

    if not data["user_id"] and not data["category_id"]:
        return jsonify({'error': 'any parametres are given'})

    need_records = []
    if data["user_id"]:
        if data["category_id"]:
            need_records = Record.query.filter_by(user_id=data["user_id"], category_id=data["category_id"])
        else:
            need_records = Record.query.filter_by(user_id=data["user_id"])

    else:
        need_records = Record.query.filter_by(category_id=data["category_id"])

    res = {}
    for i in need_records:
        res[i.id] = {
                "id": i.id,
                "user_id": i.user_id,
                "cat_id": i.category_id,
                "sum": i.sum,
                "created_at": i.created_at
            }
    return res


# need token
@app.route('/record', methods=['POST'])
@jwt_required()
def get_records():
    jwt_claims = verify_jwt_in_request()

    data = request.get_json()
    record_schema = RecordSchema()
    try:
        record_data = record_schema.load(data)
    except Exception as err:
        return jsonify({'error': 'some errors in form'}), 400

    
    new_record = Record(user_id=jwt_claims[1]["sub"], category_id=record_data['category_id'], sum=record_data['sum'])
    with app.app_context():
        db.session.add(new_record)
        db.session.commit()

        record_data = {
            "id": new_record.id,
            "user_id": new_record.user_id,
            "cat_id": new_record.category_id,
            "sum": new_record.sum
        }

        return jsonify(record_data), 200

# token need
@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def work_record(record_id):
    if request.method == "GET":
        with app.app_context():
            record_show = Record.query.filter_by(id=record_id).first()

            if record_show:
                rec_data = {
                    "id": record_show.id,
                    "cat_id": record_show.category_id,
                    "user_id": record_show.user_id,
                    "sum": record_show.sum,
                    "created_at": record_show.created_at
                }
            
                return jsonify(rec_data), 200
            else:
                return jsonify({"message": f"Record {record_show.id} not found"}), 404
    else:
        #jwt required
        jwt_claims = verify_jwt_in_request()

        if jwt_claims is None:
            return jsonify({'error': 'invalid token'}), 401
        else:

            with app.app_context():
                record_delete = Record.query.filter_by(id=record_id).first()

                if record_delete:
                    db.session.delete(record_delete)
                    db.session.commit()
                    db.session.close()
                    return jsonify({'message': f'Record {record_id} deleted'}), 200
                else:
                    return jsonify({'error': f'Record {record_id} not found'}), 404



@app.route('/usercategories', methods=['GET'])
def get_ucat():
    with app.app_context():
        res = {}
        ucats = UserCategory.query.filter_by(is_public=True)
        for i in ucats:
            res[i.id] = {
                "name": i.name,
                "user_id": i.user_id
            }
        
        return res



# jwt_required()
@app.route('/usercategory/<int:user_id>', methods=['GET'])
def get_user_ucat(user_id):
    jwt_claims = verify_jwt_in_request()

    if jwt_claims is None:
        return jsonify({'error': 'invalid token'}), 401
    else:
        if jwt_claims[1]["sub"] == user_id:
        #print(jwt_claims[1]["sub"])
            with app.app_context():
                res = {}
                ucats = UserCategory.query.filter_by(user_id=user_id)
                for i in ucats:
                    res[i.id] = {
                        "name": i.name,
                        "user_id": i.user_id,
                        "is_public": i.is_public
                    }
                
                return res
        else:
            return jsonify({'error':f'You cannot get user {user_id} categories'}), 400



@app.route('/usercategory/<int:user_id>/<int:ucat_id>', methods=['DELETE'])
@jwt_required()
def del_id_ucat(user_id, ucat_id):
    jwt_claims = verify_jwt_in_request()

    if jwt_claims[1]["sub"] == user_id:
        with app.app_context():
            del_ucat = UserCategory.query.filter_by(id=ucat_id, user_id=user_id).first()

            if del_ucat:
                db.session.delete(del_ucat)
                db.session.commit()
                db.session.close()
                return jsonify({'mesage': f'User Category {del_ucat.id} deleted'}), 200
            else:
                return jsonify({'error': f'User Category {del_ucat.id} not found'}), 404
    else:
        return jsonify({'error':f'You cannot delete user {user_id} categories'}), 400
        



@app.route('/usercategory', methods=['POST'])
@jwt_required()
def post_ucat():
    jwt_claims = verify_jwt_in_request()

    if jwt_claims is None:
        return jsonify({'error': 'invalid token'}), 401
    else:
        data = request.get_json()
        
        ucat_schema = UserCategorySchema()
        try:
            ucat_data = ucat_schema.load(data)
        except Exception as err:
            return jsonify({"error": "bad input"}), 405


        new_ucategory = UserCategory(name=data["name"], user_id=jwt_claims[1]["sub"], is_public=data["is_public"])

        with app.app_context():
            db.session.add(new_ucategory)
            db.session.commit()

            record_data = {
                "id": new_ucategory.id,
                "user_id": new_ucategory.user_id,
                "is_public": new_ucategory.is_public
            }

