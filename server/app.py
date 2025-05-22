from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({"error": "Bakery not found"}), 404
    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get_or_404(id)
    data = request.get_json() or {}
    name = data.get('name')
    if name:
        bakery.name = name
        db.session.commit()
    return jsonify(bakery.to_dict()), 200

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_serialized = [bg.to_dict() for bg in baked_goods]
    return make_response(jsonify(baked_goods_serialized), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not most_expensive:
        return jsonify({"error": "No baked goods found"}), 404
    return make_response(jsonify(most_expensive.to_dict()), 200)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.get_json() or {}
    name = data.get('name')
    price = data.get('price')
    bakery_id = data.get('bakery_id')

    if not all([name, price, bakery_id]):
        return jsonify({"error": "Missing data for baked good creation"}), 400

    baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(baked_good)
    db.session.commit()

    return jsonify(baked_good.to_dict()), 201

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get_or_404(id)
    db.session.delete(baked_good)
    db.session.commit()
    return jsonify({"message": f"Baked good '{baked_good.name}' deleted"}), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
