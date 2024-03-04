import requests

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from ..utils import utility

router = APIRouter()

class User(BaseModel):
    id: int
    name: str
    screen_name: str


class Tweet(BaseModel):
    text: str
    urls: list[HttpUrl]
    user: User


cookie = 'g_state={"i_l":0}; kdt=J9R7RlQlvvYhdpzghHjL0GpWKnEU29YKIF9pgUJA; dnt=1; night_mode=1; guest_id=v1%3A170670094493013297; auth_token=3f60e449a94463c2c8170699b01826bf27d88294; ct0=025d98f496cec2f5a2622d3784b4a463151a25ad1a8e75876e142bc3a6b196a2672fd915d9e873efd73d811a11482b876e4f5c0be257a30ba66cd76856d5de326cda06fd3cc12fa5753cf3ac763d0f81; twid=u%3D1752658905061023744; guest_id_marketing=v1%3A170670094493013297; guest_id_ads=v1%3A170670094493013297; lang=en; _ga=GA1.2.1290914450.1707439141; _gid=GA1.2.1430732305.1707439141; personalization_id="v1_9ye2TKwH1qjHJ3v3SKkg8w=="'
authorization = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

class MyAuth(requests.auth.AuthBase):
    def __call__(self, r):
        # Implement my authentication
        global cookie
        i = cookie.find('ct0=')
        ct0 = cookie[i+4: cookie.find('; ', i)]
        
        r.headers['Cookie'] = cookie
        r.headers['Authorization'] = authorization
        r.headers['X-Csrf-Token'] = ct0
        return r
    

@router.get('/tweet-detail/{tweet_id}', response_model=Tweet)
async def tweet_detail(tweet_id: int):
    url = 'https://twitter.com/i/api/graphql/7xdlmKfKUJQP7D7woCL5CA/TweetDetail'
    params = dict(
        variables = {
            "focalTweetId": str(tweet_id),
            "with_rux_injections": False,
            "includePromotedContent":True,
            "withCommunity":True,
            "withQuickPromoteEligibilityTweetFields":True,
            "withBirdwatchNotes":True,
            "withVoice":True,
            "withV2Timeline":True
        },
        features = {
            "responsive_web_graphql_exclude_directive_enabled":True,
            "verified_phone_label_enabled":False,
            "responsive_web_home_pinned_timelines_enabled":True,
            "creator_subscriptions_tweet_preview_api_enabled":True,
            "responsive_web_graphql_timeline_navigation_enabled":True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
            "tweetypie_unmention_optimization_enabled":True,
            "responsive_web_edit_tweet_api_enabled":True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
            "view_counts_everywhere_api_enabled":True,
            "longform_notetweets_consumption_enabled":True,
            "responsive_web_twitter_article_tweet_consumption_enabled":False,
            "tweet_awards_web_tipping_enabled":False,
            "freedom_of_speech_not_reach_fetch_enabled":True,
            "standardized_nudges_misinfo":True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":True,
            "longform_notetweets_rich_text_read_enabled":True,
            "longform_notetweets_inline_media_enabled":True,
            "responsive_web_media_download_video_enabled":False,
            "responsive_web_enhance_cards_enabled":False
        },
        fieldToggles = {"withArticleRichContentState":False}
    )
    res = requests.get(url, json=params, auth=MyAuth())
    res.raise_for_status()

    def max_bitrate(variants)->str:
        max = [0, '']
        for v in variants:
            br = int(v.get("bitrate") or 0)
            if br > max[0]:
                max[0] = br
                max[1] = v['url']
        return max[1]
    
    urls = []
    text = ''
    user = {}

    try:
        instructions = res.json()['data']['threaded_conversation_with_injections_v2']['instructions']
    except KeyError as err:
        raise HTTPException(404, {err.__class__.__name__: err.args})
    for ins in instructions:
        if ins['type'] == 'TimelineAddEntries':
            result = ins['entries'][0]['content']['itemContent']['tweet_results']['result'].get('tweet')
            if not result:
                result = ins['entries'][0]['content']['itemContent']['tweet_results']['result']
            break

    if 'extended_entities' in result['legacy']:
        for media in result['legacy']['extended_entities']['media']:
            if media['type'] == 'video':
                urls.append(max_bitrate(media['video_info']['variants']))
            else: #media['type'] == 'photo':
                urls.append(media['media_url_https'])

    text = utility.handle_title(result['legacy']["full_text"])
    user['id'] = result["core"]["user_results"]["result"]["rest_id"]
    user['name'] = result["core"]["user_results"]["result"]["legacy"]["name"]
    user['screen_name'] = result["core"]["user_results"]["result"]["legacy"]["screen_name"]

    return {
        'text': text,
        'urls': urls,
        'user': user
    }