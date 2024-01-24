from datetime import datetime
import os
import uuid
import pymongo

import config


class ContentService:
    def __init__(self):
        pass

    def get_all_content(self):
        _, content_collection = self.get_collections()

        contents = content_collection.find()
        
        return contents

    def get_content(self, content_id):
        _, content_collection = self.get_collections()

        content = content_collection.find_one({"id": content_id})

        return content

    def get_playlists_for_content(self, content_id):
        all_playlists = self.get_playlists()
        
        content_playlists = []

        # if the content is in the playlist, add it to the list
        for playlist in all_playlists:
            for playlist_item in playlist["content"]:
                if playlist_item["id"] == content_id:
                    content_playlists.append(playlist)
                
        return content_playlists
        
    def update_playlists_content(self, content_id, playlist_ids):

        metadata_collection, _ = self.get_collections()
        playlists_doc = metadata_collection.find_one({"name": "playlists"})

        # enumerate the playlists and update the content in each when needed
        for playlist in playlists_doc["playlists"]:
            if playlist["id"] in playlist_ids:
                # add the content to the playlist if it is not already there
                if content_id not in playlist["content"]:
                    playlist["content"].append(content_id)
            # remove the content from the playlist if it is there
            elif content_id in playlist["content"]:
                playlist["content"].remove(content_id)

        metadata_collection.update_one({"name": "playlists"}, {"$set": playlists_doc})
        
    def add_content(self, content):
        _, content_collection = self.get_collections()

        content_collection.insert_one(content)

    def update_content(self, content_to_update):

        _, content_collection = self.get_collections()

        content_id = content_to_update["id"]
        content_collection.update_one({"id": content_id}, {"$set": content_to_update})

    def get_playlists(self):
        metadata_collection, _ = self.get_collections()

        playlists = metadata_collection.find_one({"name": "playlists"})

        return playlists["playlists"]

    def get_playlist(self, id):
        metadata_collection, _ = self.get_collections()

        playlist = metadata_collection.find_one(
            {
                "name": "playlists"
            }, 
            {
                "playlists": { "$elemMatch": {"id": id} }
            }
        )["playlists"][0]

        if playlist is None:
            raise Exception(f"Playlist with id {id} not found")

        return playlist

    def get_playlist_with_contents(self, id):
        metadata_collection, _ = self.get_collections()

        playlist = metadata_collection.find_one(
            {"name": "playlists"}, {"playlists": {"$elemMatch": {"id": id}}}
        )["playlists"][0]

        playlist["contents"] = self.get_contents_for_playlist(playlist["id"])

        return playlist

    def update_playlist_name(self, id, name):
        metadata_collection, _ = self.get_collections()

        playlists_doc = metadata_collection.find_one({"name": "playlists"})

        for playlist in playlists_doc["playlists"]:
            if str(playlist["id"]) == id:
                playlist["name"] = name
                break

        metadata_collection.update_one({"name": "playlists"}, {"$set": playlists_doc})

    def get_collections(self):
        client = pymongo.MongoClient(config.COSMOS_DB_CONNECTION_STRING)
        db = client[config.COSMOS_DB_NAME]

        content_collection = db[config.COSMOS_DB_CONTENT_COLLECTION_NAME]
        metadata_collection = db[config.COSMOS_DB_METADATA_COLLECTION_NAME]

        # create the collection if it does not exist
        if db[config.COSMOS_DB_CONTENT_COLLECTION_NAME] is None:
            content_collection = db.create_collection(
                name=config.COSMOS_DB_CONTENT_COLLECTION_NAME
            )
        else:
            content_collection = db[config.COSMOS_DB_CONTENT_COLLECTION_NAME]

        # create the collection if it does not exist
        if db[config.COSMOS_DB_METADATA_COLLECTION_NAME] is None:
            metadata_collection = db.create_collection(
                name=config.COSMOS_DB_METADATA_COLLECTION_NAME
            )
        else:
            metadata_collection = db[config.COSMOS_DB_METADATA_COLLECTION_NAME]

        return metadata_collection, content_collection
