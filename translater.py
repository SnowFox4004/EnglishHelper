import hashlib
import os
import random
import time
import requests
import uuid
from lxml import etree
from datetime import datetime

def ascii_all(x):
    for i in x:
        if ord(i) > 128:
            return False
    return True


def get_translate2(content):
    content = content.strip()
    if not ascii_all(content):
        type = 'zh-CHS2en'
    else:
        type = 'en2zh-CHS'
    url = 'https://www.youdao.com/w/' + content + '/#keyfrom=dict2.top'
    try:
        r = requests.get(url).content.decode()
    except:
        return {'errorcode': -1}

    html = etree.HTML(r)
    means = html.xpath('//div[@class="trans-container"]')
    result = []

    for meaning in means:
        result.append(meaning.xpath('ul/li/text()'))
    if len(result[0]) == 0:
        for meaning in means:
            me = meaning.xpath('p[2]/text()')
            result.append(me)

    if len(result[0]) == 0:
        for meaning in means:
            me = meaning.xpath('ul/p/span/a/text()')
            result.append(me)
    if len(result[0]) == 0:
        return str({'errorCode': -2})

    result = [i for i in result if i]

    return str({'translateResult': [[{'tgt': result[0][0], 'src': content}]], 'smartResult': {'entries': result[0][1:]},
                'errorCode': 0, 'type': type})


def get_sas(content):
    r = str(round(time.time() * 1000))
    salt = r + str(random.randint(0, 9))

    data = 'fanyideskweb' + content + salt + 'Tbh5E8=q6U3EXe+&L[4c@'
    sign = hashlib.md5()
    sign.update(data.encode('utf-8'))

    sign = sign.hexdigest()

    return content, salt, sign


def get_sas2(content):
    r = str(round(time.time() * 1000))
    salt = str(uuid.uuid1())

    data = '07cdf5a2a24a4a2a' + content + salt + 'AqfoyPZuwiUyYUg9i3oYIqH5z2c6QceN'
    print(data)
    sign = hashlib.md5()
    sign.update(data.encode('utf-8'))

    sign = sign.hexdigest()
    data = {}
    data['langType'] = 'auto'
    data['appKey'] = '07cdf5a2a24a4a2a'
    data['q'] = content
    data['salt'] = salt
    data['sign'] = sign

    return content, salt, sign, data


def send_request(content, salt, sign):
    try:

        url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID=2021917549@10.110.96.154;OUTFOX_SEARCH_USER_ID_NCOO=\
                   1521146224.80111;JSESSIONID=aaaw274i5-Xghdy8Ll59x;___rl__test__cookies=1647006266673',
            'Referer': 'https://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'
        }
        params = {
            'i': str(content),
            'from': "AUTO",
            'to': 'AUTO',
            'smartresult': "dict",
            'client': 'fanyideskweb',
            'salt': str(salt),
            'sign': str(sign),

            'version': '2.1',
            'keyfrom': 'fanyi.web',

        }

        r = requests.post(url=url, headers=headers, data=params)

        print(r.content.decode())
        return r.content.decode()
    except:
        return "{'errorCode':-1}"


def get_translate(content):
    c, s, si = get_sas(content)
    result = send_request(c, s, si)
    return result


def get_voice(content, salt, sign, data):
    url = 'https://openapi.youdao.com/ttsapi'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, headers=headers, data=data)
    return r

def file_name_make(content : str):
    replaces=['.','?','/','\\','*','<','>','|',':','"']
    for i in replaces:
        content=content.replace(i,'')

    return content

def get_voice2(content, ):
    url = f'https://tts.youdao.com/fanyivoice?word={content}&le=auto&keyfrom=speaker-target'
    try:
        r = requests.get(url)
    except:
        return '-1'
    filename= file_name_make(content)
    filename= filename[:10]
    open(f'./Voice/{filename}.mp3', 'wb+').write(r.content)

    return f'./Voice/{filename}.mp3'


if __name__ == '__main__':
    os.startfile(get_voice2('''
    The Tibetan antelope is one of the protected animals in China. There are only about 70-100 thousand Tibetan antelopes left now. They live in some of the most inaccessible parts of the Tibetan Plateau. The Tibetan antelopes have strong vitality that they can live in places where human beings can’t live. However, they are in danger now. 
Some people love the fur of Tibetan antelope and they want to buy some clothes made of their fur at a very high price. So some businessmen plan to kill some Tibetan antelope secretly and sell their fur. Since the 1970s, millions of Tibetan antelopes have been killed by illegal hunters. After killing them, those hunters skin them and leave the Tibetan antelopes' bodies behind. Then the hunters sell the fur to businessmen. They can make a lot of money by killing the poor Tibetan antelopes. So there were more and more people coming to kill Tibetan antelopes, and the number of Tibetan antelopes is quickly decreasing. 
The Secretary of the Zhiduo county, (索南达杰) was born in 1954. He is a member of the Chinese communist party. After graduating from Qinghai Institute for Nationalities, he came back to his hometown to help. He worked really hard to develop his hometown. Because of the situation of poaching, he organized an animal protection team to help the animals there. 
In 1994, (索南达杰) and four team members went to Hoh Xil to catch poachers. They captured 7 cars, 20 illegal hunters and more than 1800 skins of Tibetan antelope. While they were bringing the hunters back, they were attacked by the poachers. (索南达杰) fought with 18 armed poachers with a small gun. He stayed in Hoh Xil forever, frozen into an ice sculpture in temperatures of minus 40 degrees Celsius. He became the hero of all people. He died when he was 40 years old. After he was killed, the government set up a nature reserve called “Coco Siri Provincial Nature Reserve". After learning (索南达杰) ‘s story, I was shocked by his bravery and the shameless of the poachers. We may not be able to fight with them, but we must stop buying things made of animals in danger. It’s no use to buying clothes made from Tibetan antelopes and it may put Tibetan antelopes in danger. When the buying stops, the killing can too. We must do something for those animals in danger!
'''.replace('\n','')).replace('/', '\\'))
