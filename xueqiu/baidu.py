# -*- coding: utf-8 -*-

"""
xueqiu.baidu
~~~~~~~~~~~~

This module implements a baidu index.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

from .utils import get_cookies
from .utils import sess
from .utils import str2date
from . import api
import arrow
import requests
import pandas as pd

#https://github.com/Kandy990125/baidu_spider_master
#https://github.com/longxiaofei/spider-BaiduIndex/blob/master/new_spider_without_selenium/config.py
PROVINCE_CODE = {
    '山东':901, '贵州':902, '江西':903, '重庆':904, '内蒙古':905,
    '湖北':906, '辽宁':907, '湖南':908, '福建':909, '上海':910,
    '北京':911, '广西':912, '广东':913, '四川':914, '云南':915,
    '江苏':916, '浙江':917, '青海':918, '宁夏':919, '河北':920,
    '黑龙江':921, '吉林':922, '天津':923, '陕西':924, '甘肃':925,
    '新疆':926, '河南':927, '安徽':928, '山西':929, '海南':930,
    '台湾':931, '西藏':932, '香港':933, '澳门':934, '全国':0}

CITY_CODE = {
    '重庆市':'11', '上海市':'57', '北京市':'514', '天津市':'164', '香港区':'663', '澳门区':'664',
    #山东
    '济南': '1', '滨州': '76', '青岛': '77', '烟台': '78', '临沂': '79', '潍坊': '80',
    '淄博': '81', '东营': '82', '聊城': '83', '菏泽': '84', '枣庄': '85', '德州': '86',
    '威海': '88', '济宁': '352', '泰安': '353', '莱芜': '356', '日照': '366',
    #贵州
    '贵阳': '2', '黔南': '3', '六盘水': '4', '遵义': '59', '黔东南': '61',
    '铜仁': '422', '安顺': '424', '毕节': '426', '黔西南': '588',
    #江西
    '南昌': '5', '九江': '6', '鹰潭': '7', '抚州': '8', '上饶': '9', '赣州': '10',
    '吉安': '115', '萍乡': '136', '景德镇': '137', '新余': '246', '宜春': '256',
    #内蒙古
    '呼和浩特': '20', '包头': '13', '鄂尔多斯': '14', '巴彦淖尔': '15', '乌海': '16',
    '阿拉善盟': '17', '锡林郭勒盟': '19', '赤峰': '21', '通辽': '22', '呼伦贝尔': '25',
    '乌兰察布': '331', '兴安盟': '333',
    #湖北
    '武汉': '28', '黄石': '30', '荆州': '31', '襄阳': '32', '黄冈': '33', '荆门': '34',
    '宜昌': '35', '十堰': '36', '随州': '37', '恩施': '38', '鄂州': '39', '咸宁': '40',
    '孝感': '41', '仙桃': '42', '天门': '73', '潜江': '74', '神农架': '687',
    #辽宁
    '沈阳': '150', '大连': '29', '盘锦': '151', '鞍山': '215', '朝阳': '216', '锦州': '217',
    '铁岭': '218', '丹东': '219', '本溪': '220', '营口': '221', '抚顺': '222', '阜新': '223',
    '辽阳': '224', '葫芦岛': '225',
    #湖南
    '长沙': '43', '岳阳': '44', '衡阳': '45', '株洲': '46', '湘潭': '47', '益阳': '48',
    '郴州': '49', '湘西': '65', '娄底': '66', '怀化': '67', '常德': '68', '张家界': '226',
    '永州': '269', '邵阳': '405',
    #福建
    '福州': '50', '莆田': '51', '三明': '52', '龙岩': '53', '厦门': '54', '泉州': '55',
    '漳州': '56', '宁德': '87', '南平': '253',
    #广西
    '南宁': '90', '柳州': '89', '桂林': '91', '贺州': '92', '贵港': '93', '玉林': '118',
    '河池': '119', '北海': '128', '钦州': '129', '防城港': '130', '百色': '131',
    '梧州': '132', '来宾': '506', '崇左': '665',
    #广东
    '广州': '95', '深圳': '94', '东莞': '133', '云浮': '195', '佛山': '196', '湛江': '197',
    '江门': '198', '惠州': '199', '珠海': '200', '韶关': '201', '阳江': '202', '茂名': '203',
    '潮州': '204', '揭阳': '205', '中山': '207', '清远': '208', '肇庆': '209', '河源': '210',
    '梅州': '211', '汕头': '212', '汕尾': '213',
    #四川
    '成都': '97', '宜宾': '96', '绵阳': '98', '广元': '99', '遂宁': '100', '巴中': '101',
    '内江': '102', '泸州': '103', '南充': '104', '德阳': '106', '乐山': '107', '广安': '108',
    '资阳': '109', '自贡': '111', '攀枝花': '112', '达州': '113', '雅安': '114', '眉山': '291',
    '甘孜': '417', '阿坝': '457', '凉山': '479',
    #云南
    '昆明': '117', '玉溪': '123', '楚雄': '124', '大理': '334', '昭通': '335', '红河': '337',
    '曲靖': '339', '丽江': '342', '临沧': '350', '文山': '437', '保山': '438', '普洱': '666',
    '西双版纳': '668', '德宏': '669', '怒江': '671', '迪庆': '672',
    #江苏
    '南京': '125', '苏州': '126', '无锡': '127', '连云港': '156', '淮安': '157',
    '扬州': '158', '泰州': '159', '盐城': '160', '徐州': '161', '常州': '162',
    '南通': '163', '镇江': '169', '宿迁': '172',
    #浙江
    '杭州': '138', '丽水': '134', '金华': '135', '温州': '149', '台州': '287', '衢州': '288',
    '宁波': '289', '绍兴': '303', '嘉兴': '304', '湖州': '305', '舟山': '306',
    #青海
    '西宁': '139', '海西': '608', '海东': '652', '玉树': '659', '海南': '676', '海北': '682',
    '黄南': '685', '果洛': '688',
    #宁夏
    '银川': '140', '吴忠': '395', '固原': '396', '石嘴山': '472', '中卫': '480',
    #河北
    '石家庄': '141', '衡水': '143', '张家口': '144', '承德': '145', '秦皇岛': '146',
    '廊坊': '147', '沧州': '148', '保定': '259', '唐山': '261', '邯郸': '292', '邢台': '293',
    #黑龙江
    '哈尔滨': '152', '大庆': '153', '伊春': '295', '大兴安岭': '297', '黑河': '300',
    '鹤岗': '301', '七台河': '302', '齐齐哈尔': '319', '佳木斯': '320', '牡丹江': '322',
    '鸡西': '323', '绥化': '324', '双鸭山': '359',
    #吉林
    '长春': '154', '四平': '155', '辽源': '191', '松原': '194', '吉林': '270', '通化': '407',
    '白山': '408', '白城': '410', '延边': '525',
    #陕西
    '西安': '165', '铜川': '271', '安康': '272', '宝鸡': '273', '商洛': '274', '渭南': '275',
    '汉中': '276', '咸阳': '277', '榆林': '278', '延安': '401',
    #甘肃
    '兰州': '166', '庆阳': '281', '定西': '282', '武威': '283', '酒泉': '284', '张掖': '285',
    '嘉峪关': '286', '平凉': '307', '天水': '308', '白银': '309', '金昌': '343',
    '陇南': '344', '临夏': '346', '甘南': '673',
    #新疆
    '乌鲁木齐': '467', '石河子': '280', '吐鲁番': '310', '昌吉': '311', '哈密': '312',
    '阿克苏': '315', '克拉玛依': '317', '博尔塔拉': '318', '阿勒泰': '383', '喀什': '384',
    '和田': '386', '巴音郭楞': '499', '伊犁': '520', '塔城': '563', '克孜勒苏柯尔克孜': '653',
    '五家渠': '661', '阿拉尔': '692', '图木舒克': '693',
    #河南
    '郑州': '168', '南阳': '262', '新乡': '263', '开封': '264', '焦作': '265', '平顶山': '266',
    '许昌': '268', '安阳': '370', '驻马店': '371', '信阳': '373', '鹤壁': '374', '周口': '375',
    '商丘': '376', '洛阳': '378', '漯河': '379', '濮阳': '380', '三门峡': '381', '济源': '667',
    #安徽
    '合肥': '189', '铜陵': '173', '黄山': '174', '池州': '175', '宣城': '176', '巢湖': '177',
    '淮南': '178', '宿州': '179', '六安': '181', '滁州': '182', '淮北': '183', '阜阳': '184',
    '马鞍山': '185', '安庆': '186', '蚌埠': '187', '芜湖': '188', '亳州': '391',
    #山西
    '太原': '231', '大同': '227', '长治': '228', '忻州': '229', '晋中': '230', '临汾': '232',
    '运城': '233', '晋城': '234', '朔州': '235', '阳泉': '236', '吕梁': '237',
    #海南
    '海口': '239', '万宁': '241', '琼海': '242', '三亚': '243', '儋州': '244', '东方': '456',
    '五指山': '582', '文昌': '670', '陵水': '674', '澄迈': '675', '乐东': '679', '临高': '680',
    '定安': '681', '昌江': '683', '屯昌': '684', '保亭': '686', '白沙': '689', '琼中': '690',
    #西藏
    '拉萨': '466', '日喀则': '516', '那曲': '655', '林芝': '656', '山南': '677', '昌都': '678',
    '阿里': '691'}

AREAS = PROVINCE_CODE.copy()
AREAS.update(CITY_CODE)
sess.cookies = requests.cookies.merge_cookies(sess.cookies,
    get_cookies('.baidu.com', lazy=False))


class BaiduIndex:
    """Baidu search/feed/news index.

    Usage::

    >>> idx = BaiduIndex()
    >>> idx.search('股票',begin='-3m',area='上海')
    >>> idx.region_distribution('股票','-6w')  # 地域分布
    >>> idx.social_attribute('股票','-15d')  # 人群属性
    """
    cookie = None

    def __init__(self, keyword='', begin='-1m', end=arrow.now(), index='search', area='全国', cookie=''):
        self._keywords = keyword.find(',')>0 and keyword.split(',') or [keyword]
        self.start_date = arrow.get(str2date(begin).date())  # arrow.range includes the end date
        self.end_date = arrow.get(arrow.get(end).date())
        self.index_type = index
        self.area = area
        self.cookie = cookie or BaiduIndex.cookie
        self._key = None
        self._uniqid = None
        self._result = {kw: [] for kw in self._keywords}

    def search(self, keyword, *args, **kwargs):
        """Get keyword related baidu index data.

        :param keyword: baidu index for keyword.
        :param begin: (optional) start date, default is `-1m`.
        :param end: (optional) end date, default is `now`.
        :param index: (optional) index type, default is `search`.
            value: search, feed, news
        :param area: (optional) baidu index by region, default is `全国`.
            value: please see `AREAS` variable
        :param cookie: (optional) your cookie strings.
        :return: pd.DataFrame
        """
        self.__init__(keyword, *args, **kwargs)
        for st,ed in self.get_date_range(self.start_date, self.end_date):
            for d in self.get_encrypt_data(st, ed):
                encdata = d.get('all') or d
                self.end_date = arrow.get(encdata['endDate'])
                self._result[d.get('word') or d.get('key')] += \
                    self.decrypt(self.get_key(), encdata['data'])
        date_range = arrow.Arrow.range('day', self.start_date, self.end_date)
        self._result['date'] = pd.to_datetime([i.date() for i in date_range])
        self.result = pd.DataFrame(self._result).set_index('date')
        return self.result

    def region_distribution(self, keyword, *args, **kwargs):
        """region distribution statistics. 地域分布"""
        self.__init__(keyword, *args, **kwargs)
        params = {'region': AREAS[self.area],
                  'word': ','.join(self._keywords),
                  'startDate': self.start_date.format('YYYY-MM-DD'),
                  'endDate': self.end_date.format('YYYY-MM-DD')}
        cookie = self.cookie and {'Cookie': self.cookie} or {}
        resp = sess.get(api.baidu_region, params=params, headers=cookie).json()
        self.region = {i['key']: {'city':i['city'], 'prov':i['prov'], 'period':i['period']}
            for i in resp['data']['region']}
        return self.region

    def social_attribute(self, keyword, *args, **kwargs):
        """social attribute statistics. 人群属性(年龄分布, 性别分布)"""
        self.__init__(keyword, *args, **kwargs)
        params = {'wordlist': ','.join(self._keywords),
                  'startdate': self.start_date.format('YYYYMMDD'),
                  'enddate': self.end_date.format('YYYYMMDD')}
        cookie = self.cookie and {'Cookie': self.cookie} or {}
        resp = sess.get(api.baidu_social, params=params, headers=cookie).json()
        self.social = {i['word']: {'age':i['str_age'], 'sex':i['str_sex']} for i in resp['data']}
        return self.social

    def get_encrypt_data(self, start_date, end_date):
        """get encrypted data."""
        idx = {'search': api.baidu_search_index,
               'feed': api.baidu_feed_index,
               'news': api.baidu_news_index}
        params = {'area': AREAS[self.area],
                  'word': ','.join(self._keywords),
                  'startDate': start_date.format('YYYY-MM-DD'),
                  'endDate': end_date.format('YYYY-MM-DD')}
        cookie = self.cookie and {'Cookie': self.cookie} or {}
        resp = sess.get(idx[self.index_type], params=params, headers=cookie)
        #status: 0 ok, 10000 no login, 10002 bad request
        data = resp.json()['data']
        self._uniqid = data['uniqid']
        encrypt_data = data.get('userIndexes') or data.get('index')
        return encrypt_data

    def get_key(self):
        cookie = self.cookie and {'Cookie': self.cookie} or {}
        resp = sess.get(api.baidu_data_key, params={'uniqid':self._uniqid}, headers=cookie)
        self._key = resp.json()['data']
        return self._key

    @staticmethod
    def get_date_range(start, end):
        """date range is one year."""
        start = arrow.get(start)
        end = arrow.get(end)
        if start.shift(years=1) > end:
            return [(start, end)]
        date_range = []
        for i in arrow.Arrow.range('year', start, end):
            if i == end: break
            tmp = end if i.shift(years=1)>=end else i.shift(years=1,days=-1)
            date_range.append((i, tmp))
        return date_range

    @staticmethod
    def decrypt(key, data):
        """decrypt data."""
        kv = {key[i]: key[len(key)//2+i] for i in range(len(key)//2)}
        dec = ''.join([kv[i] for i in data])
        return dec.split(',')