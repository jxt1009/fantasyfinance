from flask import Flask, render_template, session, request, redirect, Response
from flask_session import Session
import requests
import json


from database import Database

url = "https://finnhub.io/api/v1"
token = "ce093uaad3i6dc1cf08gce093uaad3i6dc1cf090"

test_user = {"id": 1, "given_name": "Test","family_name":"Test", "email":"test@aa.com"}

app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates'
            )
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = Database()

@app.route("/", methods=["POST", "GET"])
def homepage():
    session["user_info"] = test_user
    session['portfolio'] = {}
    return render_template('homepage.html')

@app.route("/signin", methods=["POST", "GET"])
def login():
    """    print("begin login")
    print(request)
    if request.method == "POST":
        oauth_id = jwt.decode(request.form['credential'], verify=False)
        user_info = {"id":oauth_id['sub']}
        success = db.check_user(user_info)
        print("login:" + str(success))
        if success:
            print("login success")
            session['user_info'] = user_info
            return redirect("/")
    """

    return Response("bbad", 400)

@app.route("/logout")
def logout():
    session["user_info"] = None
    return redirect("/")


@app.route("/make-trade", methods=["GET","POST"])
def make_trade():
    print("makeing trade")
    trade = request.form
    ticker = trade.get("ticker")
    shares = trade.get("shares")
    if db.make_trade(session['user_info'],{"ticker":ticker,"shares":shares}):
        print("good")
        return Response(status=200)
    print("bad")
    return Response(status=400)


@app.route("/portfolio-prices",methods=["GET"])
def update_current_stock_prices():
    portfolio = db.get_portfolio(session["user_info"])
    trades = []
    total_value = 0
    for stock in portfolio:
        price = float(get_price(stock["ticker"])['c'])
        shares = format(float(stock["shares"]),'.2f')
        value = price * float(stock['shares'])
        total_value += value
        value = format(value,'.2f')
        trades.append({"ticker": stock["ticker"], "price":price, "value": value, "shares":shares})
    print(trades)
    return json.dumps({"portfolio":trades,"value": total_value})

@app.route("/username")
def get_username():
    print(session)
    if "user_info" not in session:
        print("user not in session")
        return Response("User not logged in",status=400)
    json_obj = json.dumps({"username":session['user_info'].get('given_name')})
    print(json_obj)
    return json_obj


def get_price(ticker):
    response = requests.request("GET", f"{url}/quote?symbol={ticker}&token={token}")
    return json.loads(response.text)


def create_response_obj(message,code):
    return Response(f"{'message':'{message}'}", status=code, content_type="application/json")

if __name__ == '__main__':
    app.run(debug=True)
