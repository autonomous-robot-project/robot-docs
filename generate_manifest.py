import subprocess
from pathlib import Path


def get_git_last_modification(file_path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def extract_markdown_title(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                # Remove leading '#' e espaços
                return line.lstrip("#").strip()
    return None


def generate_manifest(folder_path):
    folder = Path(folder_path)
    manifest_path = folder / "MANIFEST.md"

    # Cabeçalho
    manifest = f"# MANIFEST - {folder.name}\n\n"
    # Última modificação geral (pode ser o último commit dos arquivos)
    all_files = list(folder.rglob("*.md"))
    last_mods = [
        get_git_last_modification(f) for f in all_files if get_git_last_modification(f)
    ]
    last_mod = max(last_mods) if last_mods else None
    manifest += f"## Last modification: {last_mod or 'Unknown'}\n\n"

    # Listar arquivos por subpasta
    for subfolder_name in ["docs", "tasks", "reflections"]:
        subfolder = folder / subfolder_name
        if not subfolder.exists():
            continue
        manifest += f"### {subfolder_name.capitalize()}:\n"
        md_files = list(subfolder.glob("*.md"))
        if not md_files:
            manifest += "- (empty)\n"
            continue
        for md_file in md_files:
            title = extract_markdown_title(md_file) or "(No title)"
            last_mod_file = get_git_last_modification(md_file) or "Unknown"
            manifest += f"- {md_file.name}: {title} (Last mod: {last_mod_file})\n"
        manifest += "\n"

    # Pendências - você pode customizar isso para detectar arquivos específicos ou textos
    manifest += "### Pendencies:\n- [ ] Add performance analysis\n- [ ] Update sensor calibration\n"

    # Gravar arquivo
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)

    print(f"MANIFEST.md generated at {manifest_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_manifest.py path/to/system-folder")
    else:
        generate_manifest(sys.argv[1])
