import itchat
import requests
import time
from itchat.content import *
import pandas as pd
from pyecharts import Pie, Map, Style, Page, Bar


replied_friends={}




@itchat.msg_register([TEXT,PICTURE, RECORDING, VIDEO, SHARING])
def reply_content(msg):
    if my_status=='busy':
        return busy(msg)
    elif my_status=='robot':
        return robot(msg['Text'])

def busy(msg):
    if reply_cnt==-1:
        return busy_text
    else:
        if msg['FromUserName'] not in replied_friends:
            replied_friends[msg['FromUserName']]=reply_cnt-1
            return busy_text
        elif replied_friends[msg['FromUserName']]==0:
            return
        else:
            replied_friends[msg['FromUserName']]-=1
            return busy_text


def robot(text):
    chat_apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : '8edce3ce905a4c1dbb965e6b35c3834d', # 如果这个Tuling Key不能用，那就换一个
                                                            # 8edce3ce905a4c1dbb965e6b35c3834d
                                                            # eb720a8970964f3f855d863d24406576
                                                            # 1107d5601866433dba9599fac1bc0083
                                                            # 71f28bf79c820df10d39b4074345ef8c
        'info'   : text, # 这是我们发出去的消息
        'userid' : 'lucas', # 这里你想改什么都可以
    }
    # 我们通过如下命令发送一个post请求
    try:
        r = requests.post(chat_apiUrl, data=data).json()
        return r'宝贝'+r['text']
    except:
        return r'你让我说什么呢'


def get_friend():
    friends_list = itchat.get_friends()[1:]
    for friend in friends_list:
        itchat.send(friend['NickName'],friend['UserName'])
        time.sleep(.5)

def send_to_room(room_name,text):
    itchat.auto_login(hotReload=True)
    itchat.get_chatrooms()
    chat_rooms=itchat.search_chatrooms(name=room_name)
    if not chat_rooms:
        print(r'未找到此群聊')
        return
    else:
        chat_room=itchat.update_chatroom(chat_rooms[0]['UserName'])
        for friend in chat_room['MemberList']:
            itchat.send(text,friend['UserName'])
            time.sleep(0.5)


# 根据key值得到对应的信息
def get_key_info(friends_info, key):
    return list(map(lambda friend_info: friend_info.get(key), friends_info))


# 获得所需的微信好友信息
def get_friends_info():
    itchat.auto_login(hotReload=True)
    friends = itchat.get_friends()
    friends_info = dict(
        province=get_key_info(friends, "Province"),
        city=get_key_info(friends, "City"),
        nickname=get_key_info(friends, "Nickname"),
        sex=get_key_info(friends, "Sex"),
        signature=get_key_info(friends, "Signature"),
        remarkname=get_key_info(friends, "RemarkName"),
    )
    return friends_info


# 性别分析
def sex():
    friends_info = get_friends_info()
    df = pd.DataFrame(friends_info)
    sex_count = df.groupby(['sex'], as_index=True)['sex'].count()
    temp = dict(zip(list(sex_count.index), list(sex_count)))
    data = {}
    data['保密'] = temp[0]
    data['男'] = temp[1]
    data['女'] = temp[2]
    # 画图
    page = Page()
    attr, value = data.keys(), data.values()
    chart = Pie('微信好友性别比')
    chart.add('Sex', attr, value, center=[50, 50],
              redius=[30, 70], is_label_show=True, legend_orient='horizontal', legend_pos='center',
              legend_top='bottom', is_area_show=True, is_toolbox_show=False)
    page.add(chart)
    page.render('Sex.html')


# 省份分析
def country():
    friends_info = get_friends_info()
    df = pd.DataFrame(friends_info)
    province_count = df.groupby('province', as_index=True)['province'].count().sort_values()
    temp = list(map(lambda x: x if x != '' else '未知', list(province_count.index)))
    # 画图
    page = Page()
    attr, value = temp, list(province_count)
    chart1 = Map('好友分布(中国地图)',width=1100, height=600)
    chart1.add('好友数量', attr, value, is_label_show=True, is_visualmap=True,is_map_symbol_show=False,
               visual_text_color='#000', is_toolbox_show=False,maptype='china')
    page.add(chart1)
    chart2 = Bar('好友分布柱状图',width=900, height=500)
    chart2.add('好友数量', attr, value, is_stack=True, is_datazoom_show=True,mark_line=["min", "max"],
               label_pos='inside', is_legend_show=True, is_label_show=True, is_toolbox_show=False
               )
    page.add(chart2)
    page.render('Country.html')


# 具体省份分析
def province(province):
    friends_info = get_friends_info()
    df = pd.DataFrame(friends_info)
    df = df.query('province == "%s"' % province)
    city_count = df.groupby('city', as_index=True)['city'].count().sort_values()
    attr = list(map(lambda x: '%s市' % x if x != '' else '未知', list(city_count.index)))
    value = list(city_count)
    # 画图
    page = Page()
    chart1 = Map('%s好友分布' % province, width=1100, height=600)
    chart1.add('好友数量', attr, value, maptype='%s' % province, is_label_show=True,
               is_visualmap=True, visual_text_color='#000',is_map_symbol_show=False,is_toolbox_show=False)
    page.add(chart1)
    chart2 = Bar('%s好友分布柱状图' % province, width=900, height=500)
    chart2.add('好友数量', attr, value, is_stack=True, is_datazoom_show=True,mark_line=["min", "max"],
               label_pos='inside', is_legend_show=True, is_label_show=True, is_toolbox_show=False)
    page.add(chart2)
    page.render('Province.html')


if __name__=='__main__':
    flag=1
    while flag==1:
        print(r'1.自动回复 2.群发信息 3.好友地域 4.好友性别')
        f=input(r'输入序号后回车')
        if f=='1':
            my_status=input('1.忙碌 2.机器人(输入序号后回车)')
            if my_status=='1':
                my_status='busy'
                busy_text=input(r'回复内容，输入后回车，使用默认直接回车(默认为“忙碌中，此消息为自动回复”)')
                busy_text=busy_text or r'忙碌中，此消息为自动回复'
                reply_cnt=input(r'回复次数，输入后回车，使用默认直接回车(默认为1次,无限次输入-1)')
                try:
                    reply_cnt=int(reply_cnt)
                except:
                    reply_cnt=1
                itchat.auto_login(hotReload=True)
                itchat.run()
                flag=0
            elif my_status=='2':
                my_status='robot'
                itchat.auto_login(hotReload=True)
                itchat.run()
                flag=0
            else:
                print('请输入正确的序号')

        elif f=='2':
            room_name=input(r'输入想要群发的组名后回车')
            text=input(r'输入想要群发的信息后回车')
            send_to_room(room_name,text)
        elif f=='3':
            area=input(r'输入“全国”或具体省份如“北京”')
            if area=='全国':
                country()
            else:
                province(area)
        elif f=='4':
            print('好友性别分析')
            sex()
        else:
            print(r'请输入正确的序号')

        flag=int(input(r'输入1继续，其余退出'))



