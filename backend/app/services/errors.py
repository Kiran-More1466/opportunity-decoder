class AnalysisError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AnalysisTimeoutError(AnalysisError):
    def __init__(self):
        super().__init__("The AI analysis timed out. Please try again.", status_code=504)


class ProviderQuotaError(AnalysisError):
    def __init__(self):
        super().__init__("The AI service quota is temporarily unavailable. Please try again later.", status_code=503)


class ProviderUnavailableError(AnalysisError):
    def __init__(self, message: str = "The AI service is temporarily unavailable. Please try again later."):
        super().__init__(message, status_code=502)
