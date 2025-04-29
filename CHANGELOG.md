# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.1.2](https://github.com/casheiro/synapstor/compare/v1.1.1...v1.1.2) (2025-04-29)


### Bug Fixes

* Remove unnecessary whitespace in the release.yaml workflow file to ensure proper formatting and maintain consistency. ([ef66299](https://github.com/casheiro/synapstor/commit/ef662997fe6c8a51ce323420a6fe0b35a6ee289b))
* Updates the token variable names in the release.yaml file to use TEST_PYPI_API_TOKEN and PYPI_API_TOKEN, ensuring correct verification and use of authentication tokens. ([92a111e](https://github.com/casheiro/synapstor/commit/92a111e1a98a970fc4ad049419135d6a4149730f))

### [1.1.1](https://github.com/casheiro/synapstor/compare/v1.1.0...v1.1.1) (2025-04-29)

## 1.1.0 (2025-04-29)


### Features

* Adds CODEOWNERS file to set repository owner as [@netomantonio](https://github.com/netomantonio), improving review and responsibilities management. ([4455024](https://github.com/casheiro/synapstor/commit/44550248e34385d3da019c099e79a81c82267b7a))


### Bug Fixes

* Adds environment variables for PyPI and TestPyPI tokens in the main-push.yaml, pr-main.yaml, and pypi-publish.yaml workflows, improving publishing configuration in GitHub Actions. ([cd1d56f](https://github.com/casheiro/synapstor/commit/cd1d56f3fd9934f415725b35c72116d489f1c415))
* Adds global permissions to the pr-main.yaml workflow, allowing writing to content, pull requests, and ID tokens. Adjusts the execution condition of the publish job to ensure it only occurs if changes are detected in the preview. ([f041098](https://github.com/casheiro/synapstor/commit/f0410982dc0f03dd535253a767ec4fb7c984b747))
* Adds new .releaserc.json file for configuring commit types and removes the commitizen-release.yaml workflow. Introduces the generate-release.yaml workflow for generating standard releases and adjusts the post-merge-release.yaml workflow to use the new workflow. Updates the pr-main.yaml workflow to integrate the new version preview and PyPI publishing logic. ([9a4a932](https://github.com/casheiro/synapstor/commit/9a4a932ca2250c345d2bd8b9c664899849640e60))
* Adds new 'tag-and-release' job to pr-main.yaml workflow to automatically generate tags and releases on pull requests with the 'ready-for-release' label. Includes commit validation, next version calculation, and release creation on GitHub. Adjusts pr-tag-release.yaml workflow to ensure formatting compliance. ([1881a12](https://github.com/casheiro/synapstor/commit/1881a12e72a1e0bb45c27da841a841c55d9e6b8a))
* Adds new line to the end of .releaserc.json, pre-commit.yaml, and test.yaml files to ensure compliance with formatting best practices. ([48b7ebc](https://github.com/casheiro/synapstor/commit/48b7ebc826fd6e0e66cb4c3cceb743df03497ba3))
* Adds new line to the end of the CODEOWNERS file to ensure compliance with formatting best practices. ([31d413a](https://github.com/casheiro/synapstor/commit/31d413a5939be93e51b563c6f0e10e601d07e399))
* Adds new line to the end of the post-merge-release.yaml and pr-release.yaml workflow files to ensure compliance with formatting best practices. ([498cee3](https://github.com/casheiro/synapstor/commit/498cee39a226fcfa2386e91a14164fff7a468885))
* Adds new workflows for generating releases on GitHub after merges and pull requests, including commit validation, version preview, and publishing to PyPI. Improves version verification and changelog generation logic. ([191d9c4](https://github.com/casheiro/synapstor/commit/191d9c431e41630e2921b4cdd3201c5d344ffa02))
* Adds write permissions for pull-requests and read permissions for contents in the pr-release.yaml workflow, improving the GitHub Actions configuration. ([36a985c](https://github.com/casheiro/synapstor/commit/36a985cea98708b4f3e1bb44daa2d0847048211d))
* Adjusts the execution condition of the publishing job in the main-push.yaml workflow and improves the permissions configuration. Updates the commitizen-release.yaml file to ensure the presence of a newline at the end of the file. In pypi-publish.yaml, maintains the upload logic to PyPI. ([1e4dafa](https://github.com/casheiro/synapstor/commit/1e4dafadb9e3a1f144f5d0700b5a6b0bac241016))
* Adjusts the publishing job execution condition in the pr-main.yaml workflow to ensure that publishing only occurs when a new version is available, improving publishing logic. ([b39d59a](https://github.com/casheiro/synapstor/commit/b39d59ab04726e0be3301c886bef6177dd166fab))
* Fixes the publishing job execution logic in the pypi-publish.yaml workflow, ensuring that the package upload check occurs correctly after the publishing attempt. ([d10da15](https://github.com/casheiro/synapstor/commit/d10da15ad0e69b88c49f6f3077e991956f7d51d2))
* Fixes write permissions for id-token and read permissions for contents in the pr-main.yaml workflow, improving GitHub Actions configuration. ([7460b35](https://github.com/casheiro/synapstor/commit/7460b353c025cfea907b1d6d742344de128b736a))
* Improves commit validation in the commitzen-release.yaml workflow by adjusting the logic for verifying commits in pull requests and simplifying the verification of the latest commit. ([da4f666](https://github.com/casheiro/synapstor/commit/da4f666e9a61da45951be737221d1fa16a8db815))
* Remove obsolete files and update dependencies in pyproject.toml for improved package management. Introduce new release workflow for automated versioning and publishing to PyPI. ([8ade650](https://github.com/casheiro/synapstor/commit/8ade6509b27494beb7232cc82ef3c4742cbf3af1))
* Remove unnecessary whitespace in the release.yaml workflow file, ensuring compliance with formatting best practices. ([9bd6037](https://github.com/casheiro/synapstor/commit/9bd603711810f5ee1ef919ab768cee0100c09022))
* Removes automatic release creation in the post-merge-release.yaml workflow and adjusts changelog generation in the pr-release.yaml and pr-tag-release.yaml workflows to include the --yes option, improving versioning logic and workflow file formatting. ([20931e8](https://github.com/casheiro/synapstor/commit/20931e8a35259412baf1555ff252d9050efaf2c0))
* Removes unnecessary blank lines in GitHub Actions workflow files, ensuring compliance with formatting best practices. ([b031852](https://github.com/casheiro/synapstor/commit/b0318527a263601da6969f27b91a98145297c06b))
* Removes unnecessary whitespace in GitHub workflow files, ensuring compliance with formatting best practices. ([4906fae](https://github.com/casheiro/synapstor/commit/4906faebc53bd1de3def504d15fb1b2916cc23e2))
* Updates GitHub Actions workflows for publishing and releasing. Modifies the commitizen-release.yaml file to improve commit validation and add release creation on GitHub. In the pypi-publish.yaml file, changes the input structure and adds logic for conditional publishing to TestPyPI or PyPI, and includes required permissions. ([1d3c376](https://github.com/casheiro/synapstor/commit/1d3c376b505beefc3ea7eadd85d7bd53a2ca50b9))
* Updates the version of the artifact upload action in the pr-main.yaml workflow from v3 to v4.6.2, ensuring compatibility with the latest improvements and fixes. ([5f5d779](https://github.com/casheiro/synapstor/commit/5f5d779ef1f1eea5ba5cbfd52f58086d892b6847))
