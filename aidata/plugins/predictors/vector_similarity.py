# aidata, Apache-2.0 license
# Filename: workflows/vector_similarity.py
# Description: Runs operations on Redis database with RediSearch on embedded vectors

import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from aidata.logger import err


class VectorSimilarity:
    INDEX_NAME = "index"  # Vector Index Name
    DOC_PREFIX = "doc:"  # RediSearch Key Prefix for the Index

    def __init__(
            self,
            r: redis.Redis
    ):
        self.r = r
        self.create_index(768)

    def create_index(self, vector_dimensions: int):
        try:
            # check to see if index exists
            self.r.ft(self.INDEX_NAME).info()
            err("Index already exists!")
        except redis.exceptions.ResponseError:
            # schema
            schema = (
                TagField("tag"),
                VectorField("vector",
                            "FLAT", {
                                "TYPE": "FLOAT32",
                                "DIM": vector_dimensions,
                                "DISTANCE_METRIC": "COSINE",
                            }
                            ),
            )

            # index Definition
            definition = IndexDefinition(prefix=[self.DOC_PREFIX], index_type=IndexType.HASH)

            # create Index
            self.r.ft(self.INDEX_NAME).create_index(fields=schema, definition=definition)

    def add_vector(self, doc_id: str, vector: list, tag: str):
        doc_key = f"{self.DOC_PREFIX}{doc_id}"
        self.r.ft(self.INDEX_NAME).add_document(doc_key, vector=vector, tag=tag)

    def search_vector(self, vector: list, num_results: int):
        query = (
            Query(f"*=>[KNN {num_results} @vector $vec as score]")
            .sort_by("score")
            .return_fields("id", "score")
            .paging(0, num_results)
            .dialect(2)
        )
        query_params = {
            "vec": vector
        }
        return self.r.ft(self.INDEX_NAME).search(query, query_params).docs
