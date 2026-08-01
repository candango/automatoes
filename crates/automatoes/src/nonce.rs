use reqwest::{blocking::Client, Certificate};

use crate::error::AcmeError;

pub fn new_nonce(endpoint: &str, verify: Option<&str>) -> Result<String, AcmeError> {
    let mut builder = Client::builder();

    if let Some(certificate_path) = verify {
        let pem = std::fs::read(certificate_path)?;
        let certificate = Certificate::from_pem(&pem)?;
        builder = builder.add_root_certificate(certificate);
    }

    let client = builder.build()?;

    let response = client
        .head(endpoint)
        .header("resource", "new-reg")
        .header("payload", "")
        .send()?;

    if !response.status().is_success() {
        return Err(AcmeError::HttpStatus(response.status()));
    }

    let nonce = response
        .headers()
        .get("Replay-Nonce")
        .ok_or(AcmeError::MissingReplayNonce)?
        .to_str()?;

    Ok(nonce.to_owned())
}
