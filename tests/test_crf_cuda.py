# Copyright 2020 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import numpy as np
import torch
from parameterized import parameterized

from monai.networks.blocks import CRF
from tests.utils import skip_if_no_cpp_extension, skip_if_no_cuda

TEST_CASES = [
    [
        # Case Description
        "2 batche(s), 1 dimension(s), 2 classe(s), 1 channel(s)",
        # Parameters
        [
            1.0,  # bilateral_weight
            0.3,  # gaussian_weight
            5.0,  # bilateral_spatial_sigma
            0.5,  # bilateral_color_sigma
            5.0,  # gaussian_spatial_sigma
            1.0,  # update_factor
            1,  # compatability_kernel_range
            5,  # iterations
        ],
        # Input
        [
            # Batch 0
            [
                # Class 0
                [0.8, 0.9, 0.6, 0.2, 0.3],
                # Class 1
                [0.1, 0.3, 0.5, 0.8, 0.7],
            ],
            # Batch 1
            [
                # Class 0
                [0.8, 0.9, 0.6, 0.2, 0.3],
                # Class 1
                [0.1, 0.3, 0.5, 0.8, 0.7],
            ],
        ],
        # Features
        [
            # Batch 0
            [
                # Channel 0
                [1, 1, 1, 0.5, 0],
            ],
            # Batch 1
            [
                # Channel 0
                [1, 1, 0.5, 0, 0],
            ],
        ],
        # Expected
        [
            # Batch 0
            [
                # Class 0
                [0.965345, 0.961201, 0.920527, 0.772525, 0.711900],
                # Class 1
                [0.034655, 0.038799, 0.079473, 0.227475, 0.288100],
            ],
            # Batch 1
            [
                # Class 0
                [0.897615, 0.816166, 0.500186, 0.158644, 0.133245],
                # Class 1
                [0.102385, 0.183834, 0.499814, 0.841356, 0.866755],
            ],
        ],
    ],
    [
        # Case Description
        "1 batche(s), 2 dimension(s), 3 classe(s), 2 channel(s)",
        # Parameters
        [
            1.0,  # bilateral_weight
            0.3,  # gaussian_weight
            5.0,  # bilateral_spatial_sigma
            0.5,  # bilateral_color_sigma
            5.0,  # gaussian_spatial_sigma
            1.0,  # update_factor
            1,  # compatability_kernel_range
            5,  # iterations
        ],
        # Input
        [
            # Batch 0
            [
                # Class 0
                [
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0, 1.0],
                    [0.0, 0.0, 0.0, 1.0, 1.0],
                ],
                # Class 1
                [
                    [1.0, 1.0, 0.0, 0.0, 0.0],
                    [1.0, 1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                ],
                # Class 2
                [
                    [0.0, 0.0, 0.0, 0.5, 1.0],
                    [0.0, 0.0, 0.5, 1.0, 0.5],
                    [0.0, 0.5, 1.0, 0.5, 0.0],
                    [0.5, 1.0, 0.5, 0.0, 0.0],
                    [1.0, 0.5, 0.0, 0.0, 0.0],
                ],
            ],
        ],
        # Features
        [
            # Batch 0
            [
                # Channel 0
                [
                    [1.0, 1.0, 0.0, 0.0, 0.0],
                    [1.0, 1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                ],
                # Channel 1
                [
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0, 1.0],
                    [0.0, 0.0, 0.0, 1.0, 1.0],
                ],
            ],
        ],
        # Expected
        [
            # Batch 0
            [
                # Class 0
                [
                    [0.001529, 0.000798, 0.000323, 0.000093, 0.000053],
                    [0.001365, 0.000966, 0.000422, 0.000178, 0.000281],
                    [0.001405, 0.001007, 0.002425, 0.013078, 0.064707],
                    [0.001239, 0.001263, 0.033857, 0.665830, 0.951172],
                    [0.001534, 0.004486, 0.263298, 0.973852, 0.999018],
                ],
                # Class 1
                [
                    [0.230989, 0.025518, 0.000764, 0.000057, 0.000029],
                    [0.037540, 0.008348, 0.000381, 0.000055, 0.000075],
                    [0.001987, 0.000665, 0.000363, 0.000499, 0.001170],
                    [0.000187, 0.000143, 0.000805, 0.001361, 0.000533],
                    [0.000131, 0.000286, 0.002139, 0.000410, 0.000069],
                ],
                # Class 2
                [
                    [0.767482, 0.973685, 0.998913, 0.999850, 0.999919],
                    [0.961095, 0.990687, 0.999197, 0.999768, 0.999644],
                    [0.996608, 0.998328, 0.997212, 0.986423, 0.934124],
                    [0.998574, 0.998594, 0.965337, 0.332809, 0.048295],
                    [0.998334, 0.995228, 0.734563, 0.025738, 0.000912],
                ],
            ],
        ],
    ],
    [
        # Case Description
        "1 batche(s), 3 dimension(s), 2 classe(s), 1 channel(s)",
        # Parameters
        [
            1.0,  # bilateral_weight
            0.3,  # gaussian_weight
            5.0,  # bilateral_spatial_sigma
            0.1,  # bilateral_color_sigma
            5.0,  # gaussian_spatial_sigma
            1.0,  # update_factor
            1,  # compatability_kernel_range
            2,  # iterations
        ],
        # Input
        [
            # Batch 0
            [
                # Class 0
                [
                    # Slice 0
                    [
                        [1.0, 1.0, 0.0, 0.0, 0.0],
                        [1.0, 1.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 1
                    [
                        [1.0, 1.0, 0.0, 0.0, 0.0],
                        [1.0, 1.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 2
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 3
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 4
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                ],
                # Class 1
                [
                    # Slice 0
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 1
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 2
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 3
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0, 1.0],
                    ],
                    # Slice 4
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0, 1.0],
                    ],
                ],
            ],
        ],
        # Features
        [
            # Batch 0
            [
                # Channel 0
                [
                    # Slice 0
                    [
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 1
                    [
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    # Slice 2
                    [
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.5, 0.0, 0.0],
                        [0.5, 0.5, 0.8, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                    ],
                    # Slice 3
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                    ],
                    # Slice 4
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0],
                    ],
                ],
            ],
        ],
        # Expected
        [
            # Batch 0
            [
                # Class 0
                [
                    # Slice 0
                    [
                        [1.000000, 1.000000, 1.000000, 0.999884, 0.769625],
                        [1.000000, 1.000000, 1.000000, 0.999851, 0.714004],
                        [1.000000, 1.000000, 0.999988, 0.997150, 0.614165],
                        [0.999862, 0.999832, 0.996976, 0.945058, 0.497088],
                        [0.720345, 0.672450, 0.590360, 0.490120, 0.416671],
                    ],
                    # Slice 1
                    [
                        [1.000000, 1.000000, 1.000000, 0.999848, 0.707997],
                        [1.000000, 1.000000, 1.000000, 0.997064, 0.127893],
                        [1.000000, 1.000000, 0.999469, 0.591574, 0.007791],
                        [0.999812, 0.996663, 0.582521, 0.006041, 0.000427],
                        [0.637809, 0.107586, 0.007432, 0.000437, 0.000333],
                    ],
                    # Slice 2
                    [
                        [1.000000, 1.000000, 0.999987, 0.996994, 0.600095],
                        [1.000000, 1.000000, 0.999441, 0.575839, 0.007303],
                        [0.999986, 0.999411, 0.587268, 0.001117, 0.000033],
                        [0.996210, 0.550023, 0.001114, 0.000001, 0.000000],
                        [0.520757, 0.006334, 0.000034, 0.000000, 0.000000],
                    ],
                    # Slice 3
                    [
                        [0.999834, 0.999807, 0.996617, 0.940887, 0.482334],
                        [0.999799, 0.996410, 0.553696, 0.005287, 0.000376],
                        [0.996193, 0.546801, 0.001047, 0.000001, 0.000000],
                        [0.930515, 0.005142, 0.000001, 0.000000, 0.000000],
                        [0.430705, 0.000371, 0.000000, 0.000000, 0.000000],
                    ],
                    # Slice 4
                    [
                        [0.665227, 0.627316, 0.550517, 0.467839, 0.406319],
                        [0.617408, 0.098325, 0.006247, 0.000359, 0.000278],
                        [0.524800, 0.006229, 0.000030, 0.000000, 0.000000],
                        [0.443054, 0.000372, 0.000000, 0.000000, 0.000000],
                        [0.388126, 0.000305, 0.000000, 0.000000, 0.000000],
                    ],
                ],
                # Class 1
                [
                    # Slice 0
                    [
                        [0.000000, 0.000000, 0.000000, 0.000116, 0.230375],
                        [0.000000, 0.000000, 0.000000, 0.000149, 0.285996],
                        [0.000000, 0.000000, 0.000012, 0.002850, 0.385835],
                        [0.000138, 0.000168, 0.003024, 0.054942, 0.502912],
                        [0.279655, 0.327550, 0.409640, 0.509880, 0.583329],
                    ],
                    # Slice 1
                    [
                        [0.000000, 0.000000, 0.000000, 0.000152, 0.292003],
                        [0.000000, 0.000000, 0.000000, 0.002936, 0.872107],
                        [0.000000, 0.000000, 0.000531, 0.408426, 0.992209],
                        [0.000188, 0.003337, 0.417479, 0.993959, 0.999574],
                        [0.362191, 0.892414, 0.992568, 0.999564, 0.999667],
                    ],
                    # Slice 2
                    [
                        [0.000000, 0.000000, 0.000013, 0.003006, 0.399905],
                        [0.000000, 0.000000, 0.000559, 0.424161, 0.992697],
                        [0.000014, 0.000589, 0.412732, 0.998884, 0.999967],
                        [0.003790, 0.449977, 0.998886, 0.999999, 1.000000],
                        [0.479243, 0.993666, 0.999966, 1.000000, 1.000000],
                    ],
                    # Slice 3
                    [
                        [0.000166, 0.000193, 0.003383, 0.059113, 0.517666],
                        [0.000201, 0.003590, 0.446304, 0.994713, 0.999624],
                        [0.003807, 0.453199, 0.998953, 0.999999, 1.000000],
                        [0.069485, 0.994858, 0.999999, 1.000000, 1.000000],
                        [0.569295, 0.999629, 1.000000, 1.000000, 1.000000],
                    ],
                    # Slice 4
                    [
                        [0.334773, 0.372684, 0.449483, 0.532161, 0.593681],
                        [0.382592, 0.901675, 0.993753, 0.999641, 0.999722],
                        [0.475200, 0.993771, 0.999970, 1.000000, 1.000000],
                        [0.556946, 0.999628, 1.000000, 1.000000, 1.000000],
                        [0.611874, 0.999695, 1.000000, 1.000000, 1.000000],
                    ],
                ],
            ],
        ],
    ],
]


@skip_if_no_cpp_extension
@skip_if_no_cuda
class CRFTestCaseCuda(unittest.TestCase):
    @parameterized.expand(TEST_CASES)
    def test(self, test_case_description, params, input, features, expected):

        # Create input tensors
        input_tensor = torch.from_numpy(np.array(input)).to(dtype=torch.float, device=torch.device("cuda"))
        feature_tensor = torch.from_numpy(np.array(features)).to(dtype=torch.float, device=torch.device("cuda"))

        # apply filter
        crf = CRF(*params)
        output = crf(input_tensor, feature_tensor).cpu().numpy()

        # Ensure result are as expected
        np.testing.assert_allclose(output, expected, atol=1e-4, rtol=1e-4)


if __name__ == "__main__":
    unittest.main()
