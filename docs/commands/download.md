# Download Command

Data can be downloaded in various formats, e.g. COCO, CIFAR, or PASCAL VOC.  The type of download
depends on the model.

Be sure to have a solid internet connection and enough disk space to download the data.

!!! note 
    *If your leave off the labels option*, the default is to fetch **all** labels.

*multiple versions* can be combined during download, e.g. to download both Baseline and Test
`--version Baseline --version Test`
    
```shell
python aidata download  --token $TATOR_TOKEN --version Baseline --labels "Diatoms, Copepods"
```

Download data format is saved to a directory with the following structure e.g. for the Baseline version:

```
Baseline
    ├── labels.txt
    ├── images
    │   ├── image1.png
    │   ├── image2.png 
    ├── labels
    │   ├── image1.txt
    │   ├── image2.txt 
```
 
## 
Once data is downloaded. See more details on how to [prepare the data](https://docs.mbari.org/deepsea-ai/data/)
and [train it](https://docs.mbari.org/deepsea-ai/commands/train/). This requires setting up the AWS account. 
This should be done by a company AWS administrator.  Once the account is setup, you can train the model on the AWS cloud.

### PASCAL VOC data format

If you want to download data also in the PASCAL VOC format, use the optional --voc flag, e.g.

```shell
python aidata download  --token $TATOR_TOKEN --generator cluster --version Baseline --labels "Diatoms, Copepods" --voc
```

Download data format is saved to a directory with the following structure e.g. for the Baseline version:
```
Baseline
    ├── labels.txt
    ├── voc
    │   ├── image1.xml
    │   ├── image2.xml 
```
 
### COCO data format

Use the optional --coco flag to download data in the [COCO](https://cocodataset.org/#home) format, e.g.

```shell
python aidata download  --token $TATOR_TOKEN --version Baseline --labels "Diatoms, Copepods"  --coco
```

Download data format is saved to a directory with the following structure e.g. for the Baseline version:
```
Baseline
    ├── labels.txt
    ├── coco
    │   └── coco.json
```
### CIFAR data format

Use the optional --cifar flag to download data in the [CIFAR](https://www.cs.toronto.edu/~kriz/cifar.html) format, e.g.

```shell
download --generator vars-annotation  --token $TATOR_TOKEN --version Baseline --group MERGE_CLASSIFY --base-dir VARSi2MAP --concepts "Atolla" --cifar --voc --cifar-size 128
```

The CIFAR data is saved in a npy file with the following structure, e.g. for the data version Baseline:
```shell 

Baseline
    ├── labels.txt
    ├── cifar
    │   ├── images.npy
    │   └── labels.npy
```

Read the data (and optionally visualize) with the following code:

```python
import numpy as np
import matplotlib.pyplot as plt
images = np.load('Baseline/cifar/images.npy')
labels = np.load('Baseline/cifar/labes.npy')
 
# Visualize a few images from the CIFAR data
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(10, 4))

for i, ax in enumerate(axes.flat):
    ax.imshow(images[i])
    ax.axis('off')

plt.tight_layout()
plt.show()
```
 
![ Image link ](../imgs/atolla_cifar128.png)
