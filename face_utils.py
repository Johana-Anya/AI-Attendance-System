import cv2
import insightface

model = insightface.app.FaceAnalysis(
    providers=["CPUExecutionProvider"]
)

model.prepare(
    ctx_id=0,
    det_size=(640,640)
)

def get_embedding(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return None

    faces = model.get(img)

    if len(faces) == 0:
        return None

    return faces[0].embedding