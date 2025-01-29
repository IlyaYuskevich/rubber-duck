import typing as t
from haystack import component
from haystack import component, logging
from haystack.dataclasses import ByteStream
from pathlib import Path
from project_paths import BLOB_STORAGE

@component
class FileContentReader():

    @component.output_types(streams=t.List[ByteStream])
    def run(self, directories: t.Optional[t.List[str]]):
        """Reads content of all files in the blob storage and additional directories."""
        streams: t.List[ByteStream] = []
        if not directories:
            directories = []
        directories.append(str(BLOB_STORAGE))
        for directory in directories:
            for filepath in Path(directory).rglob('*'):
                try:
                    if filepath.is_file():
                        stream = ByteStream.from_file_path(filepath)
                        stream.meta["path"] = str(filepath)
                        match filepath.suffix:
                            case ".html":
                                stream.mime_type = "text/html"
                            case ".pdf":
                                stream.mime_type = "application/pdf"
                            case _:
                                stream.mime_type = "text/plain"
                        streams.append(stream)
                except PermissionError:
                    print(f"Not enough permissions to read file: {str(filepath)}")

        return {
            "streams": streams,
        }