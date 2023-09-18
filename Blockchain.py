import json
from flask import Flask, jsonify, request, abort
from Miner import Miner

app = Flask(__name__)
chain = None

def get_blockchain():
    with open("blockchain.json", "r") as file:
        chain = json.loads(file.read())
    return chain

origin_creator = "MIIBCgKCAQEAn6w660T90g+Oty4PFTvy20rUuQ0BY8OkyfSjhcRJLcd+0Elm1zaePpK0Swk7z/mcdqEAfFmlVJB1WDMbK4i6W6dwvLXLguXokRWHS+n+zxPPwj15zaszuIi/eKfWf8pVHRu8y0yyKr1JP8qezxbP7hecKOsttPm6G5aWZyJemonYAmfdcvc5AVlgetUko/KAcqPLkYu8wp2w5mrM0zhiwiG8gGqwPUMgyPLfBuxjoa7PX3kbOch4xYemuMOfNKy6B2zZq9r5d0SCanc1kheOTCqmD/4wxzjc2JrrbsEhWu8QXfVW9fVtBr/Ld0xtIEhraB4yKozivpVlCPm5NbFMowIDAQAB"
current_transaction = {}

@app.route('/blockchain')
def chain():
    return jsonify(get_blockchain())

@app.route('/')
def index():
    return "<h1>Welcome to the LexiCoin API</h1><h3>Endpoints:</h3><ul><li>/blockchain</li><li>/current-block</li><li>/new-transaction</li><li>/verify-block</li><li>/add-block</li></ul>"

@app.route('/current-block')
def this_transaction():
    with open("current_block.json", "r") as file:
        contents = file.read().split("\n")
    return jsonify(contents)

@app.route('/new-transaction', methods=['POST'])
def new_transaction():
    current_transaction = request.json
    with open("current_block.json", "a") as file:
        file.write(json.dumps(request.json)+"\n")
    return jsonify(current_transaction), 201

block = None
miner = Miner(4)
@app.route('/add-block', methods=['POST'])
def add_block():
    bc = get_blockchain()
    block = request.get_json(force=True)
    valid = miner.verify_block(block, bc)
    print("Valid: ", valid)
    if valid:
        with open("current_block.json", "w") as current_block:
            current_block.write("")
        bc[0][f"{len(bc[0])+1}"] = block
        with open("blockchain.json", "w") as bc_file:
            bc_file.write(bc)
    return bc


app.run()