#!/usr/bin/env python3
"""
Download pre-trained YOLOv8 SKU-110K weights from Hugging Face.
"""
import os
import sys

def download_weights():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ai")
    target_path = os.path.join(target_dir, "yolov8_sku110k.pt")

    if os.path.exists(target_path):
        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        print(f"Weights already exist at {target_path} ({size_mb:.1f} MB)")
        return target_path

    print("Downloading YOLOv8-L SKU-110K weights from Hugging Face...")
    print("Repository: sbfisher/yolov8l-sku110k")
    print("File: best_imgsz640.pt (~84 MB)")

    try:
        from huggingface_hub import hf_hub_download

        downloaded_path = hf_hub_download(
            repo_id="sbfisher/yolov8l-sku110k",
            filename="best_imgsz640.pt",
            local_dir=target_dir,
        )

        # Rename to our standard name
        if os.path.exists(downloaded_path):
            final_path = os.path.join(target_dir, "yolov8_sku110k.pt")
            if downloaded_path != final_path:
                os.rename(downloaded_path, final_path)
            size_mb = os.path.getsize(final_path) / (1024 * 1024)
            print(f"✅ Downloaded successfully: {final_path} ({size_mb:.1f} MB)")
            return final_path
        else:
            print(f"❌ Download completed but file not found at {downloaded_path}")
            return None

    except Exception as e:
        print(f"❌ Failed to download from Hugging Face: {e}")
        return None


if __name__ == "__main__":
    result = download_weights()
    if result:
        print(f"\nReady to use: {result}")

        # Quick validation
        try:
            from ultralytics import YOLO
            model = YOLO(result)
            print(f"✅ Model loaded successfully")
            print(f"   Model type: {type(model.model).__name__}")
            print(f"   Number of classes: {len(model.names)}")
            print(f"   Class names: {model.names}")
        except Exception as e:
            print(f"Model validation: {e}")
    else:
        sys.exit(1)
