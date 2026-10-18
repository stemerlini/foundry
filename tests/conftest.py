import pytest

from foundry import project as project_mod


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Keep config and run store inside the test's temp dir."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setattr(project_mod, "DEFAULT_STORE", tmp_path / "store")
    for var in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(var, "Test")
    for var in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(var, "test@example.com")


@pytest.fixture
def make(tmp_path):
    def make(template="particle-telescope", name="p"):
        p = project_mod.create(tmp_path / name, template)
        manifest = p.root / "foundry.toml"
        manifest.write_text(manifest.read_text() + f'\n[store]\nroot = "{tmp_path / "store"}"\n')
        return project_mod.Project.load(p.root)

    return make
