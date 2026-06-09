import json
import random

import pandas as pd
import time
import os
import requests


#### 获取网页源代码
def get_html(html_url):
    """
    获取网页源代码 response
    :param html_url: 网页url地址
    :return: 网页源代码
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", }
    response = requests.get(url=html_url, headers=headers)

    return response


####保存数据
def download(content, title, lis, timelist, new_froms, plis, types):
    # if os.path.exists('xinwen.csv'):
    # 	datas = pd.DataFrame(
    # 		{'新闻标题': title,'新闻内容': content,'新闻地址': lis,'新闻时间': timelist,'新闻作者': new_froms,'图片':plis,'类型':types})
    # 	datas.to_csv('xinwen.csv', mode='a+', index=False, header=0)
    # else:
    datas = pd.DataFrame(
        {'新闻标题': title, '新闻内容': content, '新闻地址': lis, '新闻时间': timelist, '新闻作者': new_froms, '图片': plis, '类型': types})
    datas.to_csv('news_data.csv', mode='a+', index=False, header=False)


### 主函数

def main(url, type):
    titles = []
    contents = []
    timelist = []
    new_froms = []
    leixings = []
    urls = []
    purls = []
    types = []


    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", }
    response = requests.get(url=url, headers=headers)
    html_data = response.text  # 获得接口数据response.text
    print(html_data)
    html_data = str(html_data).replace('specialcnsdata =', '').replace('newslist = specialcnsdata;', '').strip()[:-1]
    json_data = json.loads(html_data)
    for li in json_data['docs']:
        new_time = li['pubtime']
        new_from = li['content_y']
        if new_time == '':
            new_time = '2025年08月20'
        if new_from == '':
            new_from = '中国新闻网'
        titles.append(li['title'])
        contents.append(li['content'])
        new_froms.append(new_from)
        timelist.append(new_time)
        urls.append(li['url'])
        purls.append(li['galleryphoto'])
        types.append(type)

    download(contents, titles, urls, timelist, new_froms, purls, types)

#https://channel.chinanews.com/cns/cjs/gj.shtml?pager=1&pagenum=9&t=5_58'
if __name__ == '__main__':
    leixing_dict = {'gj': '国际', 'gn': '时政', 'sh': '社会', 'tw': '台湾', 'hr': '华人', 'cj': '财经', 'auto': '汽车', 'yl': '娱乐',
                    'ty': '体育', 'cul': '文化', 'ydyl': '一带一路', 'fz': '法治', 'jk': '健康'}

    for name, val in leixing_dict.items():
        time.sleep(5)
        # print(name,val)
        for page in range(1, 100):
            url_1 = 'https://channel.chinanews.com/cns/cjs/{0}.shtml?pager={1}&pagenum=9&t=5_58'.format(name, page)
            print(url_1)
            main(url_1, val)
