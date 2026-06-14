class CLVPipelineError(Exception):
    """Base domain error for all customer lifetime value processing tasks."""
    pass

class DataLakeExtractionError(CLVPipelineError):
    """Raised when ingestion payloads or database variables are corrupted or missing."""
    pass

class ModelFittingInversionError(CLVPipelineError):
    """Raised when mathematical optimization matrix criteria fail boundaries."""
    pass