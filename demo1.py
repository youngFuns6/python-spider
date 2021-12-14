# -*- coding = utf-8 -*-
# @Author: youngfuns
# @Time : 2021/12/11 21:49
# @File : demo1.py
# @Software: PyCharm
import re
import urllib.error  # 制定url， 获取网页数据
import urllib.request
from bs4 import BeautifulSoup
import xlwt  # 进行Excel操作
import sqlite3


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 爬取网页
    datalist = getData(baseurl)
    # 保存到Excel
    # savepath = '.\\豆瓣电影top250.xls'
    # saveData(datalist, savepath)
    #  保存到SQLit
    sqlitePath = 'movie250.db'
    saveToDb(datalist, sqlitePath)


findLink = re.compile(r'<a href="(.*?)">')
findImgSrc = re.compile(r'<img src="(.*?)">', re.S)
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRating = re.compile(r'span class="rating_num" property="v:average">(.*)</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'span class="inq">(.*)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i * 25)
        html = askUrl(url)
        # print(url)

        # 解析数据
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.findAll("a"))
        for item in soup.findAll("div", class_="item"):
            data = []
            item = str(item)

            # 获取相关信息
            link = re.findall(findLink, item)[0]
            data.append(link)

            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)
            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(" ")

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append(" ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', ' ', bd)
            bd = re.sub('/', " ", bd)
            data.append(bd.strip())

            datalist.append(data)

    # print(datalist)
    return datalist


def askUrl(url):
    head = {
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 96.0.4664.93Safari / 537.36"
    }
    request = urllib.request.Request(url, headers=head)
    # html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        return html
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)


# 保存数据
def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet("豆瓣电影TOP250", cell_overwrite_ok=True)
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for i in range(0, 250):
        print("爬取第%d条" % i)
        for j in range(0, 8):
            sheet.write(i + 1, j, datalist[i][j])
    book.save(savepath)

def saveToDb(datalist, dbpath):
    # 连接数据库 创建数据表
    init_db(dbpath)
    # 插入数据
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    for data in datalist:
        for i in data:
            if data.index(i) == 4 or data.index(i) == 5:
                continue
                i = '"' + i + '"'
        sql = '''
            insert movie_top (
                info_link,
                banner_link,
                title,
                i_title,
                rating,
                judge,
                inq,
                info
            ) values (%s);
        ''' % ','.join(data)
        # cursor.execute(sql)
        # conn.commit()
        # conn.close()
        print(sql)
    # info = sqlite3.connect(dbpath)
    # cu = info.cursor()
    # c = cu.execute('select * from movie_top')
    # print(c)
    # info.commit()
    # info.close()

def init_db(dbpath):
    sql = '''
        create table movie_top(
        id integer primary key autoincrement,
        info_link text,
        banner_link text,
        title varchar,
        i_title varchar,
        rating numeric,
        judge numeric,
        inq text,
        info text
        )
    '''

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
