class ResponseAdapter:
    def __init__(self, response, provider):
        self.provider = provider

        adapter_methods = {
            "openrouter": self._adapt_openrouter_response,
            "ollama": self._adapt_ollama_response
        }

        adapter_method = adapter_methods.get(provider)

        if adapter_method:
            adapter_method(response)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _adapt_openrouter_response(self, response):
        self.id = response.get("id")
        self.model = response.get("model")
        self.timestamp = response.get("created")
        self.message = response["choices"][0]["message"]["content"] if response.get("choices") else None
        self.usage = {
            "prompt_tokens": response["usage"]["prompt_tokens"],
            "completion_tokens": response["usage"]["completion_tokens"],
            "total_tokens": response["usage"]["total_tokens"],
        }
        self.completed = True

    def _adapt_ollama_response(self, response):
        self.id = None
        self.model = response.get("model")
        self.timestamp = response.get("created_at")
        self.message = response.get("message", {}).get("content")
        self.usage = None
        self.completed = response.get("done", False)

    def to_dict(self):
        """Return the response as a dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "timestamp": self.timestamp,
            "completed": self.completed,
            "message": self.message,
            "usage": self.usage,
        }
