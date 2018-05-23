import requests,datetime
import json

#url에 대한 데이터를 json 타입으로 리턴해준다.
def get_json_result(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print('정상 경로가 아닙니다.',e)
        return '%s : Error for request[%s]' %(datetime.now(),url)

BASE_URL_FB_API = 'https://graph.facebook.com/v3.0'
ACCESS_TOKEN = 'EAACEdEose0cBAEVFyBkjwIqMUBlOKLCJelXRTKxXFaJsTAaLJOFGZAVDXO5GQZCnlBRPAJ35ZCnsMXF8QZAjhqumKzUfiJX17vfuP9slETsUmNSgXoiN8radZBqKLLrskGuthcItc8pZBqimdqZADo6irGiehZBejvTKHAJa8Y3LQXtadSACEIXyTl5Pcj4IZBxrIQNIqUcVb3QZDZD'
LIMIT_REQUEST = 20
pagename = ''
from_date = '2018-05-20'
to_date = '2018-05-23'

#페이스북 페이지 네임을 통해 페이지의 id값을 구한다.(리턴한다)
def fb_name_to_id(pagename):
    base = BASE_URL_FB_API
    node = '/%s'%pagename   #node = 기본적인 사용자의 사진,페이지,댓글 같은 개별객체
    params = '/?access_token=%s'%ACCESS_TOKEN

    url = base+node+params
    id_result = get_json_result(url)

    return id_result['id']

def fb_get_post_list(pagename,from_date,to_date):
        # https://graph.facebook.com/v3.0/[Node, Edge]/?parameters
        page_id = fb_name_to_id(pagename)
        base = BASE_URL_FB_API
        node = '%s/post'% page_id
        fields = '/?fields=id,message,link,name,type,shares,created_time,comments.limit(0),summary(true),reactions.limit(0).summary(true)'
        duration = '&since=%s&until=%s'%(from_date,to_date)
        parameters = '&limit=%s&access_token=%s'%(LIMIT_REQUEST,ACCESS_TOKEN)
        url = base+node+fields+duration+parameters

        postList=[]
        isNext = True
        while isNext:
            tmpPostList = get_json_result(url)
            for post in tmpPostList['data']:
                postVO = preprocess_post(post)
                postList.append(postVO)

            paging= tmpPostList.get('paging').get('next')
            if paging !=None:
                url = paging
            else:
                isNext = False

        # save results to file
        with open("/Users/JS-K/Documents/json/" + pagename + ".json", 'w', encoding='utf-8') as outfile:
            json_string = json.dumps(postList, indent=4, sort_keys=True, ensure_ascii=False)
            outfile.write(json_string)

        return postList

def preprocess_post(post):
    #작성일 +9시간 맞추기
    created_time= post['created_time']
    created_time=datetime.strptime(created_time,'%Y-%m-%dT%H:%M:%S+0000')
    created_time= created_time + datetime.timedelta(hours=+9)
    created_time= created_time.strftime('%Y-%m-%d %H:%M:%S')

    if 'shares' not in post:
        shares_count=0
    else:
        shares_count = post['shares']['count']
        # 리액션수
    if 'reactions' not in post:
        reactions_count = 0
    else:
        reactions_count = post['reactions']['summary']['total_count']
        # 댓글수
    if 'comments' not in post:
        comments_count = 0
    else:
        comments_count = post['comments']['summary']['total_count']
        # 메세지 수
    if 'message' not in post:
        message_str = ''
    else:
        message_str = post['message']

    postVO ={
        'create_time': created_time,
        'shares_count': shares_count,
        'reactions_count': reactions_count,
        'comments_count': comments_count,
        'message_str': message_str
    }

    return postVO