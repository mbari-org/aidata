# mbari_aidata, Apache-2.0 license
# Filename: predictors/vector_similarity.py
# Description: Runs operations on Redis database with RediSearch on embedded vectors
import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from mbari_aidata.logger import err, info, debug


class VectorSimilarity:
    INDEX_NAME = "index"  # Vector Index Name
    DOC_PREFIX = "doc:"  # RediSearch Key Prefix for the Index

    def __init__(self, r: redis.Redis, vector_dimensions: int, reset: bool = False):
        self.r = r
        self.create_index(vector_dimensions, reset)

    def create_index(self, vector_dimensions: int, reset_db: bool = False):
        try:
            # check to see if index exists
            self.r.ft(self.INDEX_NAME).info()
            err(f"Index {self.INDEX_NAME} already exists!")
            if reset_db:
                info(f"Existing index found. Dropping and recreating the index with new dimensions {vector_dimensions}.")
                self.r.ft(self.INDEX_NAME).dropindex(delete_documents=True)
                self.r.flushall()
                self.reset(vector_dimensions)
                exit(0)
        except redis.exceptions.ResponseError:
            if reset_db:
                self.reset(vector_dimensions)

    def reset(self, vector_dimensions: int):
        schema = (
            TagField("tag"),
            VectorField(
                "vector",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimensions,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )
        definition = IndexDefinition(prefix=[self.DOC_PREFIX], index_type=IndexType.HASH)
        self.r.ft(self.INDEX_NAME).create_index(fields=schema, definition=definition)

    def add_vector(self, doc_id: str, vector: list, tag: str):
        doc_key = f"{self.DOC_PREFIX}{doc_id}"
        debug(f"Adding vector for {doc_key} {len(vector)} dimensions tagged as {tag}")
        self.r.hset(doc_key, mapping={"vector": vector, "tag": tag})

    def search_vector(self, vector: list, top_n: int):
        query = (
            Query(f"*=>[KNN {top_n} @vector $vec as score]")
            .sort_by("score")
            .return_fields("id", "score")
            .paging(0, top_n)
            .dialect(2)
        )
        query_params = {"vec": vector}
        return self.r.ft(self.INDEX_NAME).search(query, query_params).docs

    def get_all_keys(self):
        return self.r.keys(f"{self.DOC_PREFIX}*")