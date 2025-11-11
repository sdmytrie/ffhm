import datetime
import json
from pprint import pprint

import pymongo
import requests
import settings
from utils import get_token


def main():
    TOKEN = get_token.get_jwt()["token"]
    URL = "https://intranet.ffhaltero.fr/api/v1/scoresheet/getlicencies"
    headers = {"accept": "application/json", "Authorization": "Bearer " + TOKEN}

    response = requests.get(URL, headers=headers)
    client = pymongo.MongoClient("mongo", 27017)
    db = client.exalto
    collection = db.concurrent
    for entry in response.json()["OK"]["msg"]:
        document = {
            "updatedAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "result": json.loads(json.dumps(entry)),
        }
        exalto = collection.update_one(
            {
                "licence": entry["code_adherent"]
                + "-"
                + entry["licence"]["type"]["code"]
            },
            {
                "$set": {
                    "licence": entry["code_adherent"]
                    + "-"
                    + entry["licence"]["type"]["code"],
                    "concurrent": document,
                }
            },
            upsert=True,
        )


if __name__ == "__main__":
    main()
