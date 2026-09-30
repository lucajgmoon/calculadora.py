import ast
import operator

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Operações permitidas (nada de eval() direto, por segurança)
OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def avaliar(no):
    if isinstance(no, ast.Expression):
        return avaliar(no.body)
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp) and type(no.op) in OPERADORES:
        esquerda, direita = avaliar(no.left), avaliar(no.right)
        if isinstance(no.op, ast.Pow) and abs(direita) > 100:
            raise ValueError("Expoente muito grande")
        return OPERADORES[type(no.op)](esquerda, direita)
    if isinstance(no, ast.UnaryOp) and type(no.op) in OPERADORES:
        return OPERADORES[type(no.op)](avaliar(no.operand))
    raise ValueError("Expressão inválida")


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/calcular", methods=["POST"])
def calcular():
    expressao = (request.get_json(silent=True) or {}).get("expressao", "")
    try:
        arvore = ast.parse(expressao, mode="eval")
        resultado = avaliar(arvore)
        return jsonify(resultado=resultado)
    except ZeroDivisionError:
        return jsonify(erro="Divisão por zero"), 400
    except Exception:
        return jsonify(erro="Expressão inválida"), 400


if __name__ == "__main__":
    app.run(debug=True)
