# Copyright 2023 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import TYPE_CHECKING

from ... import is_sentencepiece_available
from ...file_utils import _LazyModule, is_tokenizers_available, is_torch_available
from ...utils import OptionalDependencyNotAvailable


_import_structure = {"configuration_llama": ["LLAMA_PRETRAINED_CONFIG_ARCHIVE_MAP", "LLaMaConfig"]}

try:
    if not is_sentencepiece_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["tokenization_llama"] = ["LLaMaTokenizer"]

try:
    if not is_torch_available():
        raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    pass
else:
    _import_structure["modeling_llama"] = [
        "LLaMaForCausalLM",
        "LLaMaLayer",
        "LLaMaModel",
        "LLaMaPreTrainedModel",
    ]


if TYPE_CHECKING:
    from .configuration_llama import LLAMA_PRETRAINED_CONFIG_ARCHIVE_MAP, LLaMaConfig

    try:
        if not is_tokenizers_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .tokenization_llama import LLaMaTokenizer

    try:
        if not is_torch_available():
            raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable:
        pass
    else:
        from .modeling_llama import (
            LLaMaForCausalLM,
            LLaMaLayer,
            LLaMaModel,
            LLaMaPreTrainedModel,
        )


else:
    import sys

    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
