from mmseg.datasets.builder import DATASETS
from mmseg.datasets.custom import CustomDataset

@DATASETS.register_module()
class HistoCanDataset(CustomDataset):
  CLASSES = ('Others', 'T-G1','T-G2', 'T-G3',  'Normal mucosa' )
  PALETTE = [
              [0, 0, 0],
              [0, 192, 0],
              [255, 224, 32],
              [255, 0, 0],
              [0, 32, 255],
            ]

  def __init__(self, **kwargs):
    super().__init__(img_suffix='.png', seg_map_suffix='.png', **kwargs)

@DATASETS.register_module()
class HistoCanBinaryDataset(CustomDataset):
  CLASSES = ('Others', 'Cancerous' )
  PALETTE = [[0, 0, 0],
           [255, 255, 255]]

  def __init__(self, **kwargs):
    super().__init__(img_suffix='.png', seg_map_suffix='.png', **kwargs)