# -*- coding: utf-8 -*-
# @Author: jjj
# @Date:   2020-12-29

import json
import os

from preprocess import config as DataConfig


class Alphabet:
    """Alphabet maps objects to integer ids.
    It provides two way mapping from the index to the objects.
    """

    def __init__(self, name, label=False, keep_growing=True):
        self.__name = name
        self.unknown_tok = DataConfig.UNKNOWN_TOKEN
        self.pad_token = DataConfig.PAD_TOKEN
        self.label = label
        self.instance2index = {}
        self.instances = []
        self.keep_growing = keep_growing

        # Index 0 is occupied by default, all else following.
        self.default_index = -1
        self.next_index = 0

        self.add(self.pad_token)

        if not self.label:
            self.add(self.unknown_tok)

    def clear(self, keep_growing=True):
        self.instance2index = {}
        self.instances = []
        self.keep_growing = keep_growing

        # Index 0 is occupied by default, all else following.
        self.default_index = -1
        self.next_index = 0

    def add(self, instance):
        """Add instance into instacnes List and instance2index Map
        Args:
            instance:
        """
        if instance not in self.instance2index:
            self.instances.append(instance)
            self.instance2index[instance] = self.next_index
            self.next_index += 1

    def get_index(self, instance):
        try:
            return self.instance2index[instance]
        except KeyError:
            if self.keep_growing:
                index = self.next_index
                self.add(instance)
                return index
            else:
                return self.instance2index[self.unknown_tok]

    def get_instance(self, index):
        if index == 0:
            # First index is occupied by the wildcard element.
            return None
        try:
            return self.instances[index - 1]
        except IndexError:
            print('WARNING:Alphabet get_instance ,unknown instance, return the first label.')
            return self.instances[0]

    def size(self):
        # if self.label:
        #     return len(self.instances)
        # else:
        return len(self.instances)

    def iteritems(self):
        return self.instance2index.items()

    def enumerate_items(self, start=1):
        if start < 1 or start >= self.size():
            raise IndexError("Enumerate is allowed between [1 : size of the alphabet)")
        return zip(range(start, len(self.instances) + 1), self.instances[start - 1:])

    def close(self):
        self.keep_growing = False

    def open(self):
        self.keep_growing = True

    def get_content(self):
        return {'instance2index': self.instance2index, 'instances': self.instances}

    def from_json(self, data):
        self.instances = data["instances"]
        self.instance2index = data["instance2index"]

    def save(self, output_directory: str, name=None):
        """Save `instance2index` and `instances` records to the given directory.

        Args:
            output_directory: Directory to save model and weights.
            name: The alphabet saving name, optional.

        Returns:

        """
        saving_name = name if name else self.__name
        try:
            json.dump(self.get_content(), open(os.path.join(output_directory, saving_name + ".json"), 'w'))
        except Exception as e:
            print("Exception: Alphabet is not saved: " % repr(e))

    def load(self, input_directory: str, name=None):
        """Load model architecture and weights from the give directory.
        This allow we use old models even the structure changes.

        Args:
            input_directory: Directory to save model and weights
            name: The alphabet loading name, optional.

        """
        loading_name = name if name else self.__name
        self.from_json(json.load(open(os.path.join(input_directory, loading_name + ".json"))))
