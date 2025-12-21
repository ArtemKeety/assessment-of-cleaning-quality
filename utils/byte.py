import base64


def encoding_file(file: str)-> base64.b64encode:
    with open(file, "rb") as f:
        array = []
        while chunk := f.read(1024 * 1024):
            array.append(chunk)
        string = b"".join(array)
        return base64.b64encode(string).decode('utf-8')

