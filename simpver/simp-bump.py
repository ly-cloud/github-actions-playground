#!/usr/bin/env python3

import os
import sys

from github import Github


def verify_env(name):
    if name not in os.environ:
        raise Exception(f"Missing environment variable: {name}")


def get_pull_request_labels(repo):
    default_branch = repo.get_branch(repo.default_branch)
    latest_commit = default_branch.commit

    for pr in latest_commit.get_pulls():
        if pr.merged:
            return pr.labels

    print(f"No merged PR found for latest commit.")
    return None


def big_bump(version_tag):
    split = version_tag.replace('v', '').split('.')
    split[0] = str(int(split[0]) + 1)
    return 'v' + '.'.join(split)


def small_bump(version_tag):
    split = version_tag.replace('v', '').split('.')
    split[1] = str(int(split[1]) + 1)
    return 'v' + '.'.join(split)


def bump(repo, version_tag):
    labels = get_pull_request_labels(repo)

    if labels:
        for label in labels:
            if label.name == 'major':
                return big_bump(version_tag)

    return small_bump(version_tag)


def get_current_tag(repo):
    tags = repo.get_tags()
    for tag in tags:
        if '-' not in tag.name:
            return tag.name
    return 'v1.0'


def tag_latest_commit(repo, tag):
    default_branch = repo.get_branch(repo.default_branch)
    ref_str = 'refs/tags/' + tag
    ref = repo.create_git_ref(ref_str, default_branch.commit.sha)
    return ref.ref


def create_artifact(version):
    file_name = ".version"
    if os.path.exists(file_name):
        os.remove(file_name)
    file = open(file_name, "w")
    file.write(version)
    file.close()


def main():
    env_list = ["GITHUB_REPOSITORY", "GH_ACCESS_TOKEN"]
    [verify_env(e) for e in env_list]

    access_token = os.environ['GH_ACCESS_TOKEN']
    repo_path = os.environ["GITHUB_REPOSITORY"]

    g = Github(access_token)
    repo = g.get_repo(repo_path)

    current = get_current_tag(repo)
    print('Current:', current)

    new_version = bump(repo, current)
    tag_latest_commit(repo, new_version)
    print('New:', new_version)

    create_artifact(new_version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
