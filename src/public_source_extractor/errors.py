from __future__ import annotations


class ExtractorError(Exception):
    code = "extractor_error"
    exit_code = 1
    retryable = False
    public_message = "Extraction failed."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.public_message)

    def envelope(self) -> dict[str, object]:
        return {
            "schema_version": "0.1",
            "ok": False,
            "error": {
                "code": self.code,
                "message": self.public_message,
                "retryable": self.retryable,
            },
        }


class InputRejected(ExtractorError):
    code = "input_rejected"
    exit_code = 2
    public_message = "The URL was rejected by the public-source safety policy."


class ProviderFailure(ExtractorError):
    code = "provider_failure"
    exit_code = 3
    retryable = True
    public_message = "The extraction provider is unavailable or rejected the request."


class ProviderRateLimited(ProviderFailure):
    code = "provider_rate_limited"
    public_message = "The experimental provider rate limit was exceeded."


class ProviderTimeout(ProviderFailure):
    code = "provider_timeout"
    public_message = "The extraction provider timed out."


class InvalidProviderResponse(ExtractorError):
    code = "invalid_provider_response"
    exit_code = 4
    public_message = "The extraction provider returned an invalid or unsafe response."


class OutputFailure(ExtractorError):
    code = "output_failure"
    exit_code = 5
    public_message = "The output file could not be written safely."

