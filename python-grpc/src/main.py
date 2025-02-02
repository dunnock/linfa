import logging
from logging import log
import time
import grpc
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from concurrent import futures
from protos.centroids_pb2_grpc import ClusteringServiceServicer, add_ClusteringServiceServicer_to_server
from protos.centroids_pb2 import PredictResponse


class ClusteringService(ClusteringServiceServicer):
    def __init__(self, model: KMeans):
        self.model = model

    def Predict(self, request, context):
        features = request.features
        point = np.array(features).reshape(1, -1)
        cluster_index = model.predict(point)
        return PredictResponse(cluster_index=cluster_index)


def serve(model: KMeans):
    # Initialize GRPC Server
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Initialize Services
    add_ClusteringServiceServicer_to_server(ClusteringService(model), grpc_server)
    # Start GRPC Server
    grpc_server.add_insecure_port('[::]:5001')
    grpc_server.start()
    # Keep application alive
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        grpc_server.stop(0)


if __name__ == "__main__":
    logging.basicConfig()

    (dataset, labels) = make_blobs(3)
    model = KMeans(3, init="random", algorithm="full", max_iter=100)
    model.fit(dataset)
    log(20, "Model has been trained")

    serve(model)
