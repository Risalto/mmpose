import os.path as osp

import numpy as np
from mmcv.utils import build_from_cfg

from mmpose.datasets import PIPELINES


def test_albu_transform():
    data_prefix = 'tests/data/coco/'
    results = dict(image_file=osp.join(data_prefix, '000000000785.jpg'))

    # Define simple pipeline
    load = dict(type='LoadImageFromFile')
    load = build_from_cfg(load, PIPELINES)

    albu_transform = dict(
        type='Albumentation',
        transforms=[
            dict(type='RandomBrightnessContrast', p=0.2),
            dict(type='ToFloat')
        ])
    albu_transform = build_from_cfg(albu_transform, PIPELINES)

    # Execute transforms
    results = load(results)

    results = albu_transform(results)

    assert results['img'].dtype == np.float32


def test_photometric_distortion_transform():
    data_prefix = 'tests/data/coco/'
    results = dict(image_file=osp.join(data_prefix, '000000000785.jpg'))

    # Define simple pipeline
    load = dict(type='LoadImageFromFile')
    load = build_from_cfg(load, PIPELINES)

    photo_transform = dict(type='PhotometricDistortion')
    photo_transform = build_from_cfg(photo_transform, PIPELINES)

    # Execute transforms
    results = load(results)

    results = photo_transform(results)

    assert results['img'].dtype == np.uint8


def test_multitask_gather():
    ann_info = dict(
        image_size=np.array([256, 256]),
        heatmap_size=np.array([64, 64]),
        num_joints=17,
        joint_weights=np.ones((17, 1), dtype=np.float32),
        use_different_joint_weights=False)

    results = dict(
        joints_3d=np.zeros([17, 3]),
        joints_3d_visible=np.ones([17, 3]),
        ann_info=ann_info)

    pipeline_list = [[dict(type='TopDownGenerateTarget', sigma=2)],
                     [dict(type='TopDownGenerateTargetRegression')]]
    pipeline = dict(type='MultitaskGatherTarget', pipeline_list=pipeline_list)
    pipeline = build_from_cfg(pipeline, PIPELINES)

    results = pipeline(results)
    target = results['target']
    target_weight = results['target_weight']
    assert isinstance(target, list)
    assert isinstance(target_weight, list)
    assert target[0].shape == (17, 64, 64)
    assert target_weight[0].shape == (17, 1)
    assert target[1].shape == (17, 2)
    assert target_weight[1].shape == (17, 2)
