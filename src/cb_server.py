# usr/bin/python27
# author: Seoung H. Song


"""This file has been made up with server.py base"""

from flask import Flask, jsonify, request, render_template
from flask import make_response
from detect import detector  # Article headline's clickbaitiness predictor
from extract import extractor # Article headline extractor
from flask_cors import CORS
import logging
import validators
import unicodedata
import csv



app = Flask(__name__)

# allow all domains can get the response from this server.
CORS(app)


@app.route("/", methods=['GET','POST'])
@app.route("/index", methods=['GET','POST'])
def analyze ():

    if request.method == 'POST':
        sample_url = request.form["sample_url"]
        headline = None
        clickbaitiness = None

        if validators.url(sample_url) and sample_url is not "":
            # logging.info("given URL is: {0}".format(sample_url))
            try:
                article = extractor.extract(sample_url)
                headline = article['title']
            except Exception:
                logging.error("extract headline failed")
                pass

            if headline is not None:
                # logging.info("extracted headline is: {0}".format(headline))

                # try:
                #     # There should be an waiting time for this
                #     clickbaitiness = predictor.predict(headline)
                # except Exception:
                #     logging.error("predict failed")
                #     pass

                headline = unicodedata.normalize('NFKD', headline).encode('ascii','ignore')
                clickbaitiness = detector.detect(headline)

                row = [headline, clickbaitiness] # For extracting as csv file
                try:
                    SetToFile(row)
                except Exception:
                    logging.error("store as file failed")
                    pass
            else:
                # TODO: return index.html with error flash
                pass
        else:
            # TODO: return index.html with error flash
            logging.error("invalid URL is given")
            pass

        print(headline)
        print(clickbaitiness)
        print("===============")

        if headline is not None and clickbaitiness is not None:
            newsinfo = {"headline": headline, "clickbaitiness": round(clickbaitiness, 2)*100}
        else:
            newsinfo = None

        return render_template('index.html', newsinfo=newsinfo)
        # return render_template('index.html', headline, clickbaitiness)
    else:
        return render_template('index.html')


@app.route("/detect", methods=["GET"])
def detect ():
    headline = request.args.get("headline", "")
    clickbaitiness = predictor.predict(headline)

    # TODO: Store headlines and their clickbaitiness results as external file.
    return jsonify({ "clickbaitiness": round(clickbaitiness * 100, 2) })


@app.route("/predict", methods=["GET"])
def predict ():
    url = request.args.get("URL", "")

    # TODO: run stance prediction model with given url and return the result.
    stance = 'empty_now'
    # TODO: Store headlines and their stance results as external file.
    return jsonify({ "stance": stance })



def SetToFile(row):
    # Assume that we already know the structure of csv file
    # Appending following row
    flag = False
    headlines = []

    with open('news.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)
        # print(lines)

        for line in lines:
            flag = (row[0] == line[0])
            headlines.append(flag)


        if True not in headlines:
            with open('news.csv', 'a') as appendFile:
                writer = csv.writer(appendFile)
                writer.writerow(row)

            appendFile.close()
        else:
            logging.error("headline is already exists")

    readFile.close()



if __name__ == "__main__":
    app.secretKey = 'superSecret'

    # Exporting log history as an external log file
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    app.run(host='127.0.0.1', port=3000, debug=True, ssl_context=('cert.pem', 'key.pem'))
