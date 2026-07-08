//! CBOE delayed option-chain JSON normalizer.
//!
//! Input: `https://cdn.cboe.com/api/global/delayed_quotes/options/{TICKER}.json`
//! Shape: `{"symbol": "MU", "timestamp": "...", "data": {"close": 123.4,
//! "options": [{"option": "MU260918C00130000", "bid": ..., "ask": ...,
//! "iv": ..., "open_interest": ..., "volume": ..., "delta": ...,
//! "gamma": ...}, ...]}}`
//!
//! The contract symbol is OCC format: ROOT + YYMMDD + C|P + strike*1000
//! zero-padded to 8 digits. Point-in-time caveat handled downstream: the
//! `open_interest` in a snapshot is as of the *prior* session's settlement.

use crate::ParseError;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
struct RawChain {
    symbol: String,
    timestamp: Option<String>,
    data: RawData,
}

#[derive(Debug, Deserialize)]
struct RawData {
    close: Option<f64>,
    options: Vec<RawOption>,
}

#[derive(Debug, Deserialize)]
struct RawOption {
    option: String,
    bid: Option<f64>,
    ask: Option<f64>,
    iv: Option<f64>,
    open_interest: Option<f64>,
    volume: Option<f64>,
    delta: Option<f64>,
    gamma: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct ChainRecord {
    pub underlying: String,
    /// Underlying close in the snapshot, if present.
    pub underlying_close: Option<f64>,
    /// Snapshot timestamp string as provided by CBOE (exchange-local).
    pub snapshot_ts: Option<String>,
    pub contract: String,
    /// Expiry as YYYY-MM-DD (from the OCC symbol; 20xx assumed).
    pub expiry: String,
    /// "C" or "P".
    pub right: String,
    pub strike: f64,
    pub bid: Option<f64>,
    pub ask: Option<f64>,
    pub mid: Option<f64>,
    pub iv: Option<f64>,
    /// As of the prior session's settlement (CBOE updates OI each morning).
    pub open_interest: Option<f64>,
    pub volume: Option<f64>,
    pub delta: Option<f64>,
    pub gamma: Option<f64>,
}

/// Split an OCC contract symbol into (root, expiry, right, strike).
pub fn parse_occ_symbol(sym: &str) -> Option<(String, String, String, f64)> {
    // Last 8 chars: strike * 1000; preceding char: C/P; preceding 6: YYMMDD.
    if sym.len() < 16 {
        return None;
    }
    let (head, strike_part) = sym.split_at(sym.len() - 8);
    let (head, right) = head.split_at(head.len() - 1);
    let (root, date) = head.split_at(head.len() - 6);
    if !matches!(right, "C" | "P") || root.is_empty() {
        return None;
    }
    if !date.chars().all(|c| c.is_ascii_digit())
        || !strike_part.chars().all(|c| c.is_ascii_digit())
    {
        return None;
    }
    let strike: f64 = strike_part.parse::<u64>().ok()? as f64 / 1000.0;
    let expiry = format!("20{}-{}-{}", &date[..2], &date[2..4], &date[4..6]);
    Some((root.to_string(), expiry, right.to_string(), strike))
}

/// Normalize a full CBOE chain JSON document into flat records.
/// Contracts whose symbols fail OCC parsing are returned as errors rather
/// than silently dropped — a silent drop biases OI aggregates.
pub fn normalize(json_text: &str) -> Result<Vec<ChainRecord>, ParseError> {
    let raw: RawChain = serde_json::from_str(json_text).map_err(|e| ParseError {
        line: 0,
        message: format!("chain JSON: {e}"),
    })?;
    let mut out = Vec::with_capacity(raw.data.options.len());
    for (i, o) in raw.data.options.iter().enumerate() {
        let (_root, expiry, right, strike) =
            parse_occ_symbol(&o.option).ok_or_else(|| ParseError {
                line: i + 1,
                message: format!("bad OCC symbol {:?}", o.option),
            })?;
        let mid = match (o.bid, o.ask) {
            (Some(b), Some(a)) if a > 0.0 && a >= b => Some((a + b) / 2.0),
            _ => None,
        };
        out.push(ChainRecord {
            underlying: raw.symbol.clone(),
            underlying_close: raw.data.close,
            snapshot_ts: raw.timestamp.clone(),
            contract: o.option.clone(),
            expiry,
            right,
            strike,
            bid: o.bid,
            ask: o.ask,
            mid,
            iv: o.iv,
            open_interest: o.open_interest,
            volume: o.volume,
            delta: o.delta,
            gamma: o.gamma,
        });
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = r#"{
      "symbol": "MU",
      "timestamp": "2026-07-08 16:15:00",
      "data": {
        "close": 128.5,
        "options": [
          {"option": "MU260918C00130000", "bid": 7.10, "ask": 7.30,
           "iv": 0.42, "open_interest": 15230, "volume": 3120,
           "delta": 0.48, "gamma": 0.021},
          {"option": "MU260918P00110000", "bid": 3.00, "ask": 3.20,
           "iv": 0.45, "open_interest": 9800, "volume": 800,
           "delta": -0.25, "gamma": 0.015}
        ]
      }
    }"#;

    #[test]
    fn occ_symbol_roundtrip() {
        let (root, expiry, right, strike) = parse_occ_symbol("MU260918C00130000").unwrap();
        assert_eq!((root.as_str(), expiry.as_str(), right.as_str(), strike),
                   ("MU", "2026-09-18", "C", 130.0));
        // Fractional strike and multi-char root.
        let (root, _, _, strike) = parse_occ_symbol("BRKB261218P00450500").unwrap();
        assert_eq!((root.as_str(), strike), ("BRKB", 450.5));
        assert!(parse_occ_symbol("GARBAGE").is_none());
    }

    #[test]
    fn normalizes_chain_with_mid() {
        let recs = normalize(SAMPLE).unwrap();
        assert_eq!(recs.len(), 2);
        assert_eq!(recs[0].underlying, "MU");
        assert_eq!(recs[0].expiry, "2026-09-18");
        assert!((recs[0].mid.unwrap() - 7.20).abs() < 1e-9);
        assert_eq!(recs[1].right, "P");
        assert_eq!(recs[1].strike, 110.0);
    }

    #[test]
    fn bad_symbol_is_an_error_not_a_drop() {
        let bad = SAMPLE.replace("MU260918P00110000", "NOT_AN_OCC");
        let err = normalize(&bad).unwrap_err();
        assert!(err.message.contains("bad OCC symbol"));
    }
}
