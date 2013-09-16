#encoding:utf-8
#login wei xin
#author: Aron @ SKLSE

import httplib
import hashlib
import urllib
import re
import json

host_name = "mp.weixin.qq.com"
host_url = "/cgi-bin/login?lang=zh_CN"

h = hashlib.md5()

headers = {
        "Host":"mp.weixin.qq.com",
        "Origin":"https://mp.weixin.qq.com",
        "Referer":"https://mp.weixin.qq.com/",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest"
    }

def login_weixin(username, password):
    """login weixin
        username: your username
        password: your password:
        
        password should be decoded by md5, and then post username,pwd,and some 
        other params to the target url
    """
    
    request_dict = {"username" : '',
        'pwd' :'',
        'imagecode' : '',
        'f' : 'json',
        'register' : 0}

    h.update(password)
    request_dict['username'] = username
    request_dict['pwd'] = h.hexdigest()
    print request_dict
    body = urllib.urlencode(request_dict)
    try:
        httpClient = httplib.HTTPSConnection(host_name, 443)
        httpClient.request("POST", host_url, body, headers)
    except Exception, e:
        print e
    res = httpClient.getresponse()
    json_content = json.loads(res.read())
    print json_content
    cookies = res.getheader('Set-Cookie')
    print cookies
    import string
    cookies = string.replace(cookies, "Path=/;", "")
    slave_user = re.findall(r"(?P<tips>slave_user=.+?;)", cookies)
    slave_sid = re.findall(r"(?P<tips>slave_sid=.+?;)", cookies)
    new_cookie = ''.join(slave_user)
    new_cookie += ' '.join(slave_sid) 
    token = re.findall(r"token=(?P<tips>\d+)?", json_content['ErrMsg'])
    token = ''.join(token)
    return new_cookie, token

def get_member_list(token, fromfakeid, new_cookie):
    """get the member list who have sent message to you
    token: token
    fromfakeid: need to find it in your information html page:
        https://mp.weixin.qq.com/cgi-bin/userinfopage?t=wxm-setting&lang=zh_CN&token=780263817
    
    return a json object    
    """
    try:
        headers['Cookie'] = new_cookie
        headers['Referer'] = "https://mp.weixin.qq.com/cgi-bin/singlemsgpage" + \
            "?fromfakeid=1454670442&count=20&t=wxm-singlechat&token=%s" % str(token) + \
            "&token=%s&lang=zh_CN" % str(token)
        http_client_home = httplib.HTTPSConnection(host_name, 443)
        http_client_home.request("GET", 
                '/cgi-bin/message?t=message/list&count=20&day=7&token=%s&lang=zh_CN' % str(token), 
                "",headers)
    except Exception,e:
         print e
    res_home = http_client_home.getresponse()
    msg_item = re.findall(r"list : (?P<tips>[\w\W]+?)\.msg_item", res_home.read())
    msg_item = ''.join(msg_item)
    msg_item = msg_item[1 : len(msg_item) - 1]
    msg_json = json.loads(msg_item)
    return msg_json


def send_msg(content, token, to_fake_id, new_cookie):
    send_msg_dict = {
            'type' : '1',
            'content' : content,
            'error' : 'false',
            'imgcode' : '',
            'tofakeid' : to_fake_id,
            'token' : token,
            'ajax' : '1'
        }
    send_body = urllib.urlencode(send_msg_dict)
    try:
        headers['Cookie'] = new_cookie
        headers['Referer'] = "https://mp.weixin.qq.com/cgi-bin/singlemsgpage?" + \
                "msgid=&source=&count=20&t=wxm-singlechat&fromfakeid=1454670442&token=%s&lang=zh_CN" % str(token)
        http_client_home = httplib.HTTPSConnection(host_name, 443)
        http_client_home.request("POST", 
                'https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&lang=zh_CN&token=%s' % str(token), 
                send_body,headers)
    except Exception,e:
         print e
    res_home = http_client_home.getresponse()
    
    print res_home.read().decode('utf-8')
    

if __name__ == '__main__':
    cookie, token = login_weixin(your_user_name, your_pwd)
    member_list = get_member_list(token, None, cookie)
    print member_list
    
    for member in member_list['msg_item']:
        print member
        send_msg("nihao", token, member['fakeid'], cookie)
    
        
