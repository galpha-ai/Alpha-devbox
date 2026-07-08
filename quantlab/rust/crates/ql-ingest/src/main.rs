//! CLI: normalize raw feed files to JSONL on stdout.
//!
//! Usage:
//!   ql-ingest regsho < CNMSshvol20260706.txt > regsho.jsonl
//!   ql-ingest cboe-chain < MU.json > chain.jsonl
//!
//! The Python layer (`quantlab.pipelines`) shells out to this binary when
//! built, and falls back to its own parsers otherwise; both must agree on
//! the golden fixtures.

use std::io::Read;

fn main() {
    let mode = std::env::args().nth(1).unwrap_or_default();
    let mut input = String::new();
    std::io::stdin()
        .read_to_string(&mut input)
        .expect("read stdin");

    let result: Result<Vec<serde_json::Value>, _> = match mode.as_str() {
        "regsho" => ql_ingest::regsho::parse(&input)
            .map(|v| v.iter().map(|r| serde_json::to_value(r).unwrap()).collect()),
        "cboe-chain" => ql_ingest::cboe::normalize(&input)
            .map(|v| v.iter().map(|r| serde_json::to_value(r).unwrap()).collect()),
        _ => {
            eprintln!("usage: ql-ingest <regsho|cboe-chain> < input > output.jsonl");
            std::process::exit(2);
        }
    };

    match result {
        Ok(records) => {
            let mut out = String::new();
            for r in records {
                out.push_str(&r.to_string());
                out.push('\n');
            }
            print!("{out}");
        }
        Err(e) => {
            eprintln!("parse error: {e}");
            std::process::exit(1);
        }
    }
}
