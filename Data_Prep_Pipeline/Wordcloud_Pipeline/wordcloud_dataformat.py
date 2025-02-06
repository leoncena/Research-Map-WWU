import pymongo as pm
import os
import pandas as pd

CLIENT = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
DATABASE_LAKE = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
DATABASE_WEB = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Web")

def access_mongo_db(client, database):
    """
    Method to access the mongoDB
    :param client: Client mongoDB
    :param database: Name of database
    :return: connection to database
    """
    # connect to mongoDB
    my_client = pm.MongoClient(client)
    my_db = my_client[database]
    return my_db

def count_words(text_list):
    """
    Method to count the words, can be replaced with any other measurement for the wordcloud
    :param text_list: alle publication text data from the table
    :return: word with counts
    """
    word_counts = {}
    for text_dict in text_list:
        words = text_dict['data_for_wordcloud'].split(',')
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
    return sorted([{"text": word, "size": count} for word, count in word_counts.items()], key=lambda x: x['size'], reverse=True)

def push_to_MongoDB(client, database, data):
    """
    Method to push the data to the database
    :param client: Client mongoDB
    :param database: Name of database
    :param data: Any data that will push to the table worcloud institut
    """
    db = access_mongo_db(client, database)
    if "wordcloud_institut" in db.list_collection_names():
        db["wordcloud_institut"].delete_many({})
    db["wordcloud_institut"].insert_many(data)
    
def preprocess_WordCloud_data():
    """
    full method for exectuting the processing of word count and push to the datebase
    """
    db = access_mongo_db(CLIENT,DATABASE_LAKE)
    collection = db["publication_wordcloud_data"]
    data = list(collection.find({},{"data_for_wordcloud":1,"_id":0}))
    result = count_words(data)
    print(result[:100])
    push_to_MongoDB(CLIENT,DATABASE_WEB,result)


if __name__ == "__main__":

    preprocess_WordCloud_data()