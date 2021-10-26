import collections
import itertools
import json
import pathlib
import re
import typing

# How many packages to consider
TOP_PACKAGES = 500


def parse_req(requirement: str) -> str:
    """
    Parse a single requirement as it is written in the `requires_dist` field.

    >>> parse_req("asgiref (>=3.2) ; extra == 'asyn")
    "asgiref"
    """
    if not requirement:
        raise ValueError("requirement must be non-empty string")

    match = re.match(r"^([a-zA-Z0-9_-]+)", requirement)
    req = match.group(0)
    return req


def read_top_packages(
        file: pathlib.Path = pathlib.Path("res/top-pypi-packages-30-days.json")
) -> typing.Dict[str, typing.Any]:
    """
    Loads the top packages from the stored JSON file.
    """
    if not file.exists():
        raise FileNotFoundError(file)

    with open(file, "rb") as fd:
        stats = json.load(fd)
        top_packages = dict((package["project"], package) for package in itertools.islice(stats["rows"], TOP_PACKAGES))
        return top_packages


class LastInsertedOrderedDict(collections.OrderedDict):
    """
    Ordered dict that keeps the keys insertion order
    """

    def __setitem__(self, k: typing.Any, v: typing.Any) -> None:
        super().__setitem__(k, v)
        self.move_to_end(k, v)

    def insert(self, key: str) -> int:
        """
        Inserts a given key and set its value to the 1-based index of the inserted key.
        >>> self.insert("foo")
        1
        """
        if key not in self:
            index = len(self.keys()) + 1
            self[key] = index
            return index
        return self[key]


if __name__ == "__main__":
    top_packages = read_top_packages()

    nodes = LastInsertedOrderedDict()
    edges = set()

    with open("res/packages.json", "r") as fd:
        packages = json.load(fd)

        for pkg_name, pkg_info in packages.items():

            name = pkg_info["name"]
            if name not in top_packages:
                continue

            reqs_raw = pkg_info["requires_dist"]
            reqs = [parse_req(req) for req in reqs_raw]

            nodes.insert(name)
            for req in reqs:
                nodes.insert(req)

                edges.add((nodes[name], nodes[req]))

    print(f"Found {len(nodes)} packages")

    with open("build/nodes.json", "w") as fd:
        json.dump(
            [
                {
                    "id": _id,
                    "label": _label,
                    "download_count": top_packages[_label]["download_count"] if _label in top_packages else 0
                }
                for (_label, _id) in nodes.items()
            ], fd
        )

    with open("build/edges.json", "w") as fd:
        json.dump([{"from": _from, "to": _to} for (_from, _to) in edges], fd)
