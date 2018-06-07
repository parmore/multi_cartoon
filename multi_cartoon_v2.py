# _*_coding:utf-8_*_
import requests
import bs4
from bs4 import BeautifulSoup
import os
import re
import urllib
from multiprocessing import Pool, Manager


def make_dir(dpath):  # 建立目录
    if not os.path.exists(dpath):
        os.makedirs(dpath)
    else:
        pass


def download_all_pic(file_name, url, allpic):
    if not os.path.exists(file_name):
        print('正在下载.....%s(%s)' % (file_name, allpic))
        urllib.request.urlretrieve(url.strip('\''), filename=file_name)


def get_all_tags_links(url):  # 获取所有类型的链接地址&名字
    web_response = requests.get(url)
    web_soup = BeautifulSoup(web_response.text, 'lxml')
    tmp = web_soup.find('div', class_='tag')
    tags_links = {}
    k = 1
    for i in tmp.ul:
        if isinstance(i, bs4.element.Tag) and i.a['title'] != '全部':
            tag_name = i.a['title']
            tag_url = 'http:' + i.a['href']
            tags_links[tag_name] = tag_url
            k = k + 1
    return tags_links


def get_all_tag_page_links(key, url, data_tgpl):  # 获取所有分类下面分页地址
    web_response = requests.get(url)
    web_soup = BeautifulSoup(web_response.text, 'lxml')
    all_web_links = web_soup.find('div', class_='page')
    if all_web_links.find('a', class_='pagination-cell'):
        page_tags = all_web_links.find('a', class_='pagination-cell')
        for i in range(1, int(page_tags.string) + 1):
            url_tmp = url.rstrip('/') + '-' + str(i) + '-1/'
            index = key + '|' + str(i)
            data_tgpl[index] = url_tmp
            print('正在获取******[%s]******第*******[%s]*******页的链接' % (key, i))
    elif all_web_links.a:
        data_tgpl[key + '|1'] = url
        for i in all_web_links.a.next_siblings:
            if isinstance(i, bs4.element.Tag):
                print('正在获取******[%s]******第*******[%s]*******页的链接' % (key, str(i.string)))
                url_tmp = url.rstrip('/') + '-' + str(i.string) + '-1/'
                index = key + '|' + str(i.string)
                data_tgpl[index] = url_tmp
    else:
        data_tgpl[key + '|1'] = url


def get_all_cartoon_index(key, value, data_ctindex):
    itmp = key.split('|')
    lx, pnum = itmp[0], itmp[1]
    print('正在读取***[%s]***第****[%s]****页上的cartoon首页信息' % (lx, pnum))
    web_response = requests.get(value)
    web_soup = BeautifulSoup(web_response.text, 'lxml')
    all_web_links = web_soup.find('div', class_='list_mh')
    if not all_web_links.div:
        for j in all_web_links.children:
            if isinstance(j, bs4.element.Tag):
                p = re.compile('\?|\.|\\\\|/|:|\*|"|<|>|→|')
                cinfo = p.sub('', j.li.a['title'])
                index = key + '|' + cinfo
                data_ctindex[index] = 'http:' + j.li.a['href']


def get_all_cartoon_cpages(key, value, data_cplink):
    itmp = key.split('|')
    lx, pnum, gname = itmp[0], itmp[1], itmp[2]
    print('正在获取***%s***第****%s****页***%s***的章节链接' % (lx, pnum, gname))
    web_response = requests.get(value)
    web_soup = BeautifulSoup(web_response.text, 'html.parser')
    all_chap = web_soup.find('div', id='chapter-list-flag')
    for i in all_chap.ul:
        if isinstance(i, bs4.element.Tag) and not i.em:
            p = re.compile('\?|\.|\\\\|/|:|\*|"|<|>|→|')
            title =p.sub('',i.a['title'])
            turl = 'http:' + i.a['href']
            index = key + '|' + title
            data_cplink[index] = turl


def get_all_cartoon_cpdetails(key, value, data_cpldetial):
    itmp = key.split('|')
    lx, pnum, gname, cpname = itmp[0], itmp[1], itmp[2], itmp[3]
    print('获取***%s***第***%s***页***%s***%s***章节下每页详情链接地址' % (lx, pnum, gname, cpname))
    web_response = requests.get(value)
    web_soup = BeautifulSoup(web_response.content, 'html.parser')
    if web_soup.find('div', class_='ye'):
        all_pages = web_soup.find('select', class_="ye_select")
        for i in all_pages:
            if isinstance(i, bs4.element.Tag):
                tmp = list(value)
                tmp.insert(-1, '-' + i['value'])
                pic_url = ''.join(tmp)
                pic_response = requests.get(pic_url)
                pic_soup = BeautifulSoup(pic_response.text, 'html.parser')
                pic_page = pic_soup.find_all('script')
                for j in pic_page[4]:
                    p = re.compile('\?|\.|\\\\|/|:|\*|"|<|>|→|')
                    data = re.search('url.*', j).group()
                    img_url = data.replace('url: ', '')
                    img_name =p.sub('',pic_url.split('/')[-2])
                    index = key + '|' + img_name
                    data_cpldetial[index] = img_url
    else:
        all_pages = web_soup.find('div', class_="show_list show_join")
        if all_pages:
            for i in all_pages.ul:
                if isinstance(i, bs4.element.Tag):
                    p = re.compile('\?|\.|\\\\|/|:|\*|"|<|>|→|')
                    index = key + '|' + p.sub('',i.img['id'])
                    img_url = i.img['src'].strip('\'')
                    data_cpldetial[index] = img_url


if __name__ == '__main__':
    start_url = 'http://www.kuman.com/all/'
    img_dir = 'd:\\imgdir'
    # tag_url = get_all_tags_links(start_url)  # 标签首地址
    tag_url = {'玄幻': 'http://www.kuman.com/all-tag-xuanhuan/'}

    # 标签分页链接地址
    data_tgpl = Manager().dict()
    tag_pool = Pool(processes=50)
    for key in tag_url:
        tag_pool.apply_async(get_all_tag_page_links, args=(key, tag_url[key], data_tgpl))
    tag_url.clear()
    tag_url.clear()
    tag_pool.close()
    tag_pool.join()

    # 获取分类分页中的cartoon首页地址
    data_ctindex = Manager().dict()
    cindex_pool = Pool(processes=50)
    for key in dict(data_tgpl):
        cindex_pool.apply_async(get_all_cartoon_index, args=(key, data_tgpl[key], data_ctindex))
    data_tgpl.clear()
    cindex_pool.close()
    cindex_pool.join()

    # 获取章节地址
    data_cplink = Manager().dict()
    cplink_pool = Pool(processes=50)
    for key in dict(data_ctindex):
        cplink_pool.apply_async(get_all_cartoon_cpages, args=(key, data_ctindex[key], data_cplink))
    data_ctindex.clear()
    cplink_pool.close()
    cplink_pool.join()

    # 获取章节下页面详情(图片地址)
    data_cpldetial = Manager().dict()
    cpldetial_pool = Pool(processes=50)
    for key in dict(data_cplink):
        cpldetial_pool.apply_async(get_all_cartoon_cpdetails, args=(key, data_cplink[key], data_cpldetial))
    data_cplink.clear()
    cpldetial_pool.close()
    cpldetial_pool.join()

    # 保存文件
    print('正在保存信息............')
    recordfile = img_dir + '\\tmp_record.txt'
    if os.path.exists(recordfile):
        os.remove(recordfile)
    for key in dict(data_cpldetial):
        with open(recordfile, 'a') as f:
            f.write(key + '\t' + data_cpldetial[key]+'\n')

    # 建立文件夹
    print('正在创建目录............')
    for key in dict(data_cpldetial):
        tmp = key.split('|')
        dirname = img_dir + '\\' + tmp[0] + '\\' + tmp[2] + '\\' + tmp[3]
        make_dir(dirname)

    # 下载图片并保存
    download_pool = Pool(processes=50)
    for key in dict(data_cpldetial):
        tmp = key.split('|')
        file_name = img_dir + '\\' + tmp[0] + '\\' + tmp[2] + '\\' + tmp[3] + '\\' + tmp[4] + '.jpeg'
        download_pool.apply_async(download_all_pic, args=(file_name, data_cpldetial[key], len(data_cpldetial)))
    download_pool.close()
    download_pool.join()
    data_cpldetial.clear()
    print('^*^^*^^*^%s网站上的所有动漫图片爬取完毕！^*^^*^^*^' % start_url)
