from __future__ import annotations

import time

import httpx
import jwt


class GitHubAPIError(RuntimeError):
    pass


class GitHubAppClient:
    def __init__(self, *, app_id: str, private_key: str, base_url: str = "https://api.github.com"):
        self._app_id = app_id
        self._private_key = private_key
        self._base_url = base_url.rstrip("/")

    def app_jwt(self, now: int | None = None) -> str:
        issued = now or int(time.time())
        return jwt.encode({"iat": issued - 60, "exp": issued + 540, "iss": self._app_id}, self._private_key, algorithm="RS256")

    def installation_token(self, installation_id: int) -> str:
        response = self._request(
            "POST", f"/app/installations/{installation_id}/access_tokens",
            token=self.app_jwt(), expected=201,
        )
        token = response.get("token")
        if not isinstance(token, str) or not token:
            raise GitHubAPIError("GitHub did not return an installation token")
        return token

    def pull_request_files(self, *, installation_id: int, repository_id: int, number: int) -> list[dict]:
        token = self.installation_token(installation_id)
        repository = self._request("GET", f"/repositories/{repository_id}", token=token)
        full_name = repository.get("full_name")
        if not isinstance(full_name, str) or "/" not in full_name:
            raise GitHubAPIError("GitHub returned invalid repository metadata")
        files: list[dict] = []
        for page in range(1, 11):
            batch = self._request("GET", f"/repos/{full_name}/pulls/{number}/files?per_page=100&page={page}", token=token)
            if not isinstance(batch, list):
                raise GitHubAPIError("GitHub returned an invalid pull-request file list")
            files.extend(batch)
            if len(batch) < 100:
                return files
        raise GitHubAPIError("pull request exceeds the 1,000-file limit")

    def _request(self, method: str, path: str, *, token: str, expected: int = 200):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Cocokerel-Shield/0.1",
        }
        try:
            response = httpx.request(method, self._base_url + path, headers=headers, timeout=15, follow_redirects=False)
        except httpx.HTTPError as error:
            raise GitHubAPIError("GitHub API could not be reached") from error
        if response.status_code != expected:
            raise GitHubAPIError(f"GitHub API returned HTTP {response.status_code}")
        return response.json()
