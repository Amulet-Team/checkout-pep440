import os
import json
import itertools
import urllib.request
import urllib.parse
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet


def _get_tags(repo: str) -> list[Version]:
    releases: list[Version] = []
    github_api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    for page in itertools.count(1):
        query = urllib.parse.urlencode({"per_page": 100, "page": page})
        url = f"{github_api_url}/repos/{repo}/releases?{query}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if not data:
                break
            for release in data:
                try:
                    releases.append(Version(release["tag_name"]))
                except InvalidVersion:
                    continue
    return releases


def find_tag(repo: str, specifier_str: str) -> str:
    specifier = SpecifierSet(specifier_str)
    versions = [v for v in _get_tags(repo) if v in specifier]
    if not versions:
        raise Exception("No matching tags found")
    return str(max(versions))
