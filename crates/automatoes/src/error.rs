use thiserror::Error;

#[derive(Debug, Error)]
pub enum AcmeError {
    #[error("nonce request failed: {0}")]
    Request(#[from] reqwest::Error),

    #[error("failed to read CA certificate: {0}")]
    CertificateFile(#[from] std::io::Error),

    #[error("nonce endpoint returned HTTP status {0}")]
    HttpStatus(reqwest::StatusCode),

    #[error("response missing Replay-Nonce header")]
    MissingReplayNonce,

    #[error("invalid Replay-Nonce header: {0}")]
    InvalidReplayNonce(#[from] reqwest::header::ToStrError),
}
