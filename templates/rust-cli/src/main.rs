use anyhow::Result;
use clap::Parser;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    println!("Hello, {}!", cli.name);
    Ok(())
}

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[arg(short, long, default_value = "World")]
    name: String,
}
