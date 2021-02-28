'''
ISBNコードから書籍情報を取得しDBに出力するプログラム

【参考】
psycopg2 でよくやる操作まとめ
https://qiita.com/hoto17296/items/0ca1569d6fa54c7c4732
'''

import json
import requests
import psycopg2


def get_connection():
    # connect postgreSQL
    # dsn = os.environ.get('DATABASE_URL')
    users = 'postgres'  # initial user
    dbnames = 'postgres'
    passwords = 'postgres'
    return psycopg2.connect(" user=" + users + " dbname=" + dbnames + " password=" + passwords)


ferror = open('data/ISBN_error.txt', 'w')

fi = open("data/ISBN_list.txt", 'r')
isbnNoList = fi.read().splitlines()
fi.close()

urlOrigin = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

with get_connection() as conn:
    with conn.cursor() as cur:
        for isbnNo in isbnNoList:
            cur.execute('select count(*) from book_reading.isbn_txn where isbn_no like %s', (str(isbnNo),))
            (record_count, ) = cur.fetchone()
            if record_count != 0:
                print(isbnNo + ": Error. Already inserted. Skipped.")
                continue

            jsonStr = requests.get(urlOrigin + str(isbnNo))

            jsonContent = json.loads(jsonStr.text)
            if jsonContent["totalItems"] == 0:
                print(isbnNo + ": Error. No book.")
                ferror.write(str(isbnNo) + "\n")
                continue

            # descriptionは存在しない可能性あり。Oracleで言うNVL関数の代わりに、try-except文を使用。
            description = ""
            try:
                description = jsonContent["items"][0]["volumeInfo"]["description"]
            except KeyError:
                ferror.write(isbnNo + "\n")

            sqlStr = ('INSERT INTO book_reading.isbn_txn ('
                      'isbn_no'
                      ',title'
                      ',authors'
                      ',published_date'
                      ',page_count'
                      ',description'
                      ',self_link'
                      ',create_user'
                      ',update_user'
                      ') VALUES ('
                      '%s'
                      ',%s'
                      ',%s'
                      ',to_date(%s, \'YYYY/MM/DD\' )'
                      ',%s'
                      ',%s'
                      ',%s'
                      ',%s'
                      ',%s'
                      ')')
            sqlParameter = (isbnNo.strip(" ")
                            , jsonContent["items"][0]["volumeInfo"]["title"]
                            , "  ".join(jsonContent["items"][0]["volumeInfo"]["authors"])
                            , jsonContent["items"][0]["volumeInfo"]["publishedDate"]
                            , jsonContent["items"][0]["volumeInfo"]["pageCount"]
                            , description
                            , jsonContent["items"][0]["selfLink"]
                            , "admin"
                            , "admin"
                            )
            cur.execute(sqlStr, sqlParameter)
            print(isbnNo + ": OK.")

        conn.commit()

ferror.close()
