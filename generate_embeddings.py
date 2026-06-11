import os
import pickle
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(project_root)

from face_utils import get_embedding
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from face_utils import get_embedding

embeddings = {}

for img in os.listdir("images"):

    path = os.path.join(
        "images",
        img
    )

    student_id = img.split(".")[0]

    emb = get_embedding(path)

    if emb is not None:

        embeddings[
            student_id
        ] = emb

with open(
    "embeddings.pkl",
    "wb"
) as f:

    pickle.dump(
        embeddings,
        f
    )

print(
    "Embeddings Saved"
)
import os
import pickle

from face_utils import get_embedding

embeddings = {}

for img in os.listdir(
    "images"
):

    path = os.path.join(
        "images",
        img
    )

    sid = img.split(".")[0]

    emb = get_embedding(path)

    if emb is not None:

        embeddings[sid] = emb

with open(
    "embeddings.pkl",
    "wb"
) as f:

    pickle.dump(
        embeddings,
        f
    )

print(
    "Embeddings Created"
)