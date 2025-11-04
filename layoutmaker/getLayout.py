import yaml
from typing import Any
import os

# DIR:str = "layoutmaker/layout"
base_dir:str = os.path.dirname(os.path.abspath(__file__))
yaml_path:str = os.path.join(base_dir, "layout")


class DuplicateKeyNumberingLoader(yaml.Loader):
    def construct_mapping(self, node, deep=False):#type:ignore
        mapping = {}
        counters = {}

        for key_node, value_node in node.value: #type:ignore
            key = self.construct_object(key_node, deep=deep)#type:ignore
            value = self.construct_object(value_node, deep=deep)#type:ignore

            # Keep count of how many times a key appears
            if key in counters:
                counters[key] += 1
                numbered_key = f"{key}{counters[key]}"
            else:
                counters[key] = 1
                numbered_key = key#type:ignore

            # Inject original name into the value dict
            if isinstance(value, dict):
                value["name"] = key

            mapping[numbered_key] = value

        return mapping#type:ignore


def getLayoutData(direction:str = yaml_path) -> dict[str, Any]:
    with open(f"{direction}.yaml", 'r') as file:
        data = yaml.load(file, Loader=DuplicateKeyNumberingLoader)
        
    return data

def main() -> None:
    print(getLayoutData())

if __name__ == '__main__':
    main()