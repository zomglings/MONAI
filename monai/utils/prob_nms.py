from typing import List, Sequence, Tuple, Union

import numpy as np
import torch

from monai.networks.layers import GaussianFilter


class ProbNMS:
    """
    Performs probability based non-maximum suppression (NMS) on the probabilities map via
    iteratively selecting the coordinate with highest probability and then move it as well
    as its surrounding values. The remove range is determined by the parameter `box_size`.
    If multiple coordinates have the same highest probability, only one of them will be
    selected.

    Args:
        spatial_dims: number of spatial dimensions of the input probabilities map.
            Defaults to 2.
        sigma: the standard deviation for gaussian filter.
            It could be a single value, or `spatial_dims` number of values. Defaults to 0.0.
        prob_threshold: the probability threshold, the function will stop searching if
            the highest probability is no larger than the threshold. The value should be
            no less than 0.0. Defaults to 0.5.
        box_size: the box size (in pixel) to be removed around the the pixel with the maximum probability.
            It can be an integer that defines the size of a square or cube,
            or a list containing different values for each dimensions. Defaults to 48.

    Return:
        a list of selected lists, where inner lists contain probability and coordinates.
        For example, for 3D input, the inner lists are in the form of [probability, x, y, z].

    Raises:
        ValueError: When ``prob_threshold`` is less than 0.0.
        ValueError: When ``box_size`` is a list or tuple, and its length is not equal to `spatial_dims`.
        ValueError: When ``box_size`` has a less than 1 value.

    """

    def __init__(
        self,
        spatial_dims: int = 2,
        sigma: Union[Sequence[float], float, Sequence[torch.Tensor], torch.Tensor] = 0.0,
        prob_threshold: float = 0.5,
        box_size: Union[int, List[int], Tuple[int]] = 48,
    ) -> None:
        self.sigma = sigma
        self.spatial_dims = spatial_dims
        if self.sigma != 0:
            self.filter = GaussianFilter(spatial_dims=spatial_dims, sigma=sigma)
        if prob_threshold < 0:
            raise ValueError("prob_threshold should be no less than 0.0.")
        self.prob_threshold = prob_threshold
        if isinstance(box_size, int):
            self.box_size = np.asarray([box_size] * spatial_dims)
        else:
            if len(box_size) != spatial_dims:
                raise ValueError("the sequence length of box_size should be the same as spatial_dims.")
            self.box_size = np.asarray(box_size)
        if self.box_size.min() <= 0:
            raise ValueError("box_size should be larger than 0.")

        self.box_lower_bd = self.box_size // 2
        self.box_upper_bd = self.box_size - self.box_lower_bd

    def __call__(
        self,
        prob_map: Union[np.ndarray, torch.Tensor],
    ):
        """
        prob_map: the input probabilities map, it must have shape (H[, W, ...]).
        """
        if self.sigma != 0:
            if not isinstance(prob_map, torch.Tensor):
                prob_map = torch.as_tensor(prob_map, dtype=torch.float)
            self.filter.to(prob_map)
            prob_map = self.filter(prob_map)
        else:
            if not isinstance(prob_map, torch.Tensor):
                prob_map = prob_map.copy()

        if isinstance(prob_map, torch.Tensor):
            prob_map = prob_map.detach().cpu().numpy()

        prob_map_shape = prob_map.shape

        outputs = []
        while np.max(prob_map) > self.prob_threshold:
            max_idx = np.unravel_index(prob_map.argmax(), prob_map_shape)
            prob_max = prob_map[max_idx]
            max_idx_arr = np.asarray(max_idx)
            outputs.append([prob_max] + list(max_idx_arr))

            idx_min_range = (max_idx_arr - self.box_lower_bd).clip(0, None)
            idx_max_range = (max_idx_arr + self.box_upper_bd).clip(None, prob_map_shape)
            # for each dimension, set values during index ranges to 0
            slices = tuple(slice(idx_min_range[i], idx_max_range[i]) for i in range(self.spatial_dims))
            prob_map[slices] = 0

        return outputs
