
import numpy as np
import os
import os.path as osp
import torch.utils.data as data
import torchvision.transforms as T
from PIL import Image

class SegSTRONGC(data.Dataset):
    def __init__(self, root_folder: str, set_indices: list, subset_indices: list, split: str = 'train', domains: list = ['regular'], image_transforms = None, gt_transforms = None):
        '''
            reference dataset loading for SegSTRONGC
            root_folder: the root_folder of the SegSTRONGC dataset
            set_indices: is the indices for sets to be used
            subset_indices: is the indices for the subsets to be used
            split: 'train', 'val' or 'test'
            domain: the image domains to be loaded.
            image_transforms: any transforms to perform, can add augmentations here.
            gt_transforms: corresponding transform for gt.
        '''
        self.split = split
        self.root_folder = root_folder
        self.set_indices = set_indices
        self.subset_indices = subset_indices
        self.domains = domains
        self.image_transforms = image_transforms
        self.gt_transforms = gt_transforms

        self.image_paths = []
        self.gt_paths = []

        for set_idx, s in enumerate(self.set_indices):
            for ss in self.subset_indices[set_idx]:
                set_folder = osp.join(self.root_folder + '/images', self.split + '/' + str(s) + '/' + str(ss))
                gt_folder = osp.join(set_folder, 'ground_truth')
                
                image_numbers = len(os.listdir(osp.join(gt_folder, 'left')))

                for d in self.domains:
                    image_folder = osp.join(set_folder, d)
                    for i in range(image_numbers):
                        image_name = str(i) + ".png"
                        gt_name = str(i) + ".npy"
                        self.image_paths.append(osp.join(image_folder, 'left/' + image_name))
                        self.gt_paths.append(osp.join(gt_folder, 'left/' + gt_name))
                        self.image_paths.append(osp.join(image_folder, 'right/' + image_name))
                        self.gt_paths.append(osp.join(gt_folder, 'right/' + gt_name))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        image = np.array(Image.open(self.image_paths[idx])).astype(np.float32)
        gt = np.load(self.gt_paths[idx]).astype(np.float32)
        if self.image_transforms is None:
            image = T.ToTensor()(image)
        else:
            image = self.image_transforms(image)
        if self.gt_transforms is None:
            gt = T.ToTensor()(gt)
        else:
            gt = self.gt_transforms(gt)
        return image, gt
