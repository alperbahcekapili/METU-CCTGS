# METU-CCTGS

We welcome you all to official repository of the paper [Colorectal cancer tumor grade segmentation: A new dataset and baseline results](https://www.cell.com/heliyon/fulltext/S2405-8440(25)00847-3)


This repository contains following:
* Links to pretrained weights
* A tutorial on how to use these weights
* Short util scripts which may help processing the dataset



**Pretrained weights**

Following table contains both the checkpoint links and corresponding mmseg configuration files. A tutorial on using these configuration files is given on the root folder of this repository. Swin Transformer is utilized as example.

| Model Name | Link |
|------------|------|
| Swin Transofermer    | [Link](https://drive.google.com/drive/folders/149fCOcNVqmKJ4VBXc4MG64Bxo86Vf1Im?usp=drive_link) |



**Tutorial**

Troughout the training and experimenting process is done with [mmseg](https://github.com/open-mmlab/mmsegmentation) project. You can find relevant tutorials on how to use mmseg on it's official repository. For this repo, we will assume you already know what a mmseg config is and how it is used. 

1. Setup:

Create and activate the conda environment via 

```
conda create --name metu-cctgs-env python=3.8 -y
conda activate metu-cctgs-env
```

We need to 

```
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.0"

```
Install MMSeg 

```
git clone -b main https://github.com/open-mmlab/mmsegmentation.git
cd mmsegmentation
pip install -v -e .
# '-v' means verbose, or more output
# '-e' means installing a project in editable mode,
# thus any local modifications made to the code will take effect without reinstallation.
```

Now we installed MMSeg as well. You can verify the installation via the instructions explained [here](https://github.com/open-mmlab/mmsegmentation/blob/main/docs/en/get_started.md) 


2. METU CCTGS dataset 

We have defined a custom mmseg dataset in METU-CCTGS/mmseg/HistoCanDataset.py

There are three updates we need to make in order to add this custom dataset to our mmsegmentation framework.

1. We need to copy given dataset config file(HistoCanDataset.py) to `mmsegmentation/__base__/datasets/`
2. Register this dataset in `mmsegmentation/mmseg/datasets/histocan.py` (need to copy histocan.py in relevant folder)
3. Import dataset in `mmsegmentation/mmseg/datasets/__init__.py`


Now our dataset is defined ready to be used with mmsegmentation framework.

3. Training

In order to start the training we need to get the training configuration. You can get the configs for that from the table given above. We will use SwinTransformer for this tutorial. Let us download that config and update it's content for our use case:

When we download the dataset after filling the form here [here](https://eakbas.github.io/metu-cctgs/): 

We will need to update a couple of fields in the train cofiguration. 

First
Replace `data_root` entries folder entry with the root folder of the dataset as follows:

`<any_path>/metucctgs_ds`

 And now we need to update img_dir and ann_dir(there are three for) entries well. Then you should be good to go ! 

 You can start the training with tools/dist_train.sh script as follows:

 `tools/dist_train.sh config <numgpus>`


**Utils**

You can find the script that we used for downloading and patchifying script from util/s3_wsi_patchify.py. In this file between the lines 97 and 122 you can find how the geojson data is process and labels are mapped to reported classes.