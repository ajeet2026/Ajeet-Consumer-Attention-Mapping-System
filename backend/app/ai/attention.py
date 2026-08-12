class AttentionDetector:
    def __init__(self):
        # Mapped 2D bounding boxes in camera view for configured shelves
        # format: shelf_id -> [x1, y1, x2, y2]
        self.shelf_regions = {
            1: [40, 60, 240, 280],  # Beverages (left)
            2: [380, 60, 580, 280],  # Snacks (right)
        }

    def detect_attention(self, shopper_centroid, gaze_vector, active_shelves=None):
        """
        Calculates if the shopper's gaze vector intersects with any shelf region.
        shopper_centroid: (cx, cy) - representing the face center
        gaze_vector: [vx, vy, vz] - 3D gaze direction vector
        active_shelves: list of SQLAlchemy Shelf objects to check against.
        Returns the shelf_id if looking at a shelf, or None.
        """
        # Exclude z vector for 2D ray casting
        vx, vy = gaze_vector[0], gaze_vector[1]

        # Use database shelves mapped regions if provided, otherwise fallback to defaults
        regions = self.shelf_regions
        if active_shelves:
            # Map database shelves to default regions based on ID
            regions = {}
            for idx, shelf in enumerate(active_shelves):
                # Distribute regions dynamically
                if idx % 2 == 0:
                    regions[shelf.id] = [40, 60, 240, 280]
                else:
                    regions[shelf.id] = [380, 60, 580, 280]

        # Run 2D Ray-Box intersection algorithm (Slab Method)
        for shelf_id, box in regions.items():
            if self._ray_intersects_box(shopper_centroid, (vx, vy), box):
                return shelf_id

        return None

    def _ray_intersects_box(self, origin, direction, box):
        ox, oy = origin
        vx, vy = direction
        x1, y1, x2, y2 = box

        if vx == 0 and vy == 0:
            return False

        t_min = 0.0
        t_max = float("inf")

        # Check X dimension intersection intervals
        if vx != 0:
            t1 = (x1 - ox) / vx
            t2 = (x2 - ox) / vx
            t_min = max(t_min, min(t1, t2))
            t_max = min(t_max, max(t1, t2))
        else:
            if ox < x1 or ox > x2:
                return False

        # Check Y dimension intersection intervals
        if vy != 0:
            t1 = (y1 - oy) / vy
            t2 = (y2 - oy) / vy
            t_min = max(t_min, min(t1, t2))
            t_max = min(t_max, max(t1, t2))
        else:
            if oy < y1 or oy > y2:
                return False

        # If t_min <= t_max and t_max > 0, the ray intersects the bounding box
        return t_min <= t_max and t_max > 0
