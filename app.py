from flask import Flask, redirect, url_for, render_template, request,jsonify
import requests
import sys

app = Flask(__name__)

API_KEY = 'b72d5b0f-9505-4063-9104-5d7a1c314562'
pairs = {}
@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        amount = request.form["amount"]
        address=request.form["address"]
        depositCurrency = request.form['depositCurrency']
        receiveCurrency = request.form['receiveCurrency']
        print(depositCurrency,receiveCurrency,file=sys.stderr)
        # new_amount = requests.get('https://api.simpleswap.io/v1/get_estimated?api_key=b72d5b0f-9505-4063-9104-5d7a1c314562&fixed=false&currency_from=btc&currency_to=eth&amount='+amount).text
        r = requests.post('https://api.simpleswap.io/v1/create_exchange?api_key='+API_KEY,json={"fixed": "", "currency_from":depositCurrency,"currency_to":receiveCurrency,"address_to":address,"amount":amount}).json()
        if('code' in r):
            if(r['code']==400):
                return redirect(url_for("exchange", id="Address not valid"))
        else:
            id = r['id']
            return redirect(url_for("exchange", id=id))
    else:
        global pairs
        # r = requests.get('https://api.simpleswap.io/v1/get_all_currencies?api_key='+API_KEY)
        pairs = requests.get('https://api.simpleswap.io/v1/get_all_pairs?api_key={}&fixed='.format(API_KEY)).json()
        depositCurrency = []
        tmp = pairs.keys()
        tmp = list(tmp)
        tmp.sort()
        print(len(tmp),tmp,file=sys.stderr)
        for i in tmp:
            # t = {}
            # t['symbol'] = i['symbol']
            # t['name'] = i['name']
            depositCurrency.append({'symbol':i,'name':i})
        return render_template("login.html",depositCurrency=depositCurrency)

@app.route("/exchange")
def exchange():
    r = request.args.get('id',0)
    print(r,file=sys.stderr)
    return "id = " + r

@app.route('/currencyPair')
def currencyPair():
    symbol = request.args.get('symbol',default=0)
    # a = requests.get('https://api.simpleswap.io/v1/get_pairs?api_key={}&fixed=&symbol={}'.format(API_KEY,symbol)).json()
    # print(symbol,file=sys.stderr)
    # print(r,file=sys.stderr)
    global pairs
    a = pairs[symbol]
    a.sort()
    print(len(a),a,file=sys.stderr)
    r = []
    for i in a:
        r.append({'name':i,'symbol':i})
    return jsonify(result = r)

@app.route('/getRate')
def getRate():
    deposit = request.args.get('deposit',default=0)
    receive = request.args.get('receive',default=0)
    amount =  request.args.get('amount',default=0)

    a = requests.get('https://api.simpleswap.io/v1/get_estimated?api_key={}&fixed=&currency_from={}&currency_to={}&amount={}'.format(API_KEY,deposit,receive,amount)).json()
    r = {'rate': a}
    print(r,file=sys.stderr)
    return jsonify(result = r)

@app.route('/getMinMax')
def getMinMax():
    deposit = request.args.get('deposit',default=0)
    receive = request.args.get('receive',default=0)
    amount = request.args.get('amount',default=0)
    a = requests.get('https://api.simpleswap.io/v1/get_ranges?api_key={}&fixed=&currency_from={}&currency_to={}'.format(API_KEY,deposit,receive)).json()
    min = a['min']
    max = a['max']
    try:
        min = float(min)
    except:
        min = 'null'
    try:
        max = float(max)
    except:
        max = 'null'
    try:
        amount = float(amount)
    except:
        amount = 0
    r = {'min': min,'max': max}
    if(min=='null' or amount<=0 or amount<min):
        r['error'] = 1
    elif(max!='null' and amount>max):
        r['error'] = 1
    else:
        r['error'] = 0
    print(r,file=sys.stderr)
    return jsonify(result = r)

if __name__ == "__main__":
    app.run(debug=True)
