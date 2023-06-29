from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Loop through each column in the data record
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def random_cafe():
    cafes_data = db.session.query(Cafe).all()
    cafe = random.choice(cafes_data)
    data = {
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        }
    return jsonify(cafe=data)


@app.route("/all", methods=['GET'])
def all_data():
    data = []
    cafes_data = db.session.query(Cafe).all()
    for cafe in cafes_data:
        data.append(cafe.to_dict())
    return jsonify(cafe=data)


@app.route("/search", methods=['GET'])
def search():
    location = request.args.get('loc', None)
    response = db.session.execute(db.select(Cafe).filter_by(location=location)).scalars()
    print(response)
    data = {}
    for cafe in response:
        print(type(cafe))
        data[cafe.id] = cafe.to_dict()
    if len(data) == 0:
        data = {"Not found": "Sorry, we dont have a cafe at that location."}
        return jsonify(error=data)
    else:
        return jsonify(cafe=data)


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add():
    if request.method == 'POST':
        data = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    seats=request.form.get('seats'),
                    has_toilet=eval(request.form.get('has_toilet').lower().title()),
                    has_wifi=eval(request.form.get('has_wifi').lower().title()),
                    has_sockets=eval(request.form.get('has_sockets').lower().title()),
                    can_take_calls=eval(request.form.get('can_take_calls').lower().title()),
                    coffee_price=request.form.get('coffee_price')
                    )
        db.session.add(data)
        db.session.commit()
        return jsonify(response={"Success": "Successfully added the new cafe."})



## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    if request.method == 'PATCH':
        price_update = request.args.get('new_price', None)
        try:
            data = Cafe.query.get(cafe_id)
            data.coffee_price = f"{price_update}"
        except AttributeError:
            status = {"Not found": "Sorry, cafe with that id was not found in the database."}
        else:
            db.session.commit()
            status = {"Success": "Successfully added the new cafe."}
        finally:
            return jsonify(response=status)


## HTTP DELETE - Delete Record
@app.route("/report-close/<int:cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    if request.method == 'DELETE':
        api_key = request.args.get("api-key")
        if api_key == "TopSecretAPIKey":
            try:
                data = Cafe.query.get(cafe_id)
                db.session.delete(data)
            except AttributeError:
                status = {"Not found": "Sorry, cafe with that id was not found in the database."}
            else:
                db.session.commit()
                status = {"Success": "The cafe was deleted."}
            finally:
                return jsonify(response=status)
        else:
            return jsonify(error="Sorry, that's not allowed. Please ensure you have a valid api-key.")


if __name__ == '__main__':
    app.run(debug=True)
