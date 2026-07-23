# Model and preprocessing provenance

## Reference implementation

| Component | Source | Pinned identity |
| --- | --- | --- |
| SelfMAD++ | <https://github.com/LeonTodorov/SelfMADpp> | commit `75bcbe08ad66b758d1e6d7a1630a91bb797d8019` |
| SMDD checkpoint | [Authors' download](https://unilj-my.sharepoint.com/:u:/g/personal/leon_todorov_fe1_uni-lj_si/EXPI80C7nVJGm8L130BWR2IBhcaUoDusyDMBYtXdJxgnHQ?e=D4OiAr) | SHA-256 `642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4` |
| 81-point predictor | [dlib model files](http://dlib.net/files/) | SHA-256 `8cae4375589dd915d9a0a881101bed1bbb4e9887e35e63b024388f1ca25ff869` after decompression |
| Author crop script | [`utils/preprocessing/crop.py`](https://github.com/LeonTodorov/SelfMADpp/blob/75bcbe08ad66b758d1e6d7a1630a91bb797d8019/utils/preprocessing/crop.py) | file SHA-256 `a9a5f667e9e85e8b7f6b255221e5855ddbcfbd7de3c8e23324fa967990922ad6` |

The repository does not redistribute either model file. Installation verifies exact checksums and fails closed on a mismatch.

## Score definition

SelfMAD++ uses label `0` for bona fide and label `1` for morph. The exported score is the class-1 softmax value. The service does not invert or transform it: product-facing documentation uses the same scalar as a bona fide deviation score, where higher means lower compatibility with the model's learned bona fide side of its decision boundary.

The original morph label documents how the backend was trained; it neither limits the service to morph detection nor establishes coverage of all manipulations. Score direction is fixed before evaluating any dataset, and evaluation must never reverse polarity per dataset to improve an EER or AUC.

## Evaluation environment

The frozen benchmark was produced with Python 3.10, PyTorch 2.3.1 with CUDA 12.1 support, torchvision 0.18.1, and the dependency versions pinned by SelfMAD++. Scoring ran as two independent processes, each owning one NVIDIA RTX 2080 Ti. CPU face cropping was pipelined with GPU scoring where applicable.

## Reproduction boundary

Exact numerical reproduction also depends on the source images, manifests, decoder behavior, dlib version, GPU libraries, and checkpoint. Reports therefore retain input counts, crop failures, software identities, selection rules, and artifact checksums rather than describing results as universally reproducible from a metric alone.
