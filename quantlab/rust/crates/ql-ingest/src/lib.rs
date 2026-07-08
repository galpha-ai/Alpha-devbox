//! Parsers/normalizers for raw market-data feeds.
//!
//! Contract shared with the Python layer (`quantlab.pipelines`): both
//! implementations must produce identical normalized records on the golden
//! fixtures under `tests/fixtures/` — the cross-language fixture test is the
//! acceptance check for parser correctness.

pub mod cboe;
pub mod regsho;

/// A parse failure with enough context to find the offending input.
#[derive(Debug, Clone, PartialEq)]
pub struct ParseError {
    pub line: usize,
    pub message: String,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "line {}: {}", self.line, self.message)
    }
}

impl std::error::Error for ParseError {}
