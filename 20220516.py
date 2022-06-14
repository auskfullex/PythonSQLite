from datetime import datetime
import time
import re
import pandas as pd
# from pandasgui import show
pd.options.display.max_colwidth = 500
pd.options.display.max_columns = 100
pd.options.display.max_rows= 100
pd.set_option('display.max_colwidth', 500)
pd.set_option('display.float_format',  '{:,}'.format)
import warnings
warnings.filterwarnings("ignore", 'This pattern is interpreted as a regular expression, and has match groups. To actually get the groups, use str.extract.')

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
#
# opts = Options()
# opts.add_argument("user-agent=New York Institute of Technology servicecentral@nyit.edu")
# opts.add_argument("content-encoding=gzip")
# opts.add_argument("From=jsuh02@nyit.edu")


# what change?



########################################################################################################################
# READING WEB-SCRAPED DATASETS
########################################################################################################################
path = r'C:\Dropbox\Research\NonGAAP_CF'
ea0508 = pd.read_csv(path+r'\parse_nongaap\nongaap 0508.csv') # 27,307
ea1720 = pd.read_csv(path+r'\parse_nongaap\nongaap 1720.csv') # 42,793
ea0916 = pd.read_csv(path+r'\parse_nongaap\nongaap 0916.csv') # 68,810
ea = pd.concat([ea0508, ea0916, ea1720], ignore_index=True) # 138,910

########################################################################################################################
# REGEX CONSTRUCTION
########################################################################################################################
# NONGAAP: nongaap_prefix & nongaap_suffix
adjusted = r'\(?adjusted\)?'
discr = r'\(?discretionary\)?'
distr = r'\(?distributable\)?'
nongaap = r'\(?non-?\s*gaap\)?'
proforma = r'\(?pro-?\s*forma\)?'
before_wc_chg = r'\(?before\s*working\s*capital\s*changes?\)?'
nongaap_prefix = '|'.join([adjusted,discr,distr,nongaap,proforma])
nongaap_suffix = '|'.join([adjusted,discr,distr,nongaap,proforma,before_wc_chg])

# EXTRA DESCRIPTIONS PRECEDING CF:exdesclead
net = r'net'
aftertax = r'(after\s*-*\s*tax)'
operating = r'operating'
exdesclead = '|'.join([net,aftertax,operating])

# CASH FLOW
cf = r'(?!.*\b(?:free))(cash\s*-*flows?)|(cash\s*-*earnings?)|cf|cash' # () asks to remember groups, and ?: asks to not remember the grouped part. https://stackoverflow.com/questions/3705842/what-does-do-in-regex
# cf = r'(cash\s*-*flows?)|(cash\s*-*earnings?)|cf|cash'
# ebitda = r'(ebidta|(earnings?\s*before\s*interests?\s*\,*(taxes|tax)\s*\,*\s*depreciations?\s*(and)?\s*amortizations?))'
# ebit = r'(ebit|(earnings?\s*before\s*interests?\s*\,*(and)?\s*(taxes|tax)))'



# EXTRA DESCRIPTIONS FOLLOWING CF: exdescfol
fromop = r'(from\s*((operations?)|operating\s*(activities|activity)))'
beforewc = r'(before\s*working\s*capitals?)'
providedby = r'(provided\s*by\s*operating\s*(activities|activity))'
exdescfol = '|'.join([fromop,beforewc,providedby])

# COMBINE ALL
# regex_prefix = r'('+nongaap_prefix+r')'+r'\s*('+exdesclead+")?\s*"+"("+cf+"|"+ebitda+"|"+ebit+")\s*("+exdescfol+")?"
# regex_suffix = r'('+exdesclead+")?\s*"+"("+cf+"|"+ebitda+"|"+ebit+")\s*("+exdescfol+")?\s*("+nongaap_suffix+")"
regex_prefix = r'('+nongaap_prefix+r')'+r'\s*('+exdesclead+")?\s*"+"("+cf+")\s*("+exdescfol+")?"
regex_suffix = r'('+exdesclead+")?\s*"+"("+cf+")\s*("+exdescfol+")?\s*("+nongaap_suffix+")"
regex = r'('+regex_prefix+r')'+'|'+r'('+regex_suffix+r')'

# TEST
text = 'Pro forma free-cash flow'
result = re.search(regex, text, re.I)
result.group()

ea = ea.assign(nongaapcf202 = ea.item202.str.contains(regex, flags = re.I),
               nongaapcf701 = ea.item701.str.contains(regex, flags = re.I),
               nongaapcf801 = ea.item801.str.contains(regex, flags = re.I),
               nongaapcf901 = ea.item901.str.contains(regex, flags = re.I),
               nongaapcf991 = ea.exhibit991.str.contains(regex, flags = re.I))

columns = ['url','datadate','nongaapcf202','nongaapcf701','nongaapcf801','nongaapcf901','nongaapcf991','nongaapcf']
ea = ea.assign(nongaapcf = (ea.nongaapcf202 == True) |
                           (ea.nongaapcf701 == True) |
                           (ea.nongaapcf801 == True) |
                           (ea.nongaapcf901 == True) |
                           (ea.nongaapcf991 == True)
               )

ea_nongaapcf = ea.loc[ea.nongaapcf == True, columns]
ea_nongaapcf.to_excel(path+r'\work\nongaapcf.xlsx')





########################################################################################################################
# BELOW ARE NOT USED
########################################################################################################################

# ########################################################################################################################
# # LOGISTIC MODEL
# ########################################################################################################################
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import CountVectorizer
#
# y = impair.HFU.values
# sentences = impair.contents.values
# sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, y, test_size=0.25, random_state=1000)
#
# vectorizer = CountVectorizer()
# vectorizer.fit(sentences_train)
# X_train = vectorizer.transform(sentences_train)
# X_test  = vectorizer.transform(sentences_test)
# X_train
#
# from sklearn.linear_model import LogisticRegression
# classifier = LogisticRegression().fit(X_train, y_train)
# score = classifier.score(X_test, y_test)
# print("Accuracy:", score) #66%. too low.
#
# classifier.predict(X_test)
#
#
#
#
#
# ########################################################################################################################
# # BAG OF WORDS
# ########################################################################################################################
# from sklearn.feature_extraction.text import CountVectorizer
#
# hfs = impair.loc[impair.HFU == False,:]
# sentences_hfs = hfs.contents.values
# lsentences_hfs = list(sentences_hfs)
# lsentences_hfs
# cv = CountVectorizer(lsentences_hfs)
# count_vector=cv.fit_transform(lsentences_hfs)
# type(cv.vocabulary_)
#
# hfs.iloc[5,:]
#
# ########################################################################################################################
# # RUNNING NAIVE BAYES MODEL
# ########################################################################################################################
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.pipeline import make_pipeline
# model = make_pipeline(TfidfVectorizer(), MultinomialNB())
# model.fit(impair.contents, impair.HFU)
#
# def predict_category(s, train = impair, model = model):
#     pred = model.predict([s])
#     return train.HFU[pred[0]]
#
#
# predict_category('text')
#
# model