use std::{env, path::Path};

mod local;
mod web;

fn main() -> anyhow::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        anyhow::bail!("requires <pyckage>.zip");
    }

    local::load_pyckage(Path::new(&args[1]))?;

    Ok(())
}
