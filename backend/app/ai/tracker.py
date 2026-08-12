import math


class ShopperTracker:
    def __init__(self, max_disappeared=15):
        self.next_object_id = 1
        self.objects = {}  # id -> centroid (x, y)
        self.bboxes = {}  # id -> bbox [x1, y1, x2, y2]
        self.disappeared = {}  # id -> frame count disappeared
        self.max_disappeared = max_disappeared

    def register(self, centroid, bbox):
        self.objects[self.next_object_id] = centroid
        self.bboxes[self.next_object_id] = bbox
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        if object_id in self.objects:
            del self.objects[object_id]
        if object_id in self.bboxes:
            del self.bboxes[object_id]
        if object_id in self.disappeared:
            del self.disappeared[object_id]

    def update(self, rects):
        """
        rects: list of bounding boxes [[x1, y1, x2, y2], ...]
        Returns a dict mapping object_id -> bbox
        """
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.bboxes

        input_centroids = []
        for r in rects:
            cx = int((r[0] + r[2]) / 2)
            cy = int((r[1] + r[3]) / 2)
            input_centroids.append((cx, cy))

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i], rects[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            used_inputs = set()
            used_objects = set()

            # Greedily match existing centroids to nearest new centroids
            for obj_idx, obj_id in enumerate(object_ids):
                min_dist = float("inf")
                min_idx = -1
                for inp_idx, inp_centroid in enumerate(input_centroids):
                    if inp_idx in used_inputs:
                        continue
                    d = math.sqrt(
                        (object_centroids[obj_idx][0] - inp_centroid[0]) ** 2
                        + (object_centroids[obj_idx][1] - inp_centroid[1]) ** 2
                    )
                    if d < min_dist:
                        min_dist = d
                        min_idx = inp_idx

                # If closest new centroid is within threshold distance (e.g. 150px)
                if min_idx != -1 and min_dist < 150:
                    self.objects[obj_id] = input_centroids[min_idx]
                    self.bboxes[obj_id] = rects[min_idx]
                    self.disappeared[obj_id] = 0
                    used_inputs.add(min_idx)
                    used_objects.add(obj_id)

            # Mark remaining objects as disappeared
            for obj_id in object_ids:
                if obj_id not in used_objects:
                    self.disappeared[obj_id] += 1
                    if self.disappeared[obj_id] > self.max_disappeared:
                        self.deregister(obj_id)

            # Register any brand new centroids
            for inp_idx, inp_centroid in enumerate(input_centroids):
                if inp_idx not in used_inputs:
                    self.register(inp_centroid, rects[inp_idx])

        return self.bboxes.copy()
