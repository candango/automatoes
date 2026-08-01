//! Rust implementation of the Automatoes ACME V2 client.

pub fn hello() -> &'static str {
    "Hello from automatoes!"
}

pub mod error;
pub mod nonce;

pub use error::AcmeError;
pub use nonce::new_nonce;
