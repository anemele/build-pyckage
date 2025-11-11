use std::{
    fs,
    path::{Path, PathBuf},
};

use phf::phf_map;

// Websites that host Python releases
const FTP_MIRRORS: [&str; 2] = [
    "https://mirrors.huaweicloud.com/python/",
    "https://www.python.org/ftp/python/",
    // aliyun mirror has different website structure, do not use it.
    // "https://mirrors.aliyun.com/python-release/windows/",
];

// latest releases that with binary builds
// See: https://devguide.python.org/versions/
static LATEST_RELEASES_MAP: phf::Map<&'static str, &'static str> = phf_map!(
    "3.8"=>  "3.8.10",  // https://peps.python.org/pep-0569/
    "3.9"=>  "3.9.13",  // https://peps.python.org/pep-0596/
    "3.10"=> "3.10.11", // https://peps.python.org/pep-0619/
    "3.11"=> "3.11.9",  // https://peps.python.org/pep-0664/
    "3.12"=> "3.12.10", // https://peps.python.org/pep-0693/
    "3.13"=> "3.13.5",  // https://peps.python.org/pep-0719/
);

pub fn download_python_embed(pyver: &str, embed_dir: &Path) -> anyhow::Result<PathBuf> {
    let Some(ver) = LATEST_RELEASES_MAP.get(pyver) else {
        anyhow::bail!("invalid Python version")
    };

    for mirror in FTP_MIRRORS {
        let name = format!("python-{ver}-embed-amd64.zip");
        let url = format!("{mirror}{ver}/{name}");
        let resp = tinyget::get(url)
        .with_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0")
        .send()?;
        if resp.status_code == 200 {
            let embed_python_path = embed_dir.join(name);
            fs::write(&embed_python_path, resp.as_bytes())?;
            return Ok(embed_python_path);
        }
    }

    // 如果下载失败，打印一些建议
    println!("Download python-embed from the following mirrors");
    for mirror in FTP_MIRRORS {
        println!("- {mirror}");
    }
    println!("  and move it to {}", embed_dir.display());

    anyhow::bail!("failed to download python embed");
}
