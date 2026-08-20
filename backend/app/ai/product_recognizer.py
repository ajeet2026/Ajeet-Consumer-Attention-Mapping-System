import os
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np


class ProductRecognizer:
    def __init__(self, gallery_dir="app/ai/rpc_gallery"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gallery_dir = gallery_dir
        self.reference_embeddings = {}
        self.sku_names = []
        self.sku_vectors = None
        
        # Load lightweight ResNet18 for feature extraction
        try:
            # Load pre-trained model and remove the classification head
            base_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            self.model = torch.nn.Sequential(*list(base_model.children())[:-1])
            self.model.to(self.device)
            self.model.eval()
            print(f"ProductRecognizer: ResNet18 loaded on {self.device}")
        except Exception as e:
            print(f"ProductRecognizer: Error loading model - {e}")
            self.model = None

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self._build_gallery_index()

    def _get_embedding(self, img_pil):
        if not self.model:
            return None
        tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        with torch.no_grad():
            emb = self.model(tensor)
            emb = emb.view(emb.size(0), -1)  # Flatten
            emb = F.normalize(emb, p=2, dim=1)
        return emb

    def _build_gallery_index(self):
        if not os.path.exists(self.gallery_dir) or not self.model:
            print("ProductRecognizer: Gallery dir not found or model not loaded.")
            return

        vectors = []
        for filename in os.listdir(self.gallery_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.gallery_dir, filename)
                try:
                    img = Image.open(path).convert("RGB")
                    emb = self._get_embedding(img)
                    if emb is not None:
                        sku_name = os.path.splitext(filename)[0]
                        self.sku_names.append(sku_name)
                        vectors.append(emb.cpu().numpy())
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

        if vectors:
            self.sku_vectors = torch.tensor(np.vstack(vectors)).to(self.device)
            print(f"ProductRecognizer: Indexed {len(self.sku_names)} products from gallery.")
        else:
            print("ProductRecognizer: No images found in gallery.")

    def recognize_crop(self, crop_cv2):
        """
        Takes a cv2 image crop (BGR), converts to PIL, extracts embedding,
        and returns the best matching SKU name.
        """
        if self.sku_vectors is None or len(self.sku_names) == 0:
            return "Unknown Product"

        try:
            # Convert cv2 BGR to RGB PIL Image
            img_rgb = crop_cv2[:, :, ::-1]  # BGR to RGB
            img_pil = Image.fromarray(img_rgb)
            
            query_emb = self._get_embedding(img_pil)
            if query_emb is None:
                return "Unknown Product"

            # Compute cosine similarity
            # query_emb: [1, dim], self.sku_vectors: [N, dim]
            similarities = torch.mm(query_emb, self.sku_vectors.T)
            best_idx = torch.argmax(similarities, dim=1).item()
            best_score = similarities[0, best_idx].item()

            # Optional thresholding: if score is too low, it might not be in our gallery
            if best_score < 0.4:  # Adjust threshold as needed
                return "Unknown Product"

            return self.sku_names[best_idx]
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown Product"
