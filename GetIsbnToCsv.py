'''
ISBNコードから書籍情報を取得しCSVファイルとして出力するプログラム

【参考】
Google Book APIを使ってISBNコードから書籍情報を取得する
https://blogs.embarcadero.com/ja/google-book-api-isbn/

PythonでJSONを扱うための方法を解説
https://techplay.jp/column/558

辞書型のKeyErrorを回避する
https://tomoprog.hatenablog.com/entry/2016/05/18/222959
'''

import json
import requests

f = open('data/ISBN_output.csv', 'w')
ferror = open('data/ISBN_error.txt', 'w')
# このプログラムでは、JSONの要素のうち、以下の要素をCSVに出力することにする。
tempStr = "isbnNo,title,authors,publishedDate,pageCount,description,selfLink\n"
f.write(tempStr)

fi = open("data/ISBN_list.txt", 'r')
isbnNoList = fi.readlines()
fi.close()

urlOrigin = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

for isbnNo in isbnNoList:
    isbnNo = isbnNo.replace("\n", "")
    jsonStr = requests.get(urlOrigin + isbnNo)
    # print(jsonStr.text)
    # print(jsonStr)

    jsonContent = json.loads(jsonStr.text)
    if jsonContent["totalItems"] == 0:
        print(isbnNo + ": Error. No book.")
        ferror.write(str(isbnNo) + "\n")
        continue

    tempStr = ""
    tempStr = tempStr + '"' + isbnNo + '",'
    tempStr = tempStr + '"' + jsonContent["items"][0]["volumeInfo"]["title"] + '",'
    tempStr = tempStr + '"' + " ".join(jsonContent["items"][0]["volumeInfo"]["authors"]) + '",'
    tempStr = tempStr + jsonContent["items"][0]["volumeInfo"]["publishedDate"] + ","
    tempStr = tempStr + str(jsonContent["items"][0]["volumeInfo"]["pageCount"]) + ","
    # descriptionは存在しない可能性あり。Oracleで言うNVL関数の代わりに、try-except文を使用。
    try:
        tempStr = tempStr + '"' + jsonContent["items"][0]["volumeInfo"]["description"] + '",'
    except KeyError:
        ferror.write(isbnNo + "\n")
        tempStr = tempStr + ","

    tempStr = tempStr + jsonContent["items"][0]["selfLink"] + "\n"
    f.write(tempStr)
    print(isbnNo + ": OK.")

f.close()
ferror.close()
