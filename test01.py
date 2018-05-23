import requests,json
from datetime import datetime,timedelta

# url 을 주면 json  데이터를 리턴한다.
def get_json_result(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("정상 경로가 아닙니다.", e)
        return '%s : Error for request[%s]' % (datetime.now(), url)

BASE_URL_FB_API = 'https://graph.facebook.com/v3.0'
ACCESS_TOKEN = 'EAACEdEose0cBAOmUAcdD1smPzOBMZC4QEBZBhETzZCJhOeEC1Pej9hH8hv8H0fc8V2sIhcmwt1H6ZCjbwdPGfKOWrJP0HkSOSIZCMsk6aTOEBgcSGhC1A2kBidhgZBDZCVu37kdoNlTo7bz1YRvXXsWSAJpSX4rAROHGQAdZBWQHmHADuJW8AmEl4nBIPpX34hVkrrylAChWGgZDZD'
LIMIT_REQUEST = 20
pagename = 'chosun'
from_date = '2018-05-22'
to_date = '2018-05-23'
# 페이스북 페이지 네임을 주면 페이지 id값을 리턴해준당
def fb_name_to_id(pagename):
    base = BASE_URL_FB_API
    node = '/%s' % pagename
    params = '/?access_token=%s' % ACCESS_TOKEN
    url = base + node + params
    json_result = get_json_result(url)
    return json_result['id']

#페이스북 페이지네임, 시작날짜,끝날짜를 주면 json형태-->list형태로 데이터를 리턴해준다.

def fb_get_post_list(pagename,from_date,to_date):
    # https://graph.facebook.com/v3.0/[Node, Edge]/?parameters
    page_id = fb_name_to_id(pagename)
    base = BASE_URL_FB_API
    node = '/%s/posts' % page_id
    fields = "/?fields=id,message,link,name,type,shares,created_time,comments.limit(0).summary(true),reactions.limit(0).summary(true)"
    duration = '&since=%s&until=%s' % (from_date, to_date)
    parameters = '&limit=%s&access_token=%s' % (LIMIT_REQUEST, ACCESS_TOKEN)
    url = base+node+fields+duration+parameters

    postList=[]
    isNext=True
    while isNext:
        tmpPostList = get_json_result(url)      #json으로 된 문자열
        for post in tmpPostList['data']:        #전체 데이터에서 data만 잘라낸 것 - 하나씩 post에 넣어서 for문 돌린다.
            postVO = preprocess_post(post)       #post에서 meesageㅁ
            postList.append(postVO)

        # paging = tmpPostList['paging']['next']
        paging = tmpPostList.get('paging').get('next')
        if paging != None:
            url = paging
        else:
            isNext = False

    # save results to file
    with open("/Users/JS-K/Documents/json/" + pagename + ".json", 'w', encoding='utf-8') as outfile:
        json_string = json.dumps(postList, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(json_string)

    return postList

def preprocess_post(post):
    #작성일 +9시간 해줘야함
    created_time = post["created_time"]
    created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+0000')    #문자열 타입의 시간을 datetime식으로 바꿈
    created_time = created_time + timedelta(hours=+9)
    created_time = created_time.strftime('%Y-%m-%d %H:%M:%S')       # 문자열 타입으로 현재 시간 변환

    #공유수
    if 'shares' not in post:
        shares_count = 0
    else:
        shares_count = post['shares']['count']

    # 리액션수
    if 'reactions' not in post :
        reactions_count = 0
    else:
         reactions_count = post['reactions']['summary']['total_count']
    # 댓글수
    if 'comments' not in post :
        comments_count = 0
    else :
        comments_count = post['comments']['summary']['total_count']
    #메세지 수
    if 'message' not in post:
        message_str = ''
    else:
        message_str = post['message']

    postVO = {
                'create_time':created_time,
                'shares_count':shares_count,
                'reactions_count':reactions_count,
                'comments_count':comments_count,
                'message_str':message_str
            }
    return postVO

result = fb_get_post_list(pagename,from_date,to_date)

print(result)