# -*- coding: utf-8 -*-

class CookiesUtil(object):
    anjuke_cookies = {
        'aQQ_ajkguid': '53AF0A50-2028-B38D-2CF1-C1BF7192E9FB',
        'ctid': '107 ',
        '_ga': 'GA1.2.225350737.1513871159',
        '58tj_uuid': 'd169abf8-5750-4213-920a-45eb37c93d6c',
        'new_uv': '22',
        'als': '0',
        'isp': 'true',
        'Hm_lvt_c5899c8768ebee272710c9c5f365a6d8': '1514165902,1514254898,1514277658,1514290019',
        'propertys': 'hsc6vq-p1kjyo_hma9vh-p1kjwl_hsdv51-p1imkz_hrq03t-p1gikw_ho3ljw-p1d0bn_hrgotk-p1biu2_hl4eya-p1bira_',
        '_gid': 'GA1.2.725257540.1514083348',
        'lp_lt_ut': '021fa876ce247b517f560d90d3eb6059',
        'lps': 'http%3A%2F%2Fwww.anjuke.com%2F%7Chttps%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DgsRWoaewpLFwpt3HAjNVTMEmqlFR06kYZ82265g8vTy%26wd%3D%26eqid%3De9f806740001db48000000065a428211',
        'sessid': 'D0458865-F228-5FAC-5CB3-7F3DEFC98A5A',
        'twe': '2',
        'new_session': '0',
        'init_refer': 'https%253A%252F%252Fwww.anjuke.com%252Fsy-city.html',
        '_gat': '1'
    }

    lianjia_cookies = {
        'lianjia_ssid': 'e66a1010-a917-4218-8809-1bd598ca605e',
        'lianjia_uuid': 'a489c10f-7f3d-4fec-b247-edf25a508ea8',
        'UM_distinctid': '16344009b26449-0d9b9101123a8-1269624a-100200-16344009b28362',
        '_ga': 'GA1.2.446607003.1525854286',
        '_gid': 'GA1.2.1498763228.1525854286',
        'select_city': '110000',
        'Hm_lvt_9152f8221cb6243a53c83b956842be8a': '1525854421',
        'Hm_lpvt_9152f8221cb6243a53c83b956842be8a': '1525855786',
        '_smt_uid': '5af2b0d5.514d7fb0',
        'lj_newh_session': 'eyJpdiI6IlN1OTR6djNqN1doRTIzWlhzOWtWQXc9PSIsInZhbHVlIjoiSitrR0JLSWNzMkRFeFFGODNKK0FUc043TWtSWU1IdmF2bjNhZkVPZ2loNlZwMlJDbHorSGtNYUNOZ3duVThaUmtWZDRzbDg0MU1PYVFDMHZ3WWVDMGc9PSIsIm1hYyI6IjBiZWMzYWM3YWEwY2MxMzBhYTdjODJhYmZjY2Q4MTY5MTU4OWI4OTgyMDAwMjQ2Zjk3ZWQ2MTRlNWM5ODVmOWYifQ%3D%3D',
        'bj-fang': '8c8ce474060227ca5350c751b887aca2',
        'CNZZDATA1256144455': '1406150244-1525854429-https%253A%252F%252Fbj.lianjia.com%252F%7C1525854429',
        'CNZZDATA1254525948': '217203270-1525850693-https%253A%252F%252Fbj.lianjia.com%252F%7C1525850693',
        'CNZZDATA1255633284': '1742035927-1525849986-https%253A%252F%252Fbj.lianjia.com%252F%7C1525855389',
        'CNZZDATA1255604082': '312971672-1525852042-https%253A%252F%252Fbj.lianjia.com%252F%7C1525852042',
        '_jzqa': '1.3072597150186070500.1525854874.1525854874.1525854874.1',
        '_jzqb': '1.1.10.1525854874.1',
        '_jzqc': '1',
        '_jzqckmp': '1',
        '_qzja': '1.27179688.1525854873990.1525854873990.1525854873990.1525854873990.1525854873990.0.0.0.1.1',
        '_qzjb': '1.1525854873990.1.0.0.0',
        '_qzjc': '1',
        '_qzjto': '1.1.0',
        '_jzqa': '1.1315966401797259000.1525855475.1525855475.1525855475.1',
        '_jzqb': '1.2.10.1525855475.1',
        '_jzqc': '1',
        '_jzqckmp': ''
    }

    @classmethod
    def get_anjuke_cookies(cls):
        return cls.anjuke_cookies

    @classmethod
    def get_lianjia_cookies(cls):
        return cls.lianjia_cookies