from flask import Flask, jsonify, request
import requests
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

class Choice:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name.lower()

    def to_dict(self):
        return {"id": self.id, "name": self.name}
    
#create an array of all possible choices
choices = [
    Choice(1,"rock"), 
    Choice(2,"paper"), 
    Choice(3,"scissors"), 
    Choice(4,"lizard"), 
    Choice(5,"spock"),
    ]

def game_logic(player_input,computer_input):
    #check if the computer input is in one of the options in which it loses based on the user input
    if computer_input in computer_lose[player_input]:
        #print victory
        return "win"
    #check if the computer input and player input are the same
    elif computer_input == player_input:
        return "tie"
    #user loses in all other situations
    else:
        return "lose"

def get_choice_by_id(choice_id):
    return next((c for c in choices if c.id == choice_id), None)

#creating a dictionary with the key being a possible user choice and the values being an array with all the combinations in which the computer loses
computer_lose = {
    "scissors" : ["paper","lizard"],
    "paper" : ["rock","spock"],
    "rock" : ["lizard","scissors"],
    "lizard" : ["spock","paper"],
    "spock": ["scissors","rock"],
}

#since the api endpoint returns a number from 1 to 100 this function assigns the number to one of the possible choices
def get_computer_input(index):
    if index <= 20:
        return 0
    if index > 20 and index <= 40:
        return 1
    if index > 40 and index <= 60:
        return 2
    if index > 60 and index <= 80:
        return 3
    if index > 80 and index <= 100:
        return 4

#function that returns a random number from the https://codechallenge.boohma.com/random endpoint
def get_random_number():
    response = requests.get("https://codechallenge.boohma.com/random")
    if response.status_code == 200:
        return response.json()["random_number"]
    else:
        raise Exception("Something went wrong")


#API ENDPOINTS

#creating choices endpoint which returns all possible choices     
@app.route("/choices",methods=["GET"])
def return_choices():
    return jsonify([choice.to_dict() for choice in choices])

#create choice endpoint which returns a random choice
@app.route("/choice",methods=["GET"])
def get_random_choice():
    try:
        choice_id = get_computer_input(get_random_number())
        choice = choices[choice_id]
        return jsonify(choice.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#create play endpoint which returns the player choice, computer choice and result
@app.route("/play",methods=["POST"])
def play():
    data = request.get_json()
    player_id = data.get("player")
    player_choice = get_choice_by_id(player_id).name

    if not player_choice:
        return jsonify({"error": "Invalid player choice ID"}), 400

    try:
        computer_choice_id = get_computer_input(get_random_number())
        computer_choice = get_choice_by_id(computer_choice_id).name
        result = game_logic(player_choice, computer_choice)

        return jsonify({
            "results": result,
            "player": player_id,
            "computer": computer_choice_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)