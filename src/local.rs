use crate::web::download_python_embed;
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};
use zip::read::ZipArchive;

const _EMBED_PATH: &str = "_embed";

fn parse_python_version(pkg_name: &str) -> anyhow::Result<String> {
    let re = Regex::new(r"pyckage-py(\d\.\d+).zip$")?;
    let caps = re
        .captures(pkg_name)
        .ok_or(anyhow::anyhow!("invalid pyckage file name"))?;
    let s = caps[1].to_string();
    Ok(s)
}

#[test]
fn test_parse_python_version() {
    assert_eq!(
        parse_python_version("abc-0.1.0-pyckage-py3.12.zip").unwrap(),
        "3.12"
    )
}

fn get_file_name(path: &Path) -> Option<&str> {
    path.file_name()?.to_str()
}

fn find_python_embed(pkg_path: &Path) -> anyhow::Result<PathBuf> {
    let Some(s) = get_file_name(pkg_path) else {
        anyhow::bail!("bad file name")
    };
    let pyver = parse_python_version(s)?;
    let python_embed_pattern = format!("python-{pyver}.*-embed-amd64.zip");

    #[inline]
    fn get_glob_last(pattern: &Path) -> Option<PathBuf> {
        glob::glob(pattern.to_str()?).ok()?.last()?.ok()
    }

    // find from the same path
    let t = pkg_path.with_file_name(&python_embed_pattern);
    if let Some(p) = get_glob_last(&t) {
        return Ok(p);
    }

    // find from the _embed path
    let embed_dir = pkg_path.with_file_name(_EMBED_PATH);
    if !embed_dir.exists() {
        fs::create_dir_all(&embed_dir)?;
    }
    let t = embed_dir.join(python_embed_pattern);
    if let Some(p) = get_glob_last(&t) {
        return Ok(p);
    }

    // get from the web
    download_python_embed(&pyver, &embed_dir)
}

fn extract_zip(zip_path: &Path, output_dir: &Path) -> anyhow::Result<()> {
    let file = fs::File::open(zip_path)?;
    let mut archive = ZipArchive::new(file)?;
    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let outpath = output_dir.join(file.name());
        if file.is_dir() {
            fs::create_dir_all(&outpath)?;
        } else {
            if let Some(parent) = outpath.parent() {
                fs::create_dir_all(parent)?;
            }
            let mut outfile = fs::File::create(&outpath)?;
            std::io::copy(&mut file, &mut outfile)?;
        }
    }

    Ok(())
}

pub fn load_pyckage(pkg_path: &Path) -> anyhow::Result<()> {
    let Some(s) = get_file_name(pkg_path) else {
        anyhow::bail!("bad file name");
    };
    let Some(s) = s.strip_suffix(".zip") else {
        anyhow::bail!("invalid pyckage file name, not ends with .zip");
    };
    let dst = pkg_path.with_file_name(s);

    extract_zip(pkg_path, &dst)?;

    let embed_python = find_python_embed(pkg_path)?;
    extract_zip(&embed_python, &dst.join("bin"))?;

    Ok(())
}
