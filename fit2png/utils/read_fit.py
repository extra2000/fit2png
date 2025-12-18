from typing import Any
from garmin_fit_sdk import Decoder, Stream

def read_fit(filename: str) -> dict[Any, Any]:
    stream = Stream.from_file(filename)
    decoder = Decoder(stream)

    data, errors = decoder.read()

    if len(errors) > 0:
        raise Exception(errors)

    return data
