# import json
import uuid
from bson import ObjectId
import pymongo
from datetime import datetime
# from tqdm import tqdm
import streamlit as st

URI = st.secrets["general"]["uri"]

class CustomToDoctreenConverter:
    def __init__(self, owner_id, tree_name, uri=URI):
        self.owner_id = owner_id
        self.tree_name = tree_name
        self.client = pymongo.MongoClient(uri)
        self.db = self.client["doctreen"]
        self.treenodes_collection = self.db["test_treenodes"]
        self.trees_collection = self.db["test_trees"]

    def generate_unique_uuid(self,stream_lit_loop,index,total):
        attempts = 0
        
        while True:
            new_uuid = str(uuid.uuid4())
            attempts += 1
            
            if (self.treenodes_collection.find_one({"nodeId": new_uuid}) is None):
                stream_lit_loop.progress(index/total,text=f"UUID for node {index} created")
                return new_uuid
            
            else:
                continue

    def generate_unique_objectid(self):
        attempts = 0
        
        while True:
            new_objid = ObjectId()
            attempts += 1
            
            if (self.treenodes_collection.find_one({"_id": new_objid}) is None):
                return new_objid
            
            else:
                continue

    def generate_unique_tree_id(self):
        attempts = 0
        
        while True:
            new_tree_id = ObjectId()
            attempts += 1
            
            if (self.trees_collection.find_one({"_id": new_tree_id}) is None):
                st.info(f"Unique _id created for the tree : {new_tree_id}")
                return new_tree_id
            
            else:
                continue

    def convert_custom_to_doctreen(self, custom_nodes):
        new_nodes = []
        tree_nodes = []
        idMap = {}
        root = ''
        check = 0
        my_bar = st.progress(0,"Generating UUIDs")
        total = len(custom_nodes)
        for index,node in enumerate(custom_nodes):
            new_uuid = self.generate_unique_uuid(stream_lit_loop = my_bar,index = index+1,total = total)
            idMap[node['id']] = new_uuid
            
            if node['nodeType'] == 'TYPE_ROOT' and check == 0:
                root = new_uuid
                check = 1
                
            elif node['nodeType'] == 'TYPE_ROOT' and check == 1:
                return 'INVALID ROOT', 0
        
        my_bar.empty()
        my_bar = st.progress(0,"Adding nodes to doctreen")
        for index,node in enumerate(custom_nodes):
            node_id = self.generate_unique_objectid()
            tree_nodes.append(node_id)
            
            if node.get("nodeType", "") == 'TYPE_MEASURE':
                nodetype = 'TYPE_MESURE'
                
            elif node.get("nodeType", "") in ['TYPE_TOPIC', 'TYPE_QUESTION']:
                nodetype = 'TYPE_NODE'
                
            else:
                nodetype = node.get("nodeType", "")
            
            new_node = {
                "_id": node_id,
                "nodeId": idMap[node['id']],
                "nodeType": nodetype,
                "fatherId": idMap[node['parent']['id']] if node.get("parent") else None,
                "alias": node.get("text", ""),
                "value": {},
                "markTypes": {"MARK_SPACE": True},
                "styling": {},
                "ownerId": ObjectId(self.owner_id),
                "childNodes": [idMap.get(child.get("id"), child.get("id")) for child in node.get("childs", [])],
                "labelId": None,
                "disabled": False
            }
            result = self.treenodes_collection.insert_one(new_node)
            new_nodes.append(new_node)
            my_bar.progress((index+1)/total,text = f"Inserted node with _id:{result.inserted_id}")
        my_bar.empty()
        tree_id = self.generate_unique_tree_id()
        tree_doc = {
            "_id": tree_id,
            "treeName": self.tree_name,
            "tags": [],
            "treeNodeIds": tree_nodes,
            "description": "",
            "public": False,
            "disabled": False,
            "labels": {},
            "latest": True,
            "defaultReport": {"nodes": []},
            "subTrees": [],
            "reports": [],
            "disabledReports": [],
            "lastUpdate": datetime.utcnow(),
            "software_version": 1,
            "lineTreeId": tree_id,
            "ownerId": ObjectId(self.owner_id),
            "rootNodeId": root
        }
        
        print('=' * 20)
        tree_result = self.trees_collection.insert_one(tree_doc)
        print("Inserted tree document with _id:", tree_result.inserted_id)
        tree_link = f'https://front.interns.doctreen.io/edit/{tree_id}'
        
        return new_nodes, tree_doc, tree_link


