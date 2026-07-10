class LLMServiceError(Exception):
    """大模型服务不可用或返回无效结果。"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
