import os
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.shelf import Shelf
from app.models.shelf_snapshot import ShelfSnapshot


class ShelfAnalyticsService:
    """
    Service layer for shelf product detection and analytics.
    Connects the ShelfProductDetector AI module to the database.
    """

    @staticmethod
    def get_shelf_bbox(shelf: Shelf):
        """
        Returns the camera-view bounding box for a shelf, or None if not configured.
        """
        if shelf.bbox_x1 is not None and shelf.bbox_y1 is not None \
           and shelf.bbox_x2 is not None and shelf.bbox_y2 is not None:
            return [shelf.bbox_x1, shelf.bbox_y1, shelf.bbox_x2, shelf.bbox_y2]
        return None

    @staticmethod
    def save_snapshot(db: Session, shelf_id: int, metrics: dict, snapshot_path: str = None):
        """
        Save a shelf scan snapshot to the database.
        """
        snapshot = ShelfSnapshot(
            shelf_id=shelf_id,
            timestamp=datetime.utcnow(),
            product_count=metrics.get("product_count", 0),
            density_score=metrics.get("density_score", 0.0),
            occupancy_pct=metrics.get("occupancy_pct", 0.0),
            snapshot_path=snapshot_path,
            product_breakdown=metrics.get("product_breakdown", {}),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def get_shelf_history(db: Session, shelf_id: int, limit: int = 50):
        """
        Returns historical shelf snapshots for a given shelf.
        """
        snapshots = (
            db.query(ShelfSnapshot)
            .filter(ShelfSnapshot.shelf_id == shelf_id)
            .order_by(ShelfSnapshot.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": s.id,
                "shelf_id": s.shelf_id,
                "timestamp": s.timestamp,
                "product_count": s.product_count,
                "density_score": s.density_score,
                "occupancy_pct": s.occupancy_pct,
                "snapshot_path": s.snapshot_path,
                "product_breakdown": s.product_breakdown,
            }
            for s in snapshots
        ]

    @staticmethod
    def get_latest_snapshot(db: Session, shelf_id: int):
        """
        Returns the most recent snapshot for a shelf.
        """
        snapshot = (
            db.query(ShelfSnapshot)
            .filter(ShelfSnapshot.shelf_id == shelf_id)
            .order_by(ShelfSnapshot.timestamp.desc())
            .first()
        )
        if snapshot:
            return {
                "id": snapshot.id,
                "shelf_id": snapshot.shelf_id,
                "timestamp": snapshot.timestamp,
                "product_count": snapshot.product_count,
                "density_score": snapshot.density_score,
                "occupancy_pct": snapshot.occupancy_pct,
                "snapshot_path": snapshot.snapshot_path,
                "product_breakdown": snapshot.product_breakdown,
            }
        return None

    @staticmethod
    def get_all_shelves_summary(db: Session):
        """
        Returns the latest snapshot summary for all shelves.
        """
        shelves = db.query(Shelf).all()
        results = []
        for shelf in shelves:
            latest = ShelfAnalyticsService.get_latest_snapshot(db, shelf.id)
            bbox = ShelfAnalyticsService.get_shelf_bbox(shelf)
            results.append({
                "shelf_id": shelf.id,
                "shelf_name": shelf.name,
                "has_bbox": bbox is not None,
                "bbox": bbox,
                "latest_snapshot": latest,
            })
        return results
