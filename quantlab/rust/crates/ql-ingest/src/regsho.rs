//! FINRA Reg SHO daily short sale volume files.
//!
//! Format (pipe-delimited, header + trailer lines vary by file):
//! `Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market`
//! e.g. `20260706|MU|1234567|1234|2345678|B,Q,N`
//!
//! Level caveat (see the inv-short-interest skill): short volume includes
//! market-maker liquidity provision; downstream consumers use changes and
//! z-scores, never raw levels. This module only parses; it adds
//! `short_volume_ratio` because it is basis-free.

use crate::ParseError;
use serde::Serialize;

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct RegShoRecord {
    /// Trade date as YYYY-MM-DD.
    pub date: String,
    pub symbol: String,
    pub short_volume: u64,
    pub short_exempt_volume: u64,
    pub total_volume: u64,
    /// Reporting facilities, e.g. "B,Q,N".
    pub markets: String,
    /// short_volume / total_volume; None when total_volume == 0 (halt days).
    pub short_volume_ratio: Option<f64>,
}

/// Parse a full Reg SHO daily file. Skips the header line and any
/// non-record trailer (FINRA files end with a record-count line).
pub fn parse(input: &str) -> Result<Vec<RegShoRecord>, ParseError> {
    let mut out = Vec::new();
    for (idx, line) in input.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with("Date|") {
            continue;
        }
        let fields: Vec<&str> = line.split('|').collect();
        if fields.len() < 6 {
            // Trailer lines (e.g. a bare record count) are tolerated only
            // if they carry no pipes; anything else is a malformed record.
            if fields.len() == 1 && fields[0].chars().all(|c| c.is_ascii_digit()) {
                continue;
            }
            return Err(ParseError {
                line: idx + 1,
                message: format!("expected 6 pipe-delimited fields, got {}", fields.len()),
            });
        }
        let num = |i: usize| -> Result<u64, ParseError> {
            fields[i].parse().map_err(|_| ParseError {
                line: idx + 1,
                message: format!("field {} not an integer: {:?}", i, fields[i]),
            })
        };
        let raw_date = fields[0];
        if raw_date.len() != 8 || !raw_date.chars().all(|c| c.is_ascii_digit()) {
            return Err(ParseError {
                line: idx + 1,
                message: format!("bad date {:?}", raw_date),
            });
        }
        let short_volume = num(2)?;
        let total_volume = num(4)?;
        out.push(RegShoRecord {
            date: format!("{}-{}-{}", &raw_date[..4], &raw_date[4..6], &raw_date[6..8]),
            symbol: fields[1].to_string(),
            short_volume,
            short_exempt_volume: num(3)?,
            total_volume,
            markets: fields[5].to_string(),
            short_volume_ratio: (total_volume > 0)
                .then(|| short_volume as f64 / total_volume as f64),
        });
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "\
Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market
20260706|MU|1500000|1200|3000000|B,Q,N
20260706|SNDK|400000|0|1000000|B,Q
20260706|HALTED|0|0|0|B
2
";

    #[test]
    fn parses_records_and_skips_header_trailer() {
        let recs = parse(SAMPLE).unwrap();
        assert_eq!(recs.len(), 3);
        assert_eq!(recs[0].date, "2026-07-06");
        assert_eq!(recs[0].symbol, "MU");
        assert_eq!(recs[0].short_volume_ratio, Some(0.5));
        assert_eq!(recs[1].short_volume_ratio, Some(0.4));
    }

    #[test]
    fn zero_total_volume_yields_none_ratio() {
        let recs = parse(SAMPLE).unwrap();
        assert_eq!(recs[2].symbol, "HALTED");
        assert_eq!(recs[2].short_volume_ratio, None);
    }

    #[test]
    fn malformed_line_reports_line_number() {
        let err = parse("20260706|MU|oops|0|10|B,Q,N\n").unwrap_err();
        assert_eq!(err.line, 1);
        assert!(err.message.contains("not an integer"));
    }
}
