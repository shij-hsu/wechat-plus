# -*- coding:utf-8 -*-
'''
此程序用来实现和机器人聊天
'''
import time, re
import itchat
from itchat.content import *

xiaobing_username = ur""
my_username = ur''

# 聊天队列，用来存储小冰的聊天记录
users_queue = {}
current_chat_user = None

# 此词典用来存储对好友的称呼
my_nick_name = {
    ur'Apocalypse': ur'本尊',
    ur'春华秋实': ur'分身',
    ur'华韵琴行双湖店': ur'小姐姐',
    ur'黄锴': ur'黄锴',
    ur'随便': ur'爸爸',
    ur'吉祥如意': ur'妈妈',
    ur'蒋瀚如': ur'蒋师兄',
    ur'Victor': ur'蒋师兄',
    ur'鲤🎏': ur'部长',
    ur'Bobobob': ur'罗师姐',
    ur'猫语猫寻': ur'唐师姐',
    ur'Adele': ur'亚倩',
    ur'超←重↓栗↑': ur'罗师姐',
    ur'腾原': ur'周师兄',
    ur'风清雨柔': ur'必红哥',
    ur'孙小全': ur'孙师兄',
    ur'李朝晖': ur'李师兄',
    ur'世纪宝鼎': ur'马师兄',
    ur'桑榆扬': ur'桑师兄',
    ur'梦相游': ur'老表',
    ur'张承胜': ur'舅舅',
    ur'莫愁·杨莫愁': ur'莫愁师姐',
    ur'轩': ur'何轩'
}


# 得到发消息者的nickname
def get_nick_name(from_user_name):
    return itchat.search_friends(userName=from_user_name)['NickName']


def time_to_period(t):
    if t.tm_hour < 11:
        return ur'上午好'
    elif t.tm_hour < 13:
        return ur'中午好'
    elif t.tm_hour < 18:
        return ur'下午好'
    else:
        return ur'晚上好'


# 自己的消息处理函数，处理微软小冰返回的消息
def my_send_msg(msg, user):
    msg_type = msg['Type']
    if msg_type == 'Text':
        itchat.send(msg['Content'], user)
    elif msg_type == 'Picture':
        msg['Text'](msg['FileName'])
        itchat.send_image(msg['FileName'], user)
    elif msg_type == 'Recording' or msg_type == 'Attachment':
        msg['Text'](msg['FileName'])
        itchat.send_file(msg['FileName'], user)
    elif msg_type == 'Video':
        msg['Type'](msg['FileName'])
        itchat.send_video(msg['FileName'], user)
    else:
        itchat.send(msg['Contetn'], user)


# 返回微软小冰的公众号UserName
def get_xiaobing_username():
    mps = itchat.get_mps()
    for mp in mps:
        if mp['NickName'] == ur'小冰':
            return mp['UserName']


# 返回自己的UserName
def get_myself_username():
    frds = itchat.get_friends()
    for frd in frds:
        if frd['NickName'] == ur'Apocalypse':
            return frd['UserName']


@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, NOTE], isMpChat=True,
                     isFriendChat=True)
def revocation(msg):
    global xiaobing_username, my_username, users_queue, current_chat_user

    # 命令行记录消息
    if msg['FromUserName'] != xiaobing_username:
        mytime = time.localtime()
        msg_time_touser = mytime.tm_year.__str__() \
                          + "/" + mytime.tm_mon.__str__() \
                          + "/" + mytime.tm_mday.__str__() \
                          + "/" + mytime.tm_hour.__str__() \
                          + ":" + mytime.tm_min.__str__() \
                          + ":" + mytime.tm_sec.__str__()
        msg_id = msg['MsgId']
        msg_time = msg['CreateTime']
        msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
        msg_type = msg['Type']
        msg_content = None
        msg_url = None
        if msg['Type'] == 'Text':
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg['Text']
        elif msg['Type'] == 'Picture':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])

            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + ur'，图片已缓存'
        elif msg['Type'] == 'Card':
            msg_content = msg['RecommendInfo']['NickName'] + ur' 的名片'

            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content
        elif msg['Type'] == 'Map':
            x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*",
                                       msg['OriContent']).group(1, 2, 3)
            if location is None:
                msg_content = ur"纬度->" + x.__str__() + ur" 经度->" + y.__str__()
            else:
                msg_content = r"" + location
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content
        elif msg['Type'] == 'Sharing':
            msg_content = msg['Text']
            msg_url = msg['Url']
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + 'URL: %s' % msg_url
        elif msg['Type'] == 'Recording':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + ur'，录音已缓存'
        elif msg['Type'] == 'Attachment':
            msg_content = r'' + msg['FileName']
            msg['Text'](msg['FileName'])
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + ur'，文件已缓存'
        elif msg['Type'] == 'Video':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + ur'，视频已缓存'
        elif msg['Type'] == 'Friends':
            msg_content = msg['Text']
            msg_content = '[%s] ' % msg_type + msg_time_touser + \
                          ", %d" % msg_time + " from " + msg_from + ": " + msg_content + ur'，请求添加好友'
        elif msg['Type'] == 'Note':
            msg_content = ur'[Note] %s' % msg['Content']

        print msg_content

    '''
    聊天部分
    '''

    # 如果是自己发的消息，就不管
    if msg['FromUserName'] == my_username:
        return
    # 如果是小冰发的消息，则处理之
    elif msg['FromUserName'] == xiaobing_username:
        # itchat.send(msg['Content'], current_chat_user)
        my_send_msg(msg, current_chat_user)
        return  # 必须返回

    try:
        if users_queue[msg['FromUserName']] == 0:
            if msg['Content'] == ur'1':  # 选择聊天
                users_queue[msg['FromUserName']] = 1
                itchat.send(ur'好的，您现在可以聊天了。', msg['FromUserName'])
            else:
                users_queue[msg['FromUserName']] = 2
                itchat.send(ur'好的，您现在可以留言了。', msg['FromUserName'])
        # 处于聊天模式
        elif users_queue[msg['FromUserName']] == 1 and msg['FromUserName'] != my_username:
            current_chat_user = msg['FromUserName']
            itchat.send(msg['Content'], xiaobing_username)
    except:
        msg_from = get_nick_name(msg['FromUserName'])
        if msg_from in my_nick_name:
            welcome = my_nick_name[msg_from]
        else:
            welcome = msg_from
        welcome += ur"%s" % time_to_period(mytime)
        itchat.send(ur'%s，我有事不在，请输入数字1.和机器人聊天2.给我留言  [本消息由机器人自动回复[耶][耶]]' % welcome, msg['FromUserName'])
        users_queue[msg['FromUserName']] = 0  # 0表示处于选择状态


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)

    xiaobing_username = get_xiaobing_username()
    my_username = get_myself_username()
    current_chat_user = None

    itchat.run()
