# usr/bin/python27
# author: Seoung H. Song


"""
    This file has been made up with server.py base.

    This server logic has been made in order to check the function of UCLMR engine.
"""

from flask import Flask, jsonify, request, render_template
from flask import make_response
from tmp_predict import predictor  # Article stance detector
from extract import extractor # Article headline extractor
import logging
import validators
import unicodedata
import csv



app = Flask(__name__)


@app.route("/", methods=['GET','POST'])
@app.route("/index", methods=['GET','POST'])
def analyze ():

    if request.method == 'POST':
        sample_url = request.form["sample_url"]
        headline = None
        content = None
        stance = None

        if validators.url(sample_url) and sample_url is not "":
            # logging.info("given URL is: {0}".format(sample_url))
            try:
                article = extractor.extract(sample_url)

                headline = article['title']
                content = article['content']

            except Exception:
                logging.error("extract headline failed")
                pass

            if headline is not None and content is not None:

                predictor.save_testData(headline, content)
                stance = predictor.predict(headline, content)

                row = [headline, stance] # For extracting as csv file
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
        print(stance)
        print("===============")

        if headline is not None and stance is not None:
            newsinfo = {"headline": headline, "stance": stance}
        else:
            newsinfo = None

        # return render_template('index.html', newsinfo=newsinfo)
        return render_template('index.html')
    else:
        return render_template('index.html')


def SetToFile(row):
    # Assume that we already know the structure of csv file
    # Appending following row
    flag = False
    headlines = []

    with open('news_stance.csv', 'r') as readFile:
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
