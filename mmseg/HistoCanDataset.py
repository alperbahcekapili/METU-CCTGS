_base_ = './stare.py'

dataset_type = 'HistoCanDataset'
data_root = 'data/coad_split2'

#img_norm_cfg=dict(
#     mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0], to_rgb=True)
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

img_scale = (1400, 1200)
crop_size = (640, 640)

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='RandomRotate', degree=180, prob=1.0, pad_val=255, seg_pad_val=0),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', prob=0.5, direction='horizontal'),
    dict(type='RandomFlip', prob=0.5, direction='vertical'),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg'])
]

test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=img_scale,
        flip=False,
        transforms=[
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img'])
        ])
]

data = dict(
    samples_per_gpu=6,
    workers_per_gpu=8,
    train=dict(
        type='RepeatDataset',
#        times=,
        dataset=dict(
            type=dataset_type,
            data_root=data_root,
            img_dir="img/train",
            ann_dir="ann/train",
            pipeline=train_pipeline
        )
    ),
    val=dict(
        type='RepeatDataset',
        times=100,
        dataset=dict(
            type=dataset_type,
            data_root=data_root,
            img_dir="img/val",
            ann_dir="ann/val",
            pipeline=test_pipeline
        )
    ),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir="img/val",
        ann_dir="ann/val",
        pipeline=test_pipeline)
    )