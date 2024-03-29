import json
import boto3
import os
import sys
import uuid
import time
from botocore.vendored import requests
from requests.auth import HTTPBasicAuth
# import inflect

basic = HTTPBasicAuth('USER','Password')

ES_URL = 'ESURL'
REGION = 'us-east-1'


headers = {"Content-Type": "application/json"}
host = ES_URL
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)


SINGULAR_UNINFLECTED = ['gas', 'asbestos', 'womens', 'childrens', 'sales', 'physics']

SINGULAR_SUFFIX = [
    ('people', 'person'),
    ('men', 'man'),
    ('wives', 'wife'),
    ('menus', 'menu'),
    ('leaves', 'leaf'),
    ('us', 'us'),
    ('ss', 'ss'),
    ('is', 'is'),
    ("'s", "'s"),
    ('ies', 'y'),
    ('ies', 'y'),
    ('es', 'e'),
    ('s', '')
]
def singularize_word(word):
    for ending in SINGULAR_UNINFLECTED:
        if word.lower().endswith(ending):
            return word
    for suffix, singular_suffix in SINGULAR_SUFFIX:
        if word.endswith(suffix):
            return word[:-len(suffix)] + singular_suffix
    return word

def singular_labels(labels):
    for label in labels:
        singularize_word(label)
    return labels

def lambda_handler(event, context):

    print("EVENT --- {}".format(json.dumps(event)))
    q1 = event['queryStringParameters']['q']
    # if(q1 == "searchAudio"):
    #     q1 = convert_speechtotext()

    # p = inflect.engine()

    print("q1:", q1)
    singularize_word(q1)
    labels = get_labels(q1)
    single_labels = [singularize_word(plural) for plural in labels]

    word = "cats"
    cat = singularize_word(word)
    
    print("single_cat", single_labels)


    # for label in labels:
    #     singularize_word(label)
    #     print(label)
    
    print("single_label", single_labels)

    print("labels", labels)
    if len(single_labels) == 0:
        return
    else:
        img_paths = get_photo_path(single_labels)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'imagePaths': img_paths,
            'userQuery': q1,
            'labels': single_labels,
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        "isBase64Encoded": False
    }


def get_labels(query):
    response = lex.post_text(
        botName='PhotoAI',
        botAlias='photoBot',
        userId="test",
        inputText=query
    )
    print("lex-response", response)

    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print("slot: ", response['slots'])
        slot_val = response['slots']
        for key, value in slot_val.items():
            if value != None:
                labels.append(value)
    return labels


def get_photo_path(labels):
    img_paths = []
    unique_labels = []
    for x in labels:
        if x not in unique_labels:
            unique_labels.append(x)
    labels = unique_labels
    print("inside get photo path", labels)
    for i in labels:
        path = host + '/_search?q=labels:'+i
        print(path)
        response = requests.get(path, headers=headers,
                                auth=basic)
        print("response from ES", response)
        dict1 = json.loads(response.text)
        hits_count = dict1['hits']['total']['value']
        print("DICT : ", dict1)
        for k in range(0, hits_count):
            img_obj = dict1["hits"]["hits"]
            img_bucket = dict1["hits"]["hits"][k]["_source"]["bucket"]
            print("img_bucket", img_bucket)
            img_name = dict1["hits"]["hits"][k]["_source"]["objectKey"]
            print("img_name", img_name)
            img_link = 'https://s3.amazonaws.com/' + \
                str(img_bucket) + '/' + str(img_name)
            print(img_link)
            img_paths.append(img_link)
    print(img_paths)
    return img_paths

