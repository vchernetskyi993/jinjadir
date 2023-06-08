use assert_cmd::Command;
use predicates::prelude::*;

#[tokio::test]
async fn it_works() {
    Command::cargo_bin(env!("CARGO_PKG_NAME"))
        .unwrap()
        .arg("--name")
        .arg("John")
        .assert()
        .success()
        .stdout(predicate::eq("Hello, John!\n"));
}
