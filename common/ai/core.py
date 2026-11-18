import json

from django.conf import settings
from openai import APIError, APIStatusError, OpenAI

from vas3k_blog.exceptions import AIError


def ask_llm_structured(
    instructions,
    text,
    schema,
    model=None,
    *,
    schema_name="result",
    timeout=None,
    max_output_tokens=None,
    reasoning_effort=None,
):
    if not settings.OPENAI_API_KEY:
        raise AIError("Set OPENAI_API_KEY before using AI.")

    options = {}

    if reasoning_effort is not None:
        options["reasoning"] = {"effort": reasoning_effort}

    try:
        with OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=timeout if timeout is not None else settings.OPENAI_TIMEOUT,
            max_retries=0,
        ) as client:
            response = client.responses.create(
                model=model or settings.OPENAI_MODEL,
                input=text,
                instructions=instructions,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    },
                },
                max_output_tokens=(
                    max_output_tokens if max_output_tokens is not None
                    else settings.OPENAI_MAX_OUTPUT_TOKENS
                ),
                store=False,
                **options,
            )
    except APIStatusError as exc:
        raise AIError(
            f"OpenAI returned HTTP {exc.status_code}. Check model access, credentials and quota."
        ) from exc
    except APIError as exc:
        raise AIError("OpenAI request failed or timed out.") from exc

    if response.status != "completed" or response.error:
        raise AIError("OpenAI did not complete the response. No partial result was returned.")

    for item in response.output:
        if item.type == "message" and any(content.type == "refusal" for content in item.content):
            raise AIError("OpenAI declined the request.")

    try:
        result = json.loads(response.output_text)
    except (ValueError, TypeError) as exc:
        raise AIError("OpenAI returned invalid JSON output.") from exc

    if not isinstance(result, dict):
        raise AIError("OpenAI returned no structured object.")

    return result
