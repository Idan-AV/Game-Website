import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

# from backend.models.game import Game
# from backend.models.loan import Loan
# from backend.models.user import User
from models.game import Game
from models.loan import Loan
from models.user import User

from models import db
from flask import session

import os

app = Flask(__name__)  # - create a flask instance
# - enable all routes, allow requests from anywhere (optional - not recommended for security)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Specifies the database connection URL. In this case, it's creating a SQLite database
# named 'library.db' in your project directory. The three slashes '///' indicate a
# relative path from the current directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
db.init_app(app)  # initializes the databsewith the flask application


# this is a decorator from the flask module to define a route for for adding a book, supporting POST requests.(check the decorator summary i sent you and also the exercises)
# works!!
@app.route('/games', methods=['GET', 'POST', 'DELETE'])
def games():
    if request.method == 'GET':
        try:
            games = Game.query.all()
            games_list = [
                {
                    'id': game.id,
                    'title': game.title,
                    'genre': game.genre,
                    'price': game.price,
                    'quantity': game.quantity
                }
                for game in games
            ]

            return jsonify({'message': 'Games retrieved successfully', 'games': games_list}), 200

        except Exception as e:
            return jsonify({'error': 'Failed to retrieve games', 'message': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.json
            new_game = Game(
                title=data['title'],
                genre=data['genre'],
                price=data['price'],
                quantity=data['quantity']
            )
            db.session.add(new_game)
            db.session.commit()
            return jsonify({'message': 'Game added successfully'}), 201

        except Exception as e:
            return jsonify({'error': 'Failed to add game', 'message': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            data = request.json
            game_id = data.get('id')

            if not game_id:
                return jsonify({'error': 'Game ID is required'}), 400

            game = Game.query.get(game_id)

            if not game:
                return jsonify({'error': 'Game not found'}), 404

            db.session.delete(game)
            db.session.commit()

            return jsonify({'message': 'Game deleted successfully'}), 200

        except Exception as e:
            return jsonify({'error': 'Failed to delete game', 'message': str(e)}), 500


# works!!!
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json

        # Check if there's any admin in the database
        existing_admin = User.query.filter_by(role=1).first()

        # If no admin exists, the first user is an admin; otherwise, default to customer
        role = 1 if not existing_admin else 2

        new_user = User(
            name=data['name'],
            phone_number=data['phone_number'],
            city=data['city'],
            age=data['age'],
            password=data["password"],
            role=role  # Automatically assign role
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'role': role}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to register user', 'message': str(e)}), 500


# works!!
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        phone_number = data.get('phone_number')
        password = data.get('password')

        user = User.query.filter_by(phone_number=phone_number).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['user_name'] = user.name

            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'phone_number': user.phone_number,
                    'city': user.city,
                    'age': user.age
                }
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': 'Failed to login', 'message': str(e)}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/loans_for_customer/<int:user_id>', methods=['GET'])
def get_loans_for_customer(user_id):
    try:
        loans = Loan.query.filter_by(user_id=user_id).all()

        games_list = [
            {
                'id': loan.game.id,
                'title': loan.game.title,
                'genre': loan.game.genre,
                'price': loan.game.price,
                'quantity': loan.game.quantity
            }
            for loan in loans if loan.game
        ]

        return jsonify({'message': 'Loans retrieved successfully', 'games': games_list}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to retrieve games', 'message': str(e)}), 500

# works!!!
@app.route('/loans', methods=['GET', 'POST'])
def loans():
    if request.method == 'GET':
        try:
            loans = Loan.query.all()
            loans_list = [
                {
                    'loan_id': loan.id,
                    'user_name': loan.user.name,
                    'game_id': loan.game.id,
                    'title': loan.game.title,
                    'genre': loan.game.genre,  # Fixed incorrect attribute name
                    'price': loan.game.price,
                    'quantity': loan.game.quantity,
                    'loan_date': loan.loan_date.strftime("%Y-%m-%d"),
                    'return_date': loan.return_date.strftime("%Y-%m-%d") if loan.return_date else None
                }
                for loan in loans if loan.game
            ]

            return jsonify({'message': 'Loans retrieved successfully', 'loans': loans_list}), 200

        except Exception as e:
            return jsonify({'error': 'Failed to retrieve loaned games', 'message': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.json
            user_id = data.get('user_id')
            game_id = data.get('game_id')

            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            game = Game.query.get(game_id)
            if not game:
                return jsonify({'error': 'Game not found'}), 404

            if game.quantity <= 0:
                return jsonify({'error': 'Game is out of stock'}), 400

            new_loan = Loan(user_id=user.id, game_id=game.id, loan_date=datetime.utcnow())
            game.quantity -= 1

            db.session.add(new_loan)
            db.session.commit()

            return jsonify({'message': 'Game loaned successfully'}), 201

        except Exception as e:
            return jsonify({'error': 'Failed to loan game', 'message': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables defined in your  models(check the models folder)

    app.run(debug=True)  # start the flask application in debug mode
